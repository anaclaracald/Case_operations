"""
visualizations.py — Geração de gráficos com Plotly.

Cada função recebe os dados calculados pelo analysis.py e retorna
o HTML do gráfico como string (para embutir nos relatórios HTML).
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


# Paleta de cores consistente com identidade visual do case
COLORS = {
    "primary": "#8B5CF6",
    "secondary": "#FBE122",
    "success": "#27AE60",
    "danger": "#E74C3C",
    "neutral": "#95A5A6",
    "dark": "#1A1528",
    "palette": [
        "#8B5CF6", "#FBE122", "#1A1528", "#A78BFA",
        "#FDE047", "#5B21B6", "#CA8A04", "#DDD6FE",
    ],
}


def _to_html(fig) -> str:
    return fig.to_html(full_html=False, include_plotlyjs="cdn", config={"responsive": True})


def _fmt_brl(v: float) -> str:
    return f"R$ {v:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ---------------------------------------------------------------------------
# 1. Receita Closed Won MoM
# ---------------------------------------------------------------------------

def chart_revenue_mom(df: pd.DataFrame) -> str:
    fig = px.bar(
        df,
        x="Mês",
        y="Receita (R$)",
        text=df["Receita (R$)"].apply(_fmt_brl),
        color_discrete_sequence=[COLORS["primary"]],
        title="Receita Closed Won por Mês — 2026",
    )
    fig.update_traces(textposition="outside", marker_cornerradius=8)
    fig.update_layout(
        xaxis_title="Mês",
        yaxis_title="Receita (R$)",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=13, color=COLORS["dark"]),
        title_font=dict(family="Poppins, sans-serif", size=18, color=COLORS["dark"]),
    )
    return _to_html(fig)


# ---------------------------------------------------------------------------
# 2. Participação por Lead_Source_Category
# ---------------------------------------------------------------------------

def chart_lead_source_share(df: pd.DataFrame) -> str:
    fig = px.pie(
        df,
        names="Lead_Source_Category",
        values="Receita (R$)",
        title="Participação % por Canal de Lead — Closed Won",
        color_discrete_sequence=COLORS["palette"],
        hole=0.45,
    )
    fig.update_traces(textinfo="label+percent", pull=[0.03] * len(df))
    fig.update_layout(
        font=dict(family="Inter, sans-serif", size=13, color=COLORS["dark"]),
        title_font=dict(family="Poppins, sans-serif", size=18, color=COLORS["dark"]),
        legend_title_text="Canal",
    )
    return _to_html(fig)


# ---------------------------------------------------------------------------
# 3. Top 10 Oportunidades em Aberto (tabela)
# ---------------------------------------------------------------------------

def table_top10_open(df: pd.DataFrame) -> str:
    df = df.copy()
    if "Valor (R$)" in df.columns:
        df["Valor (R$)"] = df["Valor (R$)"].apply(lambda v: _fmt_brl(v) if pd.notna(v) else "—")
    if "Previsão de Fechamento" in df.columns:
        df["Previsão de Fechamento"] = pd.to_datetime(
            df["Previsão de Fechamento"], errors="coerce"
        ).dt.strftime("%d/%m/%Y").fillna("—")

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(df.columns),
            fill_color=COLORS["primary"],
            font=dict(color="white", size=13, family="Poppins, sans-serif"),
            align="left",
            height=40,
        ),
        cells=dict(
            values=[df[c] for c in df.columns],
            fill_color=[["#F8F7FB" if i % 2 == 0 else "white" for i in range(len(df))]],
            align="left",
            font=dict(size=12, family="Inter, sans-serif", color=COLORS["dark"]),
            height=36,
        ),
    )])
    fig.update_layout(
        title="Top 10 Oportunidades em Aberto",
        title_font=dict(family="Poppins, sans-serif", size=18, color=COLORS["dark"]),
        margin=dict(l=0, r=0, t=50, b=0),
        height=420,
    )
    return _to_html(fig)


# ---------------------------------------------------------------------------
# 4. Win Rate por Lead_Source_Category
# ---------------------------------------------------------------------------

def chart_win_rate(df: pd.DataFrame) -> str:
    fig = px.bar(
        df.sort_values("Win Rate (%)"),
        x="Win Rate (%)",
        y="Lead_Source_Category",
        orientation="h",
        text="Win Rate (%)",
        color="Win Rate (%)",
        color_continuous_scale=[[0, "#EBE4FF"], [1, COLORS["primary"]]],
        title="Win Rate por Canal de Lead (%)",
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside", marker_cornerradius=8)
    fig.update_layout(
        xaxis_title="Win Rate (%)",
        yaxis_title="",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=13, color=COLORS["dark"]),
        title_font=dict(family="Poppins, sans-serif", size=18, color=COLORS["dark"]),
        coloraxis_showscale=False,
    )
    return _to_html(fig)


# ---------------------------------------------------------------------------
# 5. Ticket Médio por Type
# ---------------------------------------------------------------------------

def chart_avg_ticket(df: pd.DataFrame) -> str:
    fig = px.bar(
        df,
        x="Type",
        y="Ticket Médio (R$)",
        text=df["Ticket Médio (R$)"].apply(_fmt_brl),
        color_discrete_sequence=[COLORS["secondary"]],
        title="Ticket Médio por Tipo de Oportunidade",
    )
    fig.update_traces(textposition="outside", marker_cornerradius=8)
    fig.update_layout(
        xaxis_title="Tipo",
        yaxis_title="Ticket Médio (R$)",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=13, color=COLORS["dark"]),
        title_font=dict(family="Poppins, sans-serif", size=18, color=COLORS["dark"]),
    )
    return _to_html(fig)


# ---------------------------------------------------------------------------
# 6. Pipeline em Aberto por Stage
# ---------------------------------------------------------------------------

def chart_pipeline_by_stage(df: pd.DataFrame) -> str:
    fig = px.bar(
        df.sort_values("Pipeline (R$)", ascending=True),
        x="Pipeline (R$)",
        y="Estágio",
        orientation="h",
        text=df.sort_values("Pipeline (R$)", ascending=True)["Pipeline (R$)"].apply(_fmt_brl),
        color_discrete_sequence=[COLORS["primary"]],
        title="Pipeline em Aberto por Estágio (R$)",
    )
    fig.update_traces(textposition="outside", marker_cornerradius=8)
    fig.update_layout(
        xaxis_title="Valor (R$)",
        yaxis_title="",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=13, color=COLORS["dark"]),
        title_font=dict(family="Poppins, sans-serif", size=18, color=COLORS["dark"]),
    )
    return _to_html(fig)


# ---------------------------------------------------------------------------
# 7. Mix New Business vs Upsell
# ---------------------------------------------------------------------------

def chart_mix_new_upsell(df: pd.DataFrame) -> str:
    fig = px.bar(
        df,
        x="Mês",
        y="Receita (R$)",
        color="Category",
        barmode="stack",
        color_discrete_map={"Novos Negócios": COLORS["primary"], "Upsell": COLORS["secondary"]},
        title="Mix Novos Negócios vs Upsell — Receita Mensal",
    )
    fig.update_traces(marker_cornerradius=4)
    fig.update_layout(
        xaxis_title="Mês",
        yaxis_title="Receita (R$)",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=13, color=COLORS["dark"]),
        title_font=dict(family="Poppins, sans-serif", size=18, color=COLORS["dark"]),
        legend_title_text="Tipo",
    )
    return _to_html(fig)


# ---------------------------------------------------------------------------
# 8. Ciclo de Venda Médio por Lead_Office
# ---------------------------------------------------------------------------

def chart_sales_cycle(df: pd.DataFrame) -> str:
    fig = px.bar(
        df,
        x="Escritório",
        y="Ciclo Médio (dias)",
        text="Ciclo Médio (dias)",
        color_discrete_sequence=[COLORS["palette"][2]],
        title="Ciclo de Venda Médio por Escritório (dias)",
    )
    fig.update_traces(textposition="outside", marker_cornerradius=8)
    fig.update_layout(
        xaxis_title="Escritório",
        yaxis_title="Dias",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=13, color=COLORS["dark"]),
        title_font=dict(family="Poppins, sans-serif", size=18, color=COLORS["dark"]),
    )
    return _to_html(fig)


# ---------------------------------------------------------------------------
# 9. Top 10 Clientes YTD (tabela/barra horizontal)
# ---------------------------------------------------------------------------

def chart_top10_clients(df: pd.DataFrame) -> str:
    fig = px.bar(
        df.sort_values("Receita YTD (R$)"),
        x="Receita YTD (R$)",
        y="Cliente",
        orientation="h",
        text=df.sort_values("Receita YTD (R$)")["Receita YTD (R$)"].apply(_fmt_brl),
        color_discrete_sequence=[COLORS["primary"]],
        title="Top 10 Clientes — Receita Closed Won YTD 2026",
    )
    fig.update_traces(textposition="outside", marker_cornerradius=8)
    fig.update_layout(
        xaxis_title="Receita (R$)",
        yaxis_title="",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=13, color=COLORS["dark"]),
        title_font=dict(family="Poppins, sans-serif", size=18, color=COLORS["dark"]),
        height=450,
    )
    return _to_html(fig)


# ---------------------------------------------------------------------------
# 10. Histograma — Idade do Pipeline Aberto
# ---------------------------------------------------------------------------

def chart_pipeline_age(df: pd.DataFrame) -> str:
    fig = px.histogram(
        df,
        x="pipeline_age_days",
        nbins=20,
        color_discrete_sequence=[COLORS["secondary"]],
        title="Distribuição da Idade do Pipeline Aberto (dias)",
        labels={"pipeline_age_days": "Idade (dias)", "count": "Nº de Oportunidades"},
    )
    fig.update_traces(marker_cornerradius=4)
    fig.update_layout(
        xaxis_title="Idade (dias desde criação)",
        yaxis_title="Nº de Oportunidades",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=13, color=COLORS["dark"]),
        title_font=dict(family="Poppins, sans-serif", size=18, color=COLORS["dark"]),
        bargap=0.05,
    )
    return _to_html(fig)
