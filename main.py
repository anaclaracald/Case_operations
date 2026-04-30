"""
main.py — Orquestrador do pipeline completo de RevOps.

Executa em ordem:
  1. Carrega dados brutos
  2. Valida (identifica problemas)
  3. Limpa (aplica correções)
  4. Normaliza (colunas derivadas)
  5. Salva opps_corrigido.xlsx
  6. Gera relatorio_erros.html
  7. Calcula métricas de análise
  8. Gera analise.html
  9. Gera apresentacao.pdf

Uso:
    python main.py
    python main.py --skip-pdf   (pula geração do PDF)
"""

import sys
import os
import pandas as pd

# Garante que o diretório do projeto está no path
sys.path.insert(0, os.path.dirname(__file__))

from src.config import (
    RAW_DATA_PATH, PROCESSED_DATA_PATH,
    REPORT_ERRORS_PATH, REPORT_ANALYSIS_PATH, PRESENTATION_PATH,
    REFERENCE_DATE, OPP_ID_COL, EARLY_STAGES,
)
from src.load_data import load_raw
from src.validation import run_all_validations
from src.cleaning import run_cleaning_pipeline
from src.normalization import run_normalization_pipeline
from src.analysis import (
    revenue_mom_2026, lead_source_share, top10_open_opps,
    win_rate_by_source, avg_ticket_by_type, pipeline_by_stage,
    mix_new_vs_upsell, avg_sales_cycle, top10_clients_ytd, pipeline_age,
)
from src.visualizations import (
    chart_revenue_mom, chart_lead_source_share, table_top10_open,
    chart_win_rate, chart_avg_ticket, chart_pipeline_by_stage,
    chart_mix_new_upsell, chart_sales_cycle, chart_top10_clients, chart_pipeline_age,
)
from src.report_errors import generate_error_report
from src.report_analysis import generate_analysis_report
from src.presentation import generate_presentation


def _fmt_brl(v: float) -> str:
    try:
        return f"R$ {v:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "—"


def main(skip_pdf: bool = False):
    print("=" * 60)
    print("  Case RevOps Monks — Pipeline de Dados")
    print("=" * 60)

    # 1. CARREGA DADOS BRUTOS
    print("\n[1/9] Carregando dados brutos...")
    df_raw = load_raw(RAW_DATA_PATH)
    total_rows_raw = len(df_raw)
    print(f"      {total_rows_raw} linhas carregadas, {df_raw.shape[1]} colunas")

    # 2. VALIDA
    print("\n[2/9] Validando qualidade dos dados...")
    validation_results = run_all_validations(df_raw)
    for r in validation_results:
        print(f"      [{r['count']:>3} linhas] {r['category']}")

    # 3. LIMPA
    print("\n[3/9] Aplicando correções...")
    df_clean = run_cleaning_pipeline(df_raw)

    # 4. NORMALIZA
    print("\n[4/9] Normalizando e enriquecendo colunas...")
    df = run_normalization_pipeline(df_clean)

    # 5. SALVA XLSX CORRIGIDO
    print("\n[5/9] Salvando opps_corrigido.xlsx...")
    os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)
    df.to_excel(PROCESSED_DATA_PATH, index=False, engine="openpyxl")
    print(f"      Salvo em: {PROCESSED_DATA_PATH} ({len(df)} linhas)")

    # 6. RELATÓRIO DE ERROS
    print("\n[6/9] Gerando relatorio_erros.html...")
    unique_deals = df[OPP_ID_COL].nunique()
    out_of_scope = int((~df["in_scope"]).sum())

    # Reexecuta validações no df bruto para ter os números corretos
    generate_error_report(
        validation_results=validation_results,
        total_rows=total_rows_raw,
        unique_deals=unique_deals,
        out_of_scope=out_of_scope,
        path=REPORT_ERRORS_PATH,
    )

    # 7. CALCULA MÉTRICAS
    print("\n[7/9] Calculando métricas de análise...")
    df_scope = df[df["in_scope"]].copy()

    mom = revenue_mom_2026(df_scope)
    ls_share = lead_source_share(df_scope)
    top10_open = top10_open_opps(df_scope)
    wr = win_rate_by_source(df_scope)
    ticket = avg_ticket_by_type(df_scope)
    pipeline_stage = pipeline_by_stage(df_scope)
    mix = mix_new_vs_upsell(df_scope)
    cycle = avg_sales_cycle(df_scope)
    top10_clients = top10_clients_ytd(df_scope)
    age = pipeline_age(df_scope)

    # KPIs para o relatório
    is_closed_won = df_scope["is_closed_won"]
    is_open = df_scope["is_open"]

    # Deduplicar para nível de deal
    deals_scope = df_scope.drop_duplicates(subset=OPP_ID_COL, keep="first")
    cw_deals = deals_scope[deals_scope["is_closed_won"]]
    open_deals_df = deals_scope[deals_scope["is_open"]]

    total_revenue = cw_deals[cw_deals["Close_Date"].dt.year == 2026]["Amount"].sum()
    open_pipeline_value = open_deals_df["Amount"].sum()

    kpis = [
        {"label": "Receita Closed Won 2026", "value": _fmt_brl(total_revenue)},
        {"label": "Pipeline em Aberto", "value": _fmt_brl(open_pipeline_value)},
        {"label": "Deals Closed Won 2026", "value": str(int((cw_deals["Close_Date"].dt.year == 2026).sum()))},
        {"label": "Deals em Aberto", "value": str(len(open_deals_df))},
        {"label": "Ticket Médio Geral", "value": _fmt_brl(deals_scope["Amount"].mean())},
    ]

    # 8. RELATÓRIO DE ANÁLISE
    print("\n[8/9] Gerando analise.html...")

    # Observações de negócio
    def _mom_obs():
        if len(mom) == 0:
            return "Não há dados de Closed Won 2026 no período."
        top_month = mom.loc[mom["Receita (R$)"].idxmax(), "Mês"]
        top_val = _fmt_brl(mom["Receita (R$)"].max())
        return (f"O mês de maior receita foi <strong>{top_month}</strong> com {top_val}. "
                "Concentração no início do ano pode indicar renovações anuais.")

    def _ls_obs():
        if len(ls_share) == 0:
            return "Dados insuficientes."
        top = ls_share.iloc[0]
        return (f"<strong>{top['Lead_Source_Category']}</strong> lidera com "
                f"{top['Participação (%)']:.1f}% da receita fechada. "
                "Isso orienta onde concentrar investimento de geração de demanda.")

    def _wr_obs():
        if len(wr) == 0:
            return "Dados insuficientes."
        top = wr.iloc[0]
        return (f"<strong>{top['Lead_Source_Category']}</strong> apresenta o maior win rate "
                f"({top['Win Rate (%)']:.1f}%). Canais com win rate baixo merecem revisão "
                "de qualificação.")

    def _ticket_obs():
        if len(ticket) == 0:
            return "Dados insuficientes."
        top = ticket.iloc[0]
        return (f"<strong>{top['Type']}</strong> tem o maior ticket médio "
                f"({_fmt_brl(top['Ticket Médio (R$)'])}). "
                "Comparar com o esforço de venda ajuda a priorizar o tipo de negócio.")

    def _pipeline_obs():
        if len(pipeline_stage) == 0:
            return "Sem pipeline em aberto."
        top = pipeline_stage.iloc[0]
        return (f"<strong>{top['Estágio']}</strong> concentra o maior valor em pipeline "
                f"({_fmt_brl(top['Pipeline (R$)'])}). "
                "Estágios iniciais com grande volume indicam pipeline lento ou mal qualificado.")

    def _mix_obs():
        if len(mix) == 0:
            return "Dados insuficientes."
        upsell = mix[mix["Category"] == "Upsell"]["Receita (R$)"].sum()
        nb = mix[mix["Category"] == "New Business"]["Receita (R$)"].sum()
        total = upsell + nb
        pct = upsell / total * 100 if total > 0 else 0
        return (f"Upsell representa {pct:.1f}% da receita fechada — base de clientes "
                "existente é relevante. Alta proporção de upsell pode indicar baixa "
                "penetração em novas contas.")

    def _cycle_obs():
        if len(cycle) == 0:
            return "Dados insuficientes."
        fastest = cycle.iloc[0]
        slowest = cycle.iloc[-1]
        return (f"<strong>{fastest['Escritório']}</strong> fecha mais rápido "
                f"({fastest['Ciclo Médio (dias)']} dias) vs "
                f"<strong>{slowest['Escritório']}</strong> "
                f"({slowest['Ciclo Médio (dias)']} dias). "
                "Diferenças podem refletir perfil de cliente ou processo de venda.")

    def _top10_clients_obs():
        if len(top10_clients) == 0:
            return "Sem dados de Closed Won YTD 2026."
        top = top10_clients.iloc[0]
        conc = top10_clients["Receita YTD (R$)"].sum() / total_revenue * 100 if total_revenue > 0 else 0
        return (f"<strong>{top['Cliente']}</strong> é o maior cliente YTD "
                f"({_fmt_brl(top['Receita YTD (R$)'])}). "
                f"Os top 10 representam {conc:.1f}% da receita total — verificar concentração de carteira.")

    def _age_obs():
        if len(age) == 0:
            return "Sem pipeline em aberto."
        median_age = age["pipeline_age_days"].median()
        old = (age["pipeline_age_days"] > 180).sum()
        return (f"Mediana de {median_age:.0f} dias de idade do pipeline. "
                f"{old} oportunidades com mais de 180 dias em aberto — "
                "avaliar se são realmente ativas ou devem ser fechadas/removidas.")

    sections = [
        {
            "short_title": "Receita MoM",
            "title": "Receita Closed Won Mês a Mês em 2026",
            "chart_html": chart_revenue_mom(mom),
            "observation": _mom_obs(),
        },
        {
            "short_title": "Canal de Lead",
            "title": "Participação % por Canal de Lead — Closed Won",
            "chart_html": chart_lead_source_share(ls_share),
            "observation": _ls_obs(),
        },
        {
            "short_title": "Top 10 Abertos",
            "title": "Top 10 Oportunidades em Aberto",
            "chart_html": table_top10_open(top10_open),
            "observation": (
                "As maiores oportunidades em aberto. Acompanhar de perto o estágio e "
                "a data prevista de fechamento para garantir previsibilidade de receita."
            ),
        },
        {
            "short_title": "Taxa de Conversão",
            "title": "Win Rate por Canal de Lead (%)",
            "chart_html": chart_win_rate(wr),
            "observation": _wr_obs(),
        },
        {
            "short_title": "Ticket Médio",
            "title": "Ticket Médio por Tipo de Oportunidade",
            "chart_html": chart_avg_ticket(ticket),
            "observation": _ticket_obs(),
        },
        {
            "short_title": "Pipeline por Estágio",
            "title": "Pipeline em Aberto por Estágio (R$)",
            "chart_html": chart_pipeline_by_stage(pipeline_stage),
            "observation": _pipeline_obs(),
        },
        {
            "short_title": "Novos vs Upsell",
            "title": "Mix Novos Negócios vs Upsell ao Longo do Tempo",
            "chart_html": chart_mix_new_upsell(mix),
            "observation": _mix_obs(),
        },
        {
            "short_title": "Ciclo de Venda",
            "title": "Ciclo de Venda Médio por Escritório (dias)",
            "chart_html": chart_sales_cycle(cycle),
            "observation": _cycle_obs(),
        },
        {
            "short_title": "Top 10 Clientes",
            "title": "Top 10 Clientes — Closed Won Acumulado 2026",
            "chart_html": chart_top10_clients(top10_clients),
            "observation": _top10_clients_obs(),
        },
        {
            "short_title": "Idade Pipeline",
            "title": "Distribuição da Idade do Pipeline Aberto",
            "chart_html": chart_pipeline_age(age),
            "observation": _age_obs(),
        },
    ]

    generate_analysis_report(
        sections=sections,
        kpis=kpis,
        reference_date=REFERENCE_DATE,
        path=REPORT_ANALYSIS_PATH,
    )

    # 9. APRESENTAÇÃO PDF
    if not skip_pdf:
        print("\n[9/9] Gerando apresentacao.pdf...")
        # Monta os insights para o PDF
        insight_revenue = _mom_obs().replace("<strong>", "").replace("</strong>", "")
        insight_pipeline = _pipeline_obs().replace("<strong>", "").replace("</strong>", "")
        insight_mix = _mix_obs()
        insight_cycle = _cycle_obs().replace("<strong>", "").replace("</strong>", "")
        insight_win_rate = _wr_obs().replace("<strong>", "").replace("</strong>", "")

        # Conta problemas de cada categoria para o slide 3
        def _get_count(cat_name: str) -> int:
            for r in validation_results:
                if r["category"] == cat_name:
                    return r["count"]
            return 0

        total_affected = sum(r["count"] for r in validation_results)
        pct_affected = round(total_affected / total_rows_raw * 100, 0)

        stats = {
            "total_rows": total_rows_raw,
            "total_rows_clean": len(df),
            "unique_deals": unique_deals,
            "open_deals": len(open_deals_df),
            "closed_won_deals": len(cw_deals),
            "total_revenue": total_revenue,
            "open_pipeline_value": open_pipeline_value,
            "avg_ticket": deals_scope["Amount"].mean(),
            "stage_typos": _get_count("Typos em Stage"),
            "amount_divergence": _get_count("Divergência Amount vs Total_Product_Amount"),
            "numeric_format": _get_count("Formatos numéricos inconsistentes"),
            "out_of_scope": out_of_scope,
            "office_typos": _get_count("Typos em Lead_Office"),
            "source_issues": _get_count("Inconsistências em Lead_Source"),
            "insight_revenue": insight_revenue,
            "insight_pipeline": insight_pipeline,
            "insight_mix": insight_mix,
            "insight_cycle": insight_cycle,
            "insight_win_rate": insight_win_rate,
            "top5_clients": top10_clients.head(5),
            "win_rate": wr,
            "pct_affected": int(pct_affected),
        }
        generate_presentation(stats=stats, path=PRESENTATION_PATH)
    else:
        print("\n[9/9] Geração de PDF pulada (--skip-pdf)")

    # RESUMO FINAL
    print("\n" + "=" * 60)
    print("  ✅ Pipeline concluído com sucesso!")
    print("=" * 60)
    print(f"\n  📊 opps_corrigido.xlsx  → {PROCESSED_DATA_PATH}")
    print(f"  📋 relatorio_erros.html → {REPORT_ERRORS_PATH}")
    print(f"  📈 analise.html         → {REPORT_ANALYSIS_PATH}")
    if not skip_pdf:
        print(f"  📄 apresentacao.pdf     → {PRESENTATION_PATH}")
    print()


if __name__ == "__main__":
    skip = "--skip-pdf" in sys.argv
    main(skip_pdf=skip)
