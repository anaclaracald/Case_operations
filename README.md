# Case RevOps — Monks

## Objetivo

Solução completa ao case técnico do processo seletivo de Estágio em Operations da Monks.

O projeto audita, limpa e analisa uma planilha de 413 linhas de oportunidades comerciais (estrutura real de CRM/Salesforce, dados anonimizados), gerando três entregáveis finais: relatório de erros, relatório de análise e apresentação executiva.

---

## Estrutura do Projeto

```
case-revops/
├── data/
│   ├── raw/
│   │   └── opps_corrupted.xlsx          # planilha original (não modificada)
│   └── processed/
│       └── opps_corrigido.xlsx          # saída após limpeza e normalização
│
├── reports/
│   ├── relatorio_erros.html             # Parte 1: auditoria de qualidade
│   ├── analise.html                     # Parte 2: 10 análises de negócio
│   └── apresentacao.pdf                 # Parte 3: slides executivos
│
├── src/
│   ├── config.py          # constantes, listas canônicas, mapeamentos
│   ├── load_data.py       # leitura da planilha bruta
│   ├── validation.py      # detecção de problemas de qualidade
│   ├── cleaning.py        # aplicação das correções
│   ├── normalization.py   # colunas derivadas (Lead_Source_Category, datas, etc.)
│   ├── analysis.py        # cálculo das 10 métricas de negócio
│   ├── visualizations.py  # geração de gráficos com Plotly
│   ├── report_errors.py   # gerador de relatorio_erros.html
│   ├── report_analysis.py # gerador de analise.html
│   └── presentation.py    # gerador de apresentacao.pdf
│
├── main.py                # orquestrador — executa o pipeline completo
├── requirements.txt
└── README.md
```

---

## Como Executar

### 1. Instale as dependências

```bash
pip install -r requirements.txt
```

> **Nota sobre WeasyPrint**: a geração do PDF requer WeasyPrint, que por sua vez precisa de bibliotecas de sistema (`pango`, `cairo`, `gdk-pixbuf`). Se a instalação falhar, o pipeline salva automaticamente um arquivo `apresentacao_slides.html` que pode ser impresso como PDF pelo browser.
>
> **Mac**: `brew install pango cairo gdk-pixbuf libffi && pip install weasyprint`

### 2. Execute o pipeline completo

```bash
cd case-revops
python main.py
```

Para pular a geração do PDF:

```bash
python main.py --skip-pdf
```

### 3. Abra os relatórios

```
reports/relatorio_erros.html   → abra no browser
reports/analise.html           → abra no browser
reports/apresentacao.pdf       → abra com qualquer leitor de PDF
```

---

## Principais Decisões Técnicas

### Granularidade: produto vs. deal
A planilha é exportada em nível de produto — um deal pode ter múltiplas linhas. Toda contagem de oportunidades e cálculo de Amount é feita após **deduplicação por `Opportunity_ID`** (`drop_duplicates(subset='Opportunity_ID', keep='first')`).

**Por que `keep='first'`**: os campos de deal (Amount, Stage, Lead_Source, etc.) são repetidos identicamente em todas as linhas de produto de um mesmo deal. O `first` garante uma linha por deal sem perda de informação. A soma de `Total_Product_Amount` é calculada separadamente antes da deduplicação.

### Amount como campo derivado
Quando `Amount` diverge da soma de `Total_Product_Amount`, o `Amount` é recalculado. A exceção são estágios iniciais (`Opportunity Identified`, `Qualified`), onde campos em branco são comportamento esperado (deal ainda não escopado).

### Taxonomia de Lead_Source
A normalização ocorre em duas camadas:
1. **Valor bruto → Canônico**: strip + lowercase + lookup em dicionário (config.py)
2. **Canônico → Categoria**: 6 categorias conforme case.md

⚠️ **Atenção especial**: `Inbound Current Client (DEPRECATED)` → `Customer Success` (não Inbound), pois representa expansão em cliente existente.

### Registros fora de escopo
Types `Retainer`, `Passthrough`, `Flex/Renewal` são **marcados** com `in_scope=False` na planilha corrigida, mas não removidos. As análises filtram apenas `in_scope=True`.

---

## Suposições Adotadas

| Suposição | Justificativa |
|---|---|
| Identificador de deal = `Opportunity_ID` | Confirmado na inspeção dos dados |
| `Closed Lost` não existe no dataset | Não foi encontrado na inspeção; se existir, entra no denominador do win rate mas não no numerador |
| Data de referência para YTD = `2026-04-29` | Data de execução do projeto |
| Tolerância de R$ 0,50 para divergência de Amount | Evita falsos positivos por arredondamento de ponto flutuante |
| Oportunidades sem `Close_Date` em 2026 são excluídas do MoM 2026 | Apenas Closed Won com ano 2026 entram na análise temporal |

---

## Como a IA Foi Usada

Este projeto usou **Claude (Anthropic)** como parceiro de desenvolvimento ao longo de todo o processo:

- **Inspeção inicial**: identificação dos padrões de erro na planilha (typos, formatos)
- **Geração de código**: todos os módulos Python foram gerados iterativamente com Claude
- **Decisões de limpeza**: discussão sobre a estratégia de deduplicação e tratamento de nulos
- **Observações de negócio**: interpretações dos gráficos refinadas com auxílio da IA
- **Estrutura modular**: arquitetura de pipeline definida em conjunto
- **Pensamento analítico**: análise do resultado de prompts, checar a realização e execução para corresponder com as expectativas do projeto

A IA não foi usada para interpretar os dados de forma isolada — todas as decisões analíticas foram validadas contra as regras do `case.md` e da desenvolvedora.

---

## Entregáveis Finais

| Arquivo | Descrição |
|---|---|
| `data/processed/opps_corrigido.xlsx` | Planilha limpa com colunas adicionais (`in_scope`, `Lead_Source_Category`, `data_quality_flag`) |
| `reports/relatorio_erros.html` | Relatório de auditoria: 9 categorias de problemas, exemplos reais, correções aplicadas |
| `reports/analise.html` | 10 análises de negócio com gráficos interativos (Plotly) e observações |
| `reports/apresentacao.pdf` | 8 slides executivos para liderança de Operations |
