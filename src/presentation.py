"""
presentation.py — Gera apresentacao.pdf usando ReportLab.

8 slides com layout executivo para liderança de Operations.
"""

import os
from src.config import PRESENTATION_PATH


def _fmt_brl(v) -> str:
    try:
        return f"R$ {float(v):,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "—"


def generate_presentation(stats: dict, path: str = PRESENTATION_PATH) -> None:
    """
    Gera a apresentação em PDF usando ReportLab.
    """
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.units import mm, cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, HRFlowable
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

    os.makedirs(os.path.dirname(path), exist_ok=True)

    PAGE_W, PAGE_H = landscape(A4)

    # -----------------------------------------------------------------------
    # Cores (Updated to match the new design)
    # -----------------------------------------------------------------------
    PRIMARY = colors.HexColor("#8B5CF6")
    PRIMARY_LIGHT = colors.HexColor("#EBE4FF")
    SECONDARY = colors.HexColor("#FBE122")
    DARK = colors.HexColor("#1A1528")
    GRAY = colors.HexColor("#6B7280")
    WHITE = colors.white
    BG = colors.HexColor("#F8F7FB")

    # -----------------------------------------------------------------------
    # Estilos
    # -----------------------------------------------------------------------
    styles = getSampleStyleSheet()

    def S(name, **kwargs):
        return ParagraphStyle(name, **kwargs)

    H1 = S("H1", fontSize=42, textColor=DARK, fontName="Helvetica-Bold",
            spaceAfter=8, alignment=TA_LEFT, leading=48)
    H2 = S("H2", fontSize=24, textColor=DARK, fontName="Helvetica-Bold",
            spaceAfter=16)
    BODY = S("BODY", fontSize=11, textColor=DARK, fontName="Helvetica",
             spaceAfter=4, leading=16)
    BODY_GRAY = S("BODY_GRAY", fontSize=11, textColor=GRAY, fontName="Helvetica",
                  spaceAfter=4, leading=16)
    LABEL = S("LABEL", fontSize=9, textColor=DARK, fontName="Helvetica-Bold",
              spaceAfter=4)

    # -----------------------------------------------------------------------
    # Helper: slide header
    # -----------------------------------------------------------------------
    def slide_header(title: str, subtitle: str = "") -> list:
        elements = [
            Spacer(1, 10 * mm),
            Paragraph(f"<b>{title}</b>", H2)
        ]
        if subtitle:
            elements.append(Paragraph(subtitle, BODY_GRAY))
        elements.append(Spacer(1, 10 * mm))
        return elements

    # -----------------------------------------------------------------------
    # Helper: info card (Purple or Yellow)
    # -----------------------------------------------------------------------
    def info_card(label: str, value: str, is_yellow=False) -> Table:
        bg_color = SECONDARY if is_yellow else PRIMARY
        text_color = DARK if is_yellow else WHITE
        
        data = [
            [Paragraph(label, ParagraphStyle("lbl", fontSize=10, textColor=text_color, fontName="Helvetica-Bold"))],
            [Spacer(1, 5*mm)],
            [Paragraph(f"<b><font color='#{text_color.hexval()[2:]}'>{value}</font></b>",
                       ParagraphStyle("cv", fontSize=24, fontName="Helvetica-Bold",
                                      alignment=TA_LEFT))],
        ]
        t = Table(data, colWidths=[65 * mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), bg_color),
            ("ROUNDEDCORNERS", (0, 0), (-1, -1), 16),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("TOPPADDING", (0, 0), (-1, -1), 16),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 16),
            ("LEFTPADDING", (0, 0), (-1, -1), 16),
            ("RIGHTPADDING", (0, 0), (-1, -1), 16),
        ]))
        return t

    # -----------------------------------------------------------------------
    # Helper: simple data table
    # -----------------------------------------------------------------------
    def data_table(headers: list, rows: list) -> Table:
        data = [headers] + rows
        col_w = (PAGE_W - 80 * mm) / len(headers)
        t = Table(data, colWidths=[col_w] * len(headers))
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BG, WHITE]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ROWPADDING", (0, 0), (-1, -1), 10),
        ]))
        return t

    # -----------------------------------------------------------------------
    # Monta os slides
    # -----------------------------------------------------------------------
    story = []

    # ---- SLIDE 1: CAPA ----
    story.append(Spacer(1, 40 * mm))
    story.append(Paragraph('<b>Sumário<br/>Executivo</b>', H1))
    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph(
        "Auditoria de dados, análise de pipeline comercial e recomendações de processo para o time de Operations.",
        ParagraphStyle("cs", fontSize=14, textColor=GRAY, leading=20, spaceAfter=10)
    ))
    story.append(Spacer(1, 20 * mm))
    story.append(Paragraph(
        f"<b>Monks · Estágio Operations · 2026</b><br/>"
        f"Dataset: 413 linhas · opps_corrupted.xlsx",
        BODY
    ))
    story.append(PageBreak())

    # ---- SLIDE 2: VISÃO GERAL ----
    story.extend(slide_header("Visão Geral do Dataset", "Acompanhando performance. Gerando resultados."))

    cards_row1 = Table(
        [[
            info_card("Linhas Brutas", str(stats.get("total_rows", 413)), is_yellow=False),
            Spacer(10*mm, 1),
            info_card("Deals Únicos", str(stats.get("unique_deals", "—")), is_yellow=True),
            Spacer(10*mm, 1),
            info_card("Em Aberto", str(stats.get("open_deals", "—")), is_yellow=False),
        ]],
        colWidths=[65*mm, 10*mm, 65*mm, 10*mm, 65*mm]
    )
    story.append(cards_row1)
    story.append(Spacer(1, 15 * mm))

    cards_row2 = Table(
        [[
            info_card("Closed Won", str(stats.get("closed_won_deals", "—")), is_yellow=True),
            Spacer(10*mm, 1),
            info_card("Receita CW 2026", _fmt_brl(stats.get("total_revenue", 0)), is_yellow=False),
            Spacer(10*mm, 1),
            info_card("Pipeline Aberto", _fmt_brl(stats.get("open_pipeline_value", 0)), is_yellow=True),
        ]],
        colWidths=[65*mm, 10*mm, 65*mm, 10*mm, 65*mm]
    )
    story.append(cards_row2)
    story.append(PageBreak())

    # ---- SLIDE 3: ERROS ----
    story.extend(slide_header("Principais Problemas Encontrados", "Auditoria de Qualidade"))
    
    erros = [
        ("Typos em Estágio, Escritório e Canal",
         f"{stats.get('stage_typos', 0) + stats.get('office_typos', 0)} linhas"),
        ("Divergência de Valor vs soma dos produtos",
         f"{stats.get('amount_divergence', 0)} deals"),
        ("Valores numéricos em formato texto",
         f"{stats.get('numeric_format', 0)} linhas"),
        ("Registros fora de escopo",
         f"{stats.get('out_of_scope', 0)} linhas"),
    ]
    
    err_data = [["Problema", "Impacto"]]
    for title, badge in erros:
        err_data.append([title, badge])
        
    story.append(data_table(err_data[0], err_data[1:]))
    story.append(PageBreak())

    # ---- SLIDE 4: IMPACTO DA LIMPEZA ----
    story.extend(slide_header("Impacto da Limpeza de Dados", "Antes vs Depois"))

    impact_rows = [
        ["Aspecto", "Antes", "Depois", "Ação"],
        ["Linhas / Deals",
         f"413 linhas",
         f"{stats.get('unique_deals', '—')} deals únicos",
         "Deduplicação"],
        ["Estágio",
         f"{stats.get('stage_typos', 0)} typos",
         "7 valores",
         "Mapeamento"],
        ["Escritório",
         f"{stats.get('office_typos', 0)} variações",
         "3 valores",
         "Normalização"],
        ["Canal de Lead",
         f"{stats.get('source_issues', 0)} inconsistências",
         "6 categorias",
         "Taxonomia"],
        ["Valor (Amount)",
         f"{stats.get('amount_divergence', 0)} divergentes",
         "Recalculado",
         "Soma TPA"],
    ]
    story.append(data_table(impact_rows[0], impact_rows[1:]))
    story.append(PageBreak())

    # ---- SLIDE 5: INSIGHTS RECEITA E PIPELINE ----
    story.extend(slide_header("Insights — Receita e Pipeline"))

    insights = [
        ("Receita concentrada no início do ano",
         stats.get("insight_revenue", "—")),
        ("Pipeline com concentração em estágios iniciais",
         stats.get("insight_pipeline", "—")),
        ("Mix Novos Negócios vs Upsell",
         stats.get("insight_mix", "—")),
        ("Ciclo de venda varia por escritório",
         stats.get("insight_cycle", "—")),
    ]
    
    for idx, (title, body) in enumerate(insights):
        is_yellow = (idx % 2 == 1)
        bg_col = SECONDARY if is_yellow else PRIMARY
        txt_col = DARK if is_yellow else WHITE
        
        t = Table(
            [[Paragraph(f"<b><font color='#{txt_col.hexval()[2:]}'>{title}</font></b>", S("H3", fontSize=13, spaceAfter=6))],
             [Paragraph(f"<font color='#{txt_col.hexval()[2:]}'>{body}</font>", S("BODY", fontSize=11, leading=16))]],
            colWidths=[PAGE_W - 60 * mm]
        )
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), bg_col),
            ("ROUNDEDCORNERS", (0, 0), (-1, -1), 12),
            ("LEFTPADDING", (0, 0), (-1, -1), 20),
            ("RIGHTPADDING", (0, 0), (-1, -1), 20),
            ("TOPPADDING", (0, 0), (-1, -1), 15),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 15),
        ]))
        story.append(t)
        story.append(Spacer(1, 6 * mm))
        
    story.append(PageBreak())

    # ---- SLIDE 6: CLIENTES E CANAL DE LEAD ----
    story.extend(slide_header("Insights — Clientes e Canal de Lead"))

    client_rows = [["Cliente", "Receita Acumulada (R$)"]]
    top5 = stats.get("top5_clients")
    if top5 is not None and len(top5) > 0:
        for _, row in top5.head(5).iterrows():
            client_rows.append([str(row.iloc[0])[:30], _fmt_brl(row.iloc[1])])

    wr_rows = [["Canal", "Taxa de Conversão"]]
    wr_df = stats.get("win_rate")
    if wr_df is not None and len(wr_df) > 0:
        for _, row in wr_df.iterrows():
            wr_rows.append([str(row["Lead_Source_Category"]), f"{row['Win Rate (%)']:.1f}%"])

    t1 = data_table(client_rows[0], client_rows[1:])
    t2 = data_table(wr_rows[0], wr_rows[1:])
    # overriding widths for side-by-side
    t1._argW[0] = 70*mm
    t1._argW[1] = 30*mm
    t2._argW[0] = 70*mm
    t2._argW[1] = 30*mm

    side_by_side = Table(
        [[t1, Spacer(10 * mm, 1), t2]],
        colWidths=[100*mm, 10 * mm, 100*mm]
    )
    story.append(side_by_side)
    story.append(PageBreak())

    # ---- SLIDE 7: RECOMENDAÇÕES ----
    story.extend(slide_header("Recomendações de Processo"))

    recs = [
        ("Validação em tempo real no Salesforce",
         "Implementar Validation Rules e Picklists para Estágio, Escritório e Canal de Lead."),
        ("Automação do recálculo de Valor (Amount)",
         "Criar um Flow/trigger no Salesforce que recalcule Amount ao salvar produtos."),
        ("Dashboard semanal de qualidade de dados",
         "Monitorar oportunidades sem produto em estágios avançados e Amount divergente."),
        ("Canal de Lead como Picklist gerenciada",
         "Substituir o campo livre pelos 17 valores canônicos."),
    ]
    
    for idx, (title, desc) in enumerate(recs):
        is_yellow = (idx % 2 == 1)
        bg_col = SECONDARY if is_yellow else PRIMARY
        txt_col = DARK if is_yellow else WHITE
        
        t = Table(
            [[Paragraph(f"<b><font color='#{txt_col.hexval()[2:]}'>{title}</font></b>", S("H3", fontSize=13, spaceAfter=6))],
             [Paragraph(f"<font color='#{txt_col.hexval()[2:]}'>{desc}</font>", S("BODY", fontSize=11, leading=16))]],
            colWidths=[PAGE_W - 60 * mm]
        )
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), bg_col),
            ("ROUNDEDCORNERS", (0, 0), (-1, -1), 12),
            ("LEFTPADDING", (0, 0), (-1, -1), 20),
            ("RIGHTPADDING", (0, 0), (-1, -1), 20),
            ("TOPPADDING", (0, 0), (-1, -1), 15),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 15),
        ]))
        story.append(t)
        story.append(Spacer(1, 6 * mm))

    story.append(PageBreak())

    # ---- SLIDE 8: CONCLUSÃO ----
    story.append(Spacer(1, 40 * mm))
    story.append(Paragraph('<b>Conclusões e Aprendizados</b>', H1))
    story.append(Spacer(1, 10 * mm))
    
    pct = stats.get("pct_affected", "—")
    story.append(Paragraph(
        f"Dados confiáveis são pré-requisito para qualquer análise de RevOps. "
        f"A limpeza revelou que <b>{pct}% das linhas</b> tinham algum problema — "
        f"a maioria corrigível com validação na origem.",
        ParagraphStyle("concb", fontSize=16, textColor=DARK, leading=24, spaceAfter=15)
    ))
    story.append(Paragraph(
        "O uso de IA acelerou identificação de padrões e geração de código, "
        "mas a decisão analítica e a interpretação de negócio foram humanas.",
        ParagraphStyle("concc", fontSize=14, textColor=GRAY, leading=20)
    ))

    # -----------------------------------------------------------------------
    # Gera o PDF
    # -----------------------------------------------------------------------
    doc = SimpleDocTemplate(
        path,
        pagesize=landscape(A4),
        leftMargin=30 * mm,
        rightMargin=30 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        title="Inteligência de Pipeline RevOps",
        author="Case Técnico",
    )
    
    # Custom background
    def add_background(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(BG)
        canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        canvas.restoreState()

    doc.build(story, onFirstPage=add_background, onLaterPages=add_background)
    print(f"[presentation] PDF gerado: {path}")
