"""
validation.py — Detecção de problemas de qualidade na planilha bruta.

Cada função retorna um dict com:
  - 'rows': DataFrame com as linhas problemáticas
  - 'count': número de linhas afetadas
  - 'description': descrição técnica do problema
  - 'business_explanation': explicação em linguagem não-técnica
  - 'correction': o que será feito para corrigir
"""

import pandas as pd
from src.config import (
    CANONICAL_LEAD_SOURCE,
    CANONICAL_LEAD_OFFICE,
    CANONICAL_STAGE,
    VALID_TYPES,
    EARLY_STAGES,
    OPP_ID_COL,
    LEAD_SOURCE_RAW_TO_CANONICAL,
)

# Normaliza string para comparação: strip, lowercase.
def _normalize_str(s: str) -> str:
    if pd.isna(s):
        return ""
    return str(s).strip().lower()


# 1. Typos em Stage
def check_stage_typos(df: pd.DataFrame) -> dict:
    canonical_lower = {s.lower() for s in CANONICAL_STAGE}
    mask = df["Stage"].apply(lambda v: _normalize_str(v) not in canonical_lower)
    affected = df[mask]
    return {
        "category": "Typos em Stage",
        "rows": affected,
        "count": len(affected),
        "description": (
            "Valores na coluna Stage que não correspondem à lista canônica: "
            + ", ".join(CANONICAL_STAGE)
        ),
        "business_explanation": (
            "O estágio do negócio estava escrito de forma errada em algumas linhas "
            "(ex: 'Closed Wonn', 'Negociation'). Isso impede filtros e dashboards de "
            "funcionar corretamente, pois o sistema não reconhece o estágio."
        ),
        "correction": (
            "Cada valor com erro foi mapeado para o seu equivalente canônico correto "
            "usando um dicionário de correções. Ex: 'Closed Wonn' → 'Closed Won'."
        ),
        "examples": affected[["Opportunity_ID", "Stage"]].drop_duplicates().head(10),
    }


# 2. Typos em Lead_Office
def check_lead_office_typos(df: pd.DataFrame) -> dict:
    canonical_lower = {s.lower() for s in CANONICAL_LEAD_OFFICE}
    mask = df["Lead_Office"].apply(lambda v: _normalize_str(v) not in canonical_lower)
    affected = df[mask]
    return {
        "category": "Typos em Lead_Office",
        "rows": affected,
        "count": len(affected),
        "description": (
            "Valores em Lead_Office fora da lista canônica: "
            + ", ".join(CANONICAL_LEAD_OFFICE)
        ),
        "business_explanation": (
            "O escritório responsável pelo negócio estava registrado de formas diferentes: "
            "'SP', 'sao paulo', 'São Paulo' — todos representam o mesmo escritório. "
            "Isso fragmenta os relatórios por escritório."
        ),
        "correction": (
            "Todos os valores foram normalizados para a forma canônica correspondente. "
            "Ex: 'SP', 'sao paulo', 'São Paulo' → 'Sao Paulo, BR'."
        ),
        "examples": affected[["Opportunity_ID", "Lead_Office"]].drop_duplicates().head(10),
    }


# 3. Typos/variações em Lead_Source
def check_lead_source_typos(df: pd.DataFrame) -> dict:
    known_keys = set(LEAD_SOURCE_RAW_TO_CANONICAL.keys())
    canonical_lower = {s.lower() for s in CANONICAL_LEAD_SOURCE}

    def is_problematic(v: str) -> bool:
        n = _normalize_str(v)
        return n not in canonical_lower and n not in known_keys

    mask = df["Lead_Source"].apply(is_problematic)
    affected = df[mask]

    # Também detecta valores com espaços extras ou inconsistências já mapeáveis
    needs_normalization = df["Lead_Source"].apply(
        lambda v: _normalize_str(v) in known_keys or str(v).strip() != str(v)
    )
    all_affected = df[needs_normalization | mask]

    return {
        "category": "Inconsistências em Lead_Source",
        "rows": all_affected,
        "count": len(all_affected),
        "description": (
            "Valores em Lead_Source com variações de grafia, espaços extras, "
            "maiúsculas/minúsculas ou separadores diferentes do canônico."
        ),
        "business_explanation": (
            "A origem do lead estava registrada de maneiras inconsistentes: "
            "espaços no início/fim, letras maiúsculas, traços ao invés de espaços. "
            "Isso faz com que a mesma fonte apareça múltiplas vezes nos relatórios."
        ),
        "correction": (
            "Cada valor foi normalizado (strip, lowercase) e mapeado para o canônico. "
            "Valores sem mapeamento direto receberam 'Unknown'."
        ),
        "examples": all_affected[["Opportunity_ID", "Lead_Source"]].drop_duplicates().head(10),
    }


# 4. Tipos fora de escopo
def check_out_of_scope_types(df: pd.DataFrame) -> dict:
    mask = ~df["Type"].isin(VALID_TYPES) & df["Type"].notna()
    affected = df[mask]
    return {
        "category": "Tipos fora de escopo",
        "rows": affected,
        "count": len(affected),
        "description": (
            f"Registros com Type fora dos valores válidos para análise: {VALID_TYPES}. "
            f"Valores encontrados: {affected['Type'].unique().tolist()}"
        ),
        "business_explanation": (
            "Existem tipos de oportunidade que não fazem parte do escopo desta análise "
            "(ex: 'Retainer', 'Passthrough', 'Flex/Renewal'). "
            "Esses registros serão marcados mas mantidos na planilha."
        ),
        "correction": (
            "Uma coluna 'in_scope' (True/False) foi adicionada. "
            "Registros fora de escopo recebem in_scope=False e são excluídos das métricas."
        ),
        "examples": affected[["Opportunity_ID", "Type"]].drop_duplicates().head(10),
    }


# 5. Type nulo
def check_null_type(df: pd.DataFrame) -> dict:
    mask = df["Type"].isna()
    affected = df[mask]
    return {
        "category": "Type ausente",
        "rows": affected,
        "count": len(affected),
        "description": "Registros sem valor na coluna Type.",
        "business_explanation": (
            "Algumas oportunidades não têm o tipo de negócio preenchido. "
            "Sem essa informação, não é possível classificá-las corretamente."
        ),
        "correction": (
            "Registros com Type nulo recebem in_scope=False "
            "e são excluídos da análise."
        ),
        "examples": affected[["Opportunity_ID", "Opportunity_Name", "Type"]].drop_duplicates().head(10),
    }


# 6. Divergência Amount vs soma de Total_Product_Amount
def check_amount_vs_products(df: pd.DataFrame) -> dict:
    work = df.copy()

    # Converte valores numéricos (aceita vírgula como decimal)
    def to_float(v):
        if pd.isna(v):
            return None
        try:
            return float(str(v).replace(",", ".").replace(" ", ""))
        except (ValueError, TypeError):
            return None

    work["_amount"] = work["Amount"].apply(to_float)
    work["_tpa"] = work["Total_Product_Amount"].apply(to_float)

    # Exclui estágios iniciais e linhas sem valores
    valid = work[
        ~work["Stage"].isin(EARLY_STAGES)
        & work["_amount"].notna()
        & work["_tpa"].notna()
    ]

    # Soma TPA por deal
    tpa_sum = valid.groupby(OPP_ID_COL)["_tpa"].sum().reset_index()
    tpa_sum.columns = [OPP_ID_COL, "_tpa_sum"]

    # Amount por deal (pega o primeiro valor — deve ser repetido)
    amount_per_deal = valid.groupby(OPP_ID_COL)["_amount"].first().reset_index()
    amount_per_deal.columns = [OPP_ID_COL, "_amount_deal"]

    merged = tpa_sum.merge(amount_per_deal, on=OPP_ID_COL)
    # Tolerância de R$ 0,50 para arredondamentos
    divergent = merged[abs(merged["_tpa_sum"] - merged["_amount_deal"]) > 0.5]
    affected_rows = df[df[OPP_ID_COL].isin(divergent[OPP_ID_COL])]

    return {
        "category": "Divergência Amount vs Total_Product_Amount",
        "rows": affected_rows,
        "count": len(affected_rows),
        "description": (
            "O campo Amount (valor total do deal) diverge da soma dos "
            "Total_Product_Amount dos produtos da mesma oportunidade."
        ),
        "business_explanation": (
            "O valor total do negócio não bate com a soma dos produtos. "
            "A regra do case é que o Amount pode estar errado; "
            "a verdade é a soma dos produtos. Esses valores serão corrigidos."
        ),
        "correction": (
            "Amount de cada deal foi substituído pela soma dos Total_Product_Amount "
            "dos seus produtos."
        ),
        "examples": (
            divergent[[OPP_ID_COL, "_amount_deal", "_tpa_sum"]]
            .rename(columns={"_amount_deal": "Amount_Original", "_tpa_sum": "TPA_Soma"})
            .head(10)
        ),
    }


# 7. Formatos numéricos inconsistentes 
def check_numeric_formats(df: pd.DataFrame) -> dict:
    def has_comma(v):
        if pd.isna(v):
            return False
        return "," in str(v)

    mask_amount = df["Amount"].apply(has_comma)
    mask_tpa = df["Total_Product_Amount"].apply(has_comma)
    affected = df[mask_amount | mask_tpa]

    return {
        "category": "Formatos numéricos inconsistentes",
        "rows": affected,
        "count": len(affected),
        "description": (
            "Campos Amount e/ou Total_Product_Amount contém vírgulas como separador decimal, "
            "impedindo conversão direta para número."
        ),
        "business_explanation": (
            "Os valores financeiros foram registrados com vírgula ao invés de ponto "
            "(ex: '3.043.949,95' ao invés de '3043949.95'). "
            "Isso impede qualquer cálculo automático."
        ),
        "correction": "Vírgulas foram substituídas por pontos e o campo convertido para float.",
        "examples": affected[["Opportunity_ID", "Amount", "Total_Product_Amount"]].head(10),
    }


# 8. Duplicatas verdadeiras 
def check_true_duplicates(df: pd.DataFrame) -> dict:
    dupes = df[df.duplicated(keep="first")]
    return {
        "category": "Linhas completamente duplicadas",
        "rows": dupes,
        "count": len(dupes),
        "description": (
            "Linhas com todos os campos idênticos a outra linha já existente."
        ),
        "business_explanation": (
            "Existem registros repetidos exatamente iguais, provavelmente por erro "
            "de exportação do CRM. Cada linha duplicada adiciona valor fictício às métricas."
        ),
        "correction": "Linhas completamente duplicadas foram removidas (mantém a primeira ocorrência).",
        "examples": dupes[["Opportunity_ID", "Opportunity_Name", "Product_Name"]].head(10),
    }


# 9. Nulos inesperados
def check_unexpected_nulls(df: pd.DataFrame) -> dict:
    advanced = df[~df["Stage"].isin(EARLY_STAGES + ["Opportunity Identified", "Qualified"])]
    mask = advanced["Amount"].isna() | advanced["Product_Name"].isna()
    affected = advanced[mask]
    return {
        "category": "Valores ausentes inesperados",
        "rows": affected,
        "count": len(affected),
        "description": (
            "Amount ou Product_Name ausentes em oportunidades em estágio avançado "
            "(não são Opportunity Identified nem Qualified)."
        ),
        "business_explanation": (
            "Oportunidades em estágios avançados devem ter valor e produto preenchidos. "
            "Campos vazios nesses casos indicam dado incompleto no CRM."
        ),
        "correction": (
            "Esses registros são sinalizados na coluna 'data_quality_flag' para "
            "revisão manual. Não são imputados automaticamente."
        ),
        "examples": affected[["Opportunity_ID", "Stage", "Amount", "Product_Name"]].head(10),
    }


# Agregador: roda todas as validações
def run_all_validations(df: pd.DataFrame) -> list:
    return [
        check_true_duplicates(df),
        check_stage_typos(df),
        check_lead_office_typos(df),
        check_lead_source_typos(df),
        check_out_of_scope_types(df),
        check_null_type(df),
        check_numeric_formats(df),
        check_amount_vs_products(df),
        check_unexpected_nulls(df),
    ]
