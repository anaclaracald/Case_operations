"""
report_errors.py — Gera o relatorio_erros.html com os problemas encontrados.
"""

import os
import pandas as pd
from jinja2 import Template
from src.config import REPORT_ERRORS_PATH


TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Relatório de Erros — Case RevOps Monks</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    --primary: #8B5CF6;
    --primary-light: #EBE4FF;
    --secondary: #FBE122;
    --dark: #1A1528;
    --gray: #6B7280;
    --bg: #F8F7FB;
    --white: #FFFFFF;
    --border: #E5E7EB;
    --shadow: 0 10px 25px rgba(0,0,0,0.05);
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--dark); line-height: 1.6; }
  h1, h2, h3, h4, h5, h6 { font-family: 'Poppins', sans-serif; color: var(--dark); }
  
  header {
    padding: 60px 40px 20px; max-width: 1200px; margin: 0 auto;
    display: flex; justify-content: space-between; align-items: flex-end;
  }
  header h1 { font-size: 48px; font-weight: 800; line-height: 1.1; max-width: 600px; }
  header p { font-size: 16px; color: var(--gray); max-width: 400px; text-align: right; }
  
  .container { max-width: 1200px; margin: 0 auto; padding: 20px 40px 60px; }
  
  /* Executive Summary */
  .summary-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 24px; margin-bottom: 40px;
  }
  .stat-card {
    border-radius: 24px; padding: 30px;
    box-shadow: var(--shadow);
    display: flex; flex-direction: column; justify-content: center;
  }
  .stat-card.purple { background: var(--primary); color: white; }
  .stat-card.yellow { background: var(--secondary); color: var(--dark); }
  .stat-card .number { font-size: 36px; font-weight: 800; font-family: 'Poppins', sans-serif; margin-bottom: 8px; }
  .stat-card .label { font-size: 14px; font-weight: 500; opacity: 0.9; }
  
  /* Summary Table */
  .summary-table-wrap { background: var(--white); border-radius: 24px; padding: 32px; box-shadow: var(--shadow); margin-bottom: 40px; }
  .summary-table-wrap h2 { font-size: 24px; font-weight: 700; margin-bottom: 20px; }
  table { width: 100%; border-collapse: collapse; font-size: 14px; }
  th { background: var(--primary); color: white; padding: 14px; text-align: left; font-weight: 600; border-radius: 8px; }
  tr:nth-child(even) td { background: var(--bg); }
  td { padding: 12px 14px; border-bottom: 1px solid var(--border); vertical-align: top; }
  
  /* Category Sections */
  .category-section {
    background: var(--white); border-radius: 24px; padding: 32px;
    box-shadow: var(--shadow); margin-bottom: 32px;
  }
  .category-header {
    display: flex; align-items: center; gap: 16px; margin-bottom: 20px;
  }
  .count-badge {
    background: var(--secondary); color: var(--dark);
    padding: 6px 16px; border-radius: 20px; font-size: 13px; font-weight: 700;
  }
  .count-badge.ok { background: var(--primary-light); color: var(--primary); }
  .category-section h3 { font-size: 20px; font-weight: 700; }
  
  .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin: 24px 0; }
  @media(max-width:640px) { .info-grid { grid-template-columns: 1fr; } }
  
  .info-box {
    background: var(--bg); border-radius: 16px; padding: 20px;
  }
  .info-box .box-label { font-size: 12px; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase; color: var(--primary); margin-bottom: 8px; }
  .info-box p { font-size: 14px; color: var(--dark); font-weight: 500; }
  
  .examples-table { margin-top: 24px; overflow-x: auto; }
  .examples-table caption { font-size: 14px; color: var(--gray); margin-bottom: 12px; text-align: left; font-weight: 600; }
  
  footer { text-align: center; padding: 32px; color: var(--gray); font-size: 13px; }
</style>
</head>
<body>

<header>
  <h1>Relatório de Auditoria<br>de Qualidade de Dados</h1>
  <p>Acompanhando performance. Gerando resultados.<br><strong>opps_corrupted.xlsx</strong></p>
</header>

<div class="container">

  <!-- Executive Summary -->
  <div class="summary-grid">
    <div class="stat-card purple">
      <div class="number">{{ total_rows }}</div>
      <div class="label">Linhas brutas</div>
    </div>
    <div class="stat-card yellow">
      <div class="number">{{ total_categories }}</div>
      <div class="label">Categorias de problemas</div>
    </div>
    <div class="stat-card purple">
      <div class="number">{{ total_affected }}</div>
      <div class="label">Linhas com problemas</div>
    </div>
    <div class="stat-card yellow">
      <div class="number">{{ unique_deals }}</div>
      <div class="label">Deals únicos</div>
    </div>
    <div class="stat-card purple">
      <div class="number">{{ out_of_scope }}</div>
      <div class="label">Registros fora de escopo</div>
    </div>
  </div>

  <!-- Summary Table -->
  <div class="summary-table-wrap">
    <h2>Resumo Executivo por Categoria</h2>
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Categoria de Problema</th>
          <th>Linhas Afetadas</th>
          <th>Correção</th>
        </tr>
      </thead>
      <tbody>
        {% for r in results %}
        <tr>
          <td>{{ loop.index }}</td>
          <td><strong>{{ r.category }}</strong></td>
          <td>
            {% if r.count == 0 %}
              <span class="count-badge ok">✓ Nenhum</span>
            {% else %}
              <span class="count-badge">{{ r.count }}</span>
            {% endif %}
          </td>
          <td style="font-size:13px;">{{ r.correction }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>

  <!-- Per-category sections -->
  {% for r in results %}
  <div class="category-section">
    <div class="category-header">
      <h3>{{ loop.index }}. {{ r.category }}</h3>
      {% if r.count == 0 %}
        <span class="count-badge ok">✓ Sem problemas</span>
      {% else %}
        <span class="count-badge">{{ r.count }} linhas afetadas</span>
      {% endif %}
    </div>

    <div class="info-grid">
      <div class="info-box">
        <div class="box-label">🏢 Em linguagem de negócio</div>
        <p>{{ r.business_explanation }}</p>
      </div>
      <div class="info-box">
        <div class="box-label">✅ Correção aplicada</div>
        <p>{{ r.correction }}</p>
      </div>
    </div>

    {% if r.examples_html %}
    <div class="examples-table">
      <caption>Exemplos reais da planilha (até 10 linhas)</caption>
      {{ r.examples_html }}
    </div>
    {% endif %}
  </div>
  {% endfor %}

</div>
<footer>
  Gerado automaticamente pelo pipeline de auditoria — Case RevOps Monks · 2026
</footer>
</body>
</html>
"""


def _df_to_html(df: pd.DataFrame) -> str:
    if df is None or len(df) == 0:
        return ""
    return df.to_html(
        index=False,
        classes="",
        border=0,
        escape=True,
    )


def generate_error_report(
    validation_results: list,
    total_rows: int,
    unique_deals: int,
    out_of_scope: int,
    path: str = REPORT_ERRORS_PATH,
) -> None:
    """
    Gera o relatório HTML de erros.
    """
    enriched = []
    total_affected = 0
    for r in validation_results:
        count = r.get("count", 0)
        total_affected += count
        examples_df = r.get("examples")
        enriched.append({
            "category": r["category"],
            "count": count,
            "description": r.get("description", ""),
            "business_explanation": r.get("business_explanation", ""),
            "correction": r.get("correction", ""),
            "examples_html": _df_to_html(examples_df) if examples_df is not None else "",
        })

    template = Template(TEMPLATE)
    html = template.render(
        total_rows=total_rows,
        total_categories=len(enriched),
        total_affected=total_affected,
        unique_deals=unique_deals,
        out_of_scope=out_of_scope,
        results=enriched,
    )

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[report_errors] Relatório gerado: {path}")
