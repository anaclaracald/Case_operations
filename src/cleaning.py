"""
cleaning.py — Aplicação das correções identificadas pela validation.py.

Cada função recebe o DataFrame e retorna uma cópia corrigida.
A ordem de aplicação deve seguir a sequência:
  1. remove_true_duplicates
  2. fix_numeric_formats
  3. fix_stage_typos
  4. fix_lead_office_typos
  5. fix_lead_source_typos
  6. fix_amount_from_products
  7. flag_out_of_scope
  8. flag_data_quality
"""

import pandas as pd
from src.config import (
    STAGE_TYPO_MAP,
    LEAD_OFFICE_NORM_MAP,
    LEAD_SOURCE_RAW_TO_CANONICAL,
    CANONICAL_LEAD_SOURCE,
    VALID_TYPES,
    EARLY_STAGES,
    OPP_ID_COL,
)


# Helpers
def _to_float(v):
    if pd.isna(v):
        return None
    try:
        return float(str(v).strip().replace(".", "").replace(",", "."))
    except (ValueError, TypeError):
        return None


# 1. Remove linhas 100% duplicadas
def remove_true_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates(keep="first").copy()
    after = len(df)
    return df


# 2. Corrige formatos numéricos
def fix_numeric_formats(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Amount"] = df["Amount"].apply(_to_float)
    df["Total_Product_Amount"] = df["Total_Product_Amount"].apply(_to_float)
    return df


# 3. Corrige typos em Stage
def fix_stage_typos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Corrige erros de digitação em Stage usando o dicionário STAGE_TYPO_MAP.
    A normalização é por lowercase + strip antes da comparação.
    """
    df = df.copy()

    def correct_stage(v: str) -> str:
        if pd.isna(v):
            return v
        normalized = str(v).strip().lower()
        return STAGE_TYPO_MAP.get(normalized, str(v).strip())

    df["Stage"] = df["Stage"].apply(correct_stage)
    return df


# 4. Corrige variações em Lead_Office
def fix_lead_office_typos(df: pd.DataFrame) -> pd.DataFrame:
    # Estratégia: lowercase + strip → lookup no dicionário.
    df = df.copy()

    def correct_office(v: str) -> str:
        if pd.isna(v):
            return v
        normalized = str(v).strip().lower()
        # Remove acentos comuns do português para comparação
        normalized = normalized.replace("ã", "a").replace("â", "a").replace("á", "a")
        return LEAD_OFFICE_NORM_MAP.get(normalized, str(v).strip())

    df["Lead_Office"] = df["Lead_Office"].apply(correct_office)
    return df


# 5. Corrige inconsistências em Lead_Source
def fix_lead_source_typos(df: pd.DataFrame) -> pd.DataFrame:
    """Estratégia em camadas:
      a) strip + lowercase → lookup exato no dicionário de mapeamento
      b) Se não encontrado, tenta strip + lowercase → lookup nos canônicos (case-insensitive)
      c) Se ainda não encontrado, mantém o valor original (será categorizado como Unknown)
    """
    df = df.copy()
    canonical_lower_map = {s.lower(): s for s in CANONICAL_LEAD_SOURCE}

    def correct_source(v: str) -> str:
        if pd.isna(v):
            return v
        stripped = str(v).strip()
        normalized = stripped.lower()
        # Camada 1: mapeamento direto de valores brutos
        if normalized in LEAD_SOURCE_RAW_TO_CANONICAL:
            return LEAD_SOURCE_RAW_TO_CANONICAL[normalized]
        # Camada 2: já é canônico (case-insensitive)
        if normalized in canonical_lower_map:
            return canonical_lower_map[normalized]
        # Camada 3: retorna o valor com strip aplicado (sem alteração de conteúdo)
        return stripped

    df["Lead_Source"] = df["Lead_Source"].apply(correct_source)
    return df


# 6. Recalcula Amount pela soma dos produtos
def fix_amount_from_products(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Soma TPA por deal (ignora nulos)
    tpa_sum = (
        df[df["Total_Product_Amount"].notna()]
        .groupby(OPP_ID_COL)["Total_Product_Amount"]
        .sum()
        .reset_index()
        .rename(columns={"Total_Product_Amount": "_tpa_sum"})
    )

    # Deals com TPA preenchido e fora de estágios iniciais
    valid_deals = df[
        ~df["Stage"].isin(EARLY_STAGES) & df["Total_Product_Amount"].notna()
    ][OPP_ID_COL].unique()

    # Merge para identificar divergências
    deal_amounts = (
        df[df[OPP_ID_COL].isin(valid_deals)]
        .groupby(OPP_ID_COL)["Amount"]
        .first()
        .reset_index()
        .rename(columns={"Amount": "_amount_original"})
    )

    merged = tpa_sum.merge(deal_amounts, on=OPP_ID_COL)
    # Tolerância de R$ 0,50
    divergent_ids = merged[
        abs(merged["_tpa_sum"] - merged["_amount_original"]) > 0.5
    ][OPP_ID_COL].tolist()

    if not divergent_ids:
        return df

    # Cria mapa Opportunity_ID → Amount corrigido
    correction_map = (
        tpa_sum[tpa_sum[OPP_ID_COL].isin(divergent_ids)]
        .set_index(OPP_ID_COL)["_tpa_sum"]
        .to_dict()
    )

    # Aplica correção: substitui Amount onde há divergência
    def correct_amount(row):
        if row[OPP_ID_COL] in correction_map:
            return correction_map[row[OPP_ID_COL]]
        return row["Amount"]

    df["Amount"] = df.apply(correct_amount, axis=1)
    print(f"[cleaning] Amount recalculado para {len(divergent_ids)} deals")
    return df

# 7. Marca registros fora de escopo
def flag_out_of_scope(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adiciona coluna 'in_scope' (bool).
    True apenas para os 3 Types válidos definidos em config.py.
    Registros com Type nulo também recebem in_scope=False.
    """
    df = df.copy()
    df["in_scope"] = df["Type"].isin(VALID_TYPES)
    out_count = (~df["in_scope"]).sum()
    print(f"[cleaning] Registros fora de escopo sinalizados: {out_count}")
    return df


# 8. Sinaliza registros com qualidade de dado suspeita
def flag_data_quality(df: pd.DataFrame) -> pd.DataFrame:
    # Adiciona coluna 'data_quality_flag' descrevendo problemas residuais.
    df = df.copy()
    from src.config import CANONICAL_LEAD_SOURCE

    flags = []
    for _, row in df.iterrows():
        issues = []
        stage = str(row.get("Stage", "")).strip()
        if stage not in EARLY_STAGES and pd.isna(row.get("Amount")):
            issues.append("Amount ausente em estágio avançado")
        if stage not in EARLY_STAGES and pd.isna(row.get("Product_Name")):
            issues.append("Produto ausente em estágio avançado")
        ls = str(row.get("Lead_Source", "")).strip()
        if ls and ls not in CANONICAL_LEAD_SOURCE:
            issues.append(f"Lead_Source não mapeado: {ls}")
        flags.append("; ".join(issues) if issues else "")

    df["data_quality_flag"] = flags
    return df


# Pipeline completo de limpeza
def run_cleaning_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    df = remove_true_duplicates(df)
    df = fix_numeric_formats(df)
    df = fix_stage_typos(df)
    df = fix_lead_office_typos(df)
    df = fix_lead_source_typos(df)
    df = fix_amount_from_products(df)
    df = flag_out_of_scope(df)
    df = flag_data_quality(df)
    return df
