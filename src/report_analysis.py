"""
report_analysis.py — Gera o analise.html com todos os gráficos e tabelas de negócio.
"""

import os
from jinja2 import Template
from src.config import REPORT_ANALYSIS_PATH

TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Análise de Pipeline — Case RevOps Monks</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
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

  /* KPI Cards */
  .kpi-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 24px; margin-bottom: 40px;
  }
  .kpi-card {
    border-radius: 24px; padding: 30px;
    box-shadow: var(--shadow);
    display: flex; flex-direction: column; justify-content: center;
  }
  .kpi-card.purple { background: var(--primary); color: white; }
  .kpi-card.yellow { background: var(--secondary); color: var(--dark); }
  .kpi-card .kpi-value { font-size: 32px; font-weight: 800; font-family: 'Poppins', sans-serif; margin-bottom: 8px; }
  .kpi-card .kpi-label { font-size: 14px; font-weight: 500; opacity: 0.9; }

  /* Chart Sections */
  .chart-section {
    background: var(--white); border-radius: 24px; padding: 32px;
    box-shadow: var(--shadow); margin-bottom: 32px;
  }
  .chart-section h2 { font-size: 24px; font-weight: 700; margin-bottom: 20px; }
  .observation {
    background: var(--primary-light); color: var(--dark);
    padding: 16px 20px; border-radius: 12px;
    font-size: 14px; margin-top: 20px; font-weight: 500;
  }

  nav {
    max-width: 1200px; margin: 0 auto; padding: 0 40px 20px;
    display: flex; gap: 10px; flex-wrap: wrap;
  }
  nav a {
    background: var(--white); color: var(--dark); text-decoration: none; font-size: 13px;
    padding: 8px 16px; border-radius: 20px; font-weight: 600;
    box-shadow: 0 4px 10px rgba(0,0,0,0.02); transition: all 0.2s;
  }
  nav a:hover { background: var(--primary); color: white; }

  footer { text-align: center; padding: 32px; color: var(--gray); font-size: 13px; }

  table { width: 100%; border-collapse: collapse; font-size: 14px; margin-top: 12px; }
  th { background: var(--primary); color: white; padding: 14px; text-align: left; font-weight: 600; border-radius: 8px; }
  tr:nth-child(even) td { background: var(--bg); }
  td { padding: 12px 14px; border-bottom: 1px solid var(--border); }
</style>
</head>
<body>

<header>
  <h1>Relatório Estratégico<br>de KPIs</h1>
  <p>Acompanhando performance. Gerando resultados.<br>Data de Referência: <strong>{{ reference_date }}</strong></p>
</header>

<nav>
  {% for s in sections %}
  <a href="#section-{{ loop.index }}">{{ s.short_title }}</a>
  {% endfor %}
</nav>

<div class="container">

  <!-- KPIs -->
  <div class="kpi-grid">
    {% for kpi in kpis %}
    <div class="kpi-card {% if loop.index is odd %}purple{% else %}yellow{% endif %}">
      <div class="kpi-value">{{ kpi.value }}</div>
      <div class="kpi-label">{{ kpi.label }}</div>
    </div>
    {% endfor %}
  </div>

  <!-- Sections -->
  {% for s in sections %}
  <div class="chart-section" id="section-{{ loop.index }}">
    <h2>{{ s.title }}</h2>
    {{ s.chart_html }}
    <div class="observation">💡 {{ s.observation }}</div>
  </div>
  {% endfor %}

</div>
<footer>
  Gerado automaticamente pelo pipeline de análise — Case RevOps Monks · 2026
</footer>
</body>
</html>
"""


def generate_analysis_report(
    sections: list,
    kpis: list,
    reference_date: str,
    path: str = REPORT_ANALYSIS_PATH,
) -> None:
    """
    Gera o relatório HTML de análise.
    """
    template = Template(TEMPLATE)
    html = template.render(
        sections=sections,
        kpis=kpis,
        reference_date=reference_date,
    )
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[report_analysis] Relatório gerado: {path}")
