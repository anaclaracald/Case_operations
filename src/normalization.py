"""
normalization.py — Enriquecimento e normalização do DataFrame limpo.

Adiciona colunas derivadas necessárias para análise:
  - Lead_Source_Category
  - year_month (para análises MoM)
  - sales_cycle_days
  - is_closed_won, is_open
  - pipeline_age_days
"""

import pandas as pd
from src.config import (
    LEAD_SOURCE_TO_CATEGORY,
    CANONICAL_LEAD_SOURCE,
    OPP_ID_COL,
    REFERENCE_DATE,
)


def add_lead_source_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria a coluna Lead_Source_Category mapeando Lead_Source → categoria.
    Valores não mapeados recebem 'Unknown'.
    """
    df = df.copy()
    df["Lead_Source_Category"] = df["Lead_Source"].map(LEAD_SOURCE_TO_CATEGORY).fillna("Unknown")
    return df
  
# Converte Close_Date e Created_Date para datetime.
def normalize_dates(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in ["Close_Date", "Created_Date"]:
        df[col] = pd.to_datetime(df[col], dayfirst=True, errors="coerce")
    return df


def add_helper_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adiciona colunas derivadas para facilitar as análises:
      - year_month: período de fechamento (YYYY-MM)
      - is_closed_won: bool
      - is_open: bool (nem Closed Won nem Closed Lost)
      - sales_cycle_days: dias entre Created_Date e Close_Date (só para Closed Won)
      - pipeline_age_days: dias desde Created_Date até hoje (só para open)
    """
    df = df.copy()
    ref = pd.Timestamp(REFERENCE_DATE)

    df["year_month"] = df["Close_Date"].dt.to_period("M").astype(str)
    df["is_closed_won"] = df["Stage"] == "Closed Won"
    # Aberto = qualquer estágio que não seja Closed Won ou Closed Lost
    df["is_open"] = ~df["Stage"].isin(["Closed Won", "Closed Lost"])

    # Ciclo de venda: apenas para Closed Won com ambas as datas preenchidas
    df["sales_cycle_days"] = None
    closed_mask = df["is_closed_won"] & df["Created_Date"].notna() & df["Close_Date"].notna()
    df.loc[closed_mask, "sales_cycle_days"] = (
        df.loc[closed_mask, "Close_Date"] - df.loc[closed_mask, "Created_Date"]
    ).dt.days

    # Idade do pipeline: dias desde criação até hoje (só para oportunidades abertas)
    df["pipeline_age_days"] = None
    open_mask = df["is_open"] & df["Created_Date"].notna()
    df.loc[open_mask, "pipeline_age_days"] = (
        ref - df.loc[open_mask, "Created_Date"]
    ).dt.days

    return df

# Pipeline de normalização 
def run_normalization_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_dates(df)
    df = add_lead_source_category(df)
    df = add_helper_columns(df)
    return df
