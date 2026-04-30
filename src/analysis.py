"""
analysis.py — Cálculo de todas as métricas de negócio.

REGRA IMPORTANTE DE GRANULARIDADE:
  - A planilha é em nível de produto. Uma oportunidade pode ter N linhas.
  - Para métricas de DEAL (Amount, ciclo de venda, win rate):
      → Deduplicar por Opportunity_ID antes de calcular.
  - Para métricas de PRODUTO (mix de produtos):
      → Usar nível de linha.

Todas as funções recebem o DataFrame já limpo, normalizado e filtrado (in_scope=True).
"""

import pandas as pd
from src.config import OPP_ID_COL

# Helper: deduplicar para nível de deal
def _deals(df: pd.DataFrame) -> pd.DataFrame:
    # Retorna um DataFrame com uma linha por Opportunity_ID.
    deal_cols = [
        OPP_ID_COL, "Account_ID", "Account_Name", "Opportunity_Owner",
        "Opportunity_Name", "Type", "Stage", "Amount", "Close_Date", "Created_Date",
        "Lead_Source", "Lead_Source_Category", "Lead_Office",
        "year_month", "is_closed_won", "is_open",
        "sales_cycle_days", "pipeline_age_days",
    ]
    existing_cols = [c for c in deal_cols if c in df.columns]
    return df[existing_cols].drop_duplicates(subset=OPP_ID_COL, keep="first")

# 1. Receita Closed Won MoM em 2026
def revenue_mom_2026(df: pd.DataFrame) -> pd.DataFrame:
    # Soma de Amount por mês para oportunidades Closed Won em 2026.
    deals = _deals(df)
    cw = deals[
        deals["is_closed_won"]
        & (deals["Close_Date"].dt.year == 2026)
        & deals["Amount"].notna()
    ].copy()

    mom = (
        cw.groupby("year_month")["Amount"]
        .sum()
        .reset_index()
        .sort_values("year_month")
        .rename(columns={"year_month": "Mês", "Amount": "Receita (R$)"})
    )
    return mom

# 2. Participação % por Lead_Source_Category (Closed Won)
def lead_source_share(df: pd.DataFrame) -> pd.DataFrame:
    # Participação percentual de cada Lead_Source_Category nas oportunidades Closed Won.
    deals = _deals(df)
    cw = deals[deals["is_closed_won"]].copy()
    total = cw["Amount"].sum()

    share = (
        cw.groupby("Lead_Source_Category")["Amount"]
        .sum()
        .reset_index()
        .rename(columns={"Amount": "Receita (R$)"})
    )
    share["Participação (%)"] = (share["Receita (R$)"] / total * 100).round(1)
    return share.sort_values("Receita (R$)", ascending=False)


# 3. Top 10 Oportunidades em Aberto
def top10_open_opps(df: pd.DataFrame) -> pd.DataFrame:
   
    # Produtos por deal (nível linha)
    products = (
        df[df["is_open"] & df["Product_Name"].notna()]
        .groupby(OPP_ID_COL)["Product_Name"]
        .apply(lambda x: ", ".join(x.dropna().unique()))
        .reset_index()
        .rename(columns={"Product_Name": "Produtos"})
    )

    deals = _deals(df)
    open_deals = deals[deals["is_open"] & deals["Amount"].notna()].copy()
    open_deals = open_deals.merge(products, on=OPP_ID_COL, how="left")

    top10 = (
        open_deals[["Account_Name", "Produtos", "Stage", "Amount", "Close_Date"]]
        .sort_values("Amount", ascending=False)
        .head(10)
        .rename(columns={
            "Account_Name": "Cliente",
            "Stage": "Estágio",
            "Amount": "Valor (R$)",
            "Close_Date": "Previsão de Fechamento",
        })
    )
    return top10

# 4. Win Rate por Lead_Source_Category
def win_rate_by_source(df: pd.DataFrame) -> pd.DataFrame:
    # % de Closed Won por Lead_Source_Category.
    # Base: Closed Won + Open Pipeline (exclui outros stages).
    deals = _deals(df)
    relevant = deals[deals["is_closed_won"] | deals["is_open"]].copy()

    total = relevant.groupby("Lead_Source_Category").size().reset_index(name="Total")
    won = (
        relevant[relevant["is_closed_won"]]
        .groupby("Lead_Source_Category")
        .size()
        .reset_index(name="Closed Won")
    )

    wr = total.merge(won, on="Lead_Source_Category", how="left").fillna(0)
    wr["Win Rate (%)"] = (wr["Closed Won"] / wr["Total"] * 100).round(1)
    return wr.sort_values("Win Rate (%)", ascending=False)


# 5. Ticket Médio por Type
def avg_ticket_by_type(df: pd.DataFrame) -> pd.DataFrame:
    # Valor médio de deal por Type. Nível de deal (deduplicado).
    deals = _deals(df)
    valid = deals[deals["Amount"].notna()].copy()

    ticket = (
        valid.groupby("Type")["Amount"]
        .mean()
        .reset_index()
        .rename(columns={"Amount": "Ticket Médio (R$)"})
        .sort_values("Ticket Médio (R$)", ascending=False)
    )
    ticket["Ticket Médio (R$)"] = ticket["Ticket Médio (R$)"].round(2)
    return ticket

# 6. Pipeline em Aberto por Stage
def pipeline_by_stage(df: pd.DataFrame) -> pd.DataFrame:
    # Soma de Amount por Stage para oportunidades em aberto.
    deals = _deals(df)
    open_deals = deals[deals["is_open"] & deals["Amount"].notna()].copy()

    pipeline = (
        open_deals.groupby("Stage")["Amount"]
        .sum()
        .reset_index()
        .rename(columns={"Stage": "Estágio", "Amount": "Pipeline (R$)"})
        .sort_values("Pipeline (R$)", ascending=False)
    )
    return pipeline

# 7. Mix New Business vs Upsell ao longo do tempo
def mix_new_vs_upsell(df: pd.DataFrame) -> pd.DataFrame:
    """Proporção entre New Business (Project Competitive/Not Competitive)
    e Change Order/Upsell por mês de fechamento."""

    deals = _deals(df)
    cw = deals[deals["is_closed_won"] & deals["Amount"].notna()].copy()

    cw["Category"] = cw["Type"].apply(
        lambda t: "Upsell" if t == "Change Order/Upsell" else "New Business"
    )

    mix = (
        cw.groupby(["year_month", "Category"])["Amount"]
        .sum()
        .reset_index()
        .rename(columns={"year_month": "Mês", "Amount": "Receita (R$)"})
        .sort_values("Mês")
    )
    return mix


# 8. Ciclo de Venda Médio por Lead_Office
def avg_sales_cycle(df: pd.DataFrame) -> pd.DataFrame:
    # Média de dias entre Created_Date e Close_Date por Lead_Office.
   
    deals = _deals(df)
    cw = deals[
        deals["is_closed_won"]
        & deals["sales_cycle_days"].notna()
    ].copy()
    cw["sales_cycle_days"] = pd.to_numeric(cw["sales_cycle_days"], errors="coerce")

    cycle = (
        cw.groupby("Lead_Office")["sales_cycle_days"]
        .mean()
        .reset_index()
        .rename(columns={"Lead_Office": "Escritório", "sales_cycle_days": "Ciclo Médio (dias)"})
    )
    cycle["Ciclo Médio (dias)"] = cycle["Ciclo Médio (dias)"].round(0).astype(int)
    return cycle.sort_values("Ciclo Médio (dias)")


# 9. Top 10 Clientes Closed Won YTD 2026
def top10_clients_ytd(df: pd.DataFrame) -> pd.DataFrame:
    # 10 maiores clientes por soma de Amount em Closed Won 2026 (YTD).
    
    deals = _deals(df)
    cw = deals[
        deals["is_closed_won"]
        & (deals["Close_Date"].dt.year == 2026)
        & deals["Amount"].notna()
    ].copy()

    top = (
        cw.groupby("Account_Name")["Amount"]
        .sum()
        .reset_index()
        .rename(columns={"Account_Name": "Cliente", "Amount": "Receita YTD (R$)"})
        .sort_values("Receita YTD (R$)", ascending=False)
        .head(10)
    )
    return top


# 10. Idade do Pipeline Aberto
def pipeline_age(df: pd.DataFrame) -> pd.DataFrame:
    # Distribuição de idade (dias desde Created_Date) do pipeline aberto.

    deals = _deals(df)
    open_deals = deals[
        deals["is_open"] & deals["pipeline_age_days"].notna()
    ].copy()
    open_deals["pipeline_age_days"] = pd.to_numeric(
        open_deals["pipeline_age_days"], errors="coerce"
    )
    return open_deals[["Opportunity_ID", "Account_Name", "Stage", "Amount", "pipeline_age_days"]]
