Case Técnico - Processo Seletivo Estágio Operations (Monks)

Obrigado pelo interesse na vaga de estágio em Operations na Monks. Como próxima etapa do processo seletivo, preparamos um case que simula uma tarefa real do nosso time.

O objetivo é entender como você aplica tecnologia e IA para resolver problemas de negócio. Não existe uma única resposta certa – queremos ver como você pensa, como interage com ferramentas de IA e como comunica o que encontrou.

O que você recebe

opps_corrupted.xlsx: planilha com 413 linhas de oportunidades comerciais (dados anonimizados, baseados na nossa estrutura real de CRM).

Este documento: (instruções).

O que você entrega (link público - GitHub, Drive ou similar)

opps_corrigido.xlsx: a planilha após sua limpeza.

relatorio_erros.html: relatório HTML dos problemas encontrados (Parte 1).

analise.html: relatório HTML com a análise dos dados (Parte 2).

apresentacao.pdf: apresentação final (Parte 3).

README.md: explicando como você abordou o problema e um resumo das suas entregas.

Contexto

O time de RevOps trabalha todos os dias com dados de pipeline comercial vindos do Salesforce. Antes de qualquer análise séria, esses dados precisam ser limpos: campos inconsistentes, duplicações, erros de digitação, categorias fora do escopo.

A planilha que enviamos contém ambos os tipos de oportunidade:

Closed Won 2026: negócios já fechados (ganhos) em 2026.

Open Pipeline: negócios em aberto, em diferentes estágios de negociação.

Informações importantes sobre o dataset

Granularidade da tabela. A planilha está exportada em nível de produto. Uma mesma oportunidade pode aparecer em várias linhas (uma para cada produto dentro do deal). Fique atento a isso antes de contar oportunidades.

Campos Amount e Total_Product_Amount. Amount é o valor total da oportunidade; Total_Product_Amount é o valor de cada produto individual. Pode haver divergência entre os dois. Quando isso acontecer, considere que o Amount é o campo com possível erro – a fonte da verdade é a soma dos Total_Product_Amount da oportunidade.

Oportunidades em estágios iniciais (Opportunity Identified ou Qualified) podem legitimamente não ter valor preenchido. Elas podem estar sem Amount, sem Total_Product_Amount e até sem Product_Name porque o deal ainda não foi escopado. Isso não é um erro, é esperado. Se você for fazer análises envolvendo valor, exclua essas oportunidades dessas análises específicas.

Escopo da análise (tipos considerados). Para esta análise, considere apenas oportunidades com os seguintes valores de Type:

Project - Not Competitive

Project - Competitive

Change Order/Upsell

Qualquer outro tipo presente na planilha deve ser excluído da análise.

Taxonomia de Lead_Source (normalização)

A coluna Lead_Source tem muitos valores diferentes, incluindo vários marcados como (DEPRECATED). Para a análise, você deve criar uma coluna nova (ex: Lead_Source_Category) e mapear cada valor bruto para uma das 6 categorias abaixo:

Categoria

Valores brutos de Lead_Source que pertencem a ela

Inbound

Inbound Media. Monks Website (DEPRECATED), Inbound Marketing (DEPRECATED), Inbound Website (DEPRECATED), Marketing Lead Scoring/Nurturing, Website Sales Form

Outbound

Personal Prospecting (DEPRECATED)

Referral

Internal Referral, Referral Personal, Referral S4 Company, Google Referral Partner, Marketing Platform Referral, Google Cloud Partner

Customer Success

Inbound Current Client (DEPRECATED), Existing Client Account/Growth Activity, Current Client Prospecting (DEPRECATED)

Event

Industry Event

Unknown

MH Lead (DEPRECATED), Don't Know/Other (DEPRECATED)

Observação importante: Inbound Current Client (DEPRECATED) é mapeado para Customer Success (não Inbound), porque descreve expansão em cliente existente, não lead novo.

Listas canônicas de referência

Use estas listas como a "verdade" ao verificar se os valores da planilha estão corretos. Qualquer valor que não estiver exatamente em uma destas listas é suspeito e deve ser investigado.

Valores canônicos de Lead_Source (17 valores):

Inbound Current Client (DEPRECATED)

Inbound Website Media. Monks (DEPRECATED)

Inbound Marketing (DEPRECATED)

Inbound Website (DEPRECATED)

Marketing Lead Scoring/Nurturing

Website Sales Form

Prospecting Personal (DEPRECATED)

Prospecting Current Client (DEPRECATED)

Referral Internal

Referral Personal

Referral S4 Company

Referral Partner

Google Marketing Platform Referral

Partner Google Cloud

Existing Client Account/Growth Activity

Industry Event

MH Lead (DEPRECATED)

Don't Know/Other (DEPRECATED)

Valores canônicos de Lead_Office (3 valores):

Sao Carlos, BR

Votorantim, BR

Sao Paulo, BR

Valores canônicos de Stage (7 valores):

Opportunity Identified

Qualified

Registration

Pitching

Pitched

Negotiation

Closed Won

Parte 1 - Auditoria e Limpeza

Construa um script que, com apoio de um modelo de IA (Claude, Gemini, ChatGPT à sua escolha), identifique e explique os problemas de qualidade presentes na planilha.

O que entregar:

opps_corrigido.xlsx: versão corrigida da planilha.

relatorio_erros.html: relatório HTML contendo:

Resumo executivo (quantos problemas encontrados, por categoria).

Para cada categoria de problema: descrição, exemplos reais da planilha, quantas linhas foram afetadas, e o que você fez para corrigir.

Explicação em linguagem natural (escreva para alguém não-técnico).

Exemplos do tipo de problema que você pode encontrar:

Duplicações (relacionadas à granularidade de produto).

Inconsistências de formatação e grafia em campos categóricos (nomes de cidade, estágios, fontes de lead).

Divergências numéricas entre campos relacionados.

Formatos inconsistentes em campos numéricos.

Registros fora do escopo da análise.

Parte 2 - Análise

Usando a planilha já corrigida, produza um relatório HTML (analise.html) contendo os seguintes gráficos e tabelas:

Receita Closed Won MoM: gráfico de barras com a soma de Amount de oportunidades Closed Won, mês a mês em 2026.

Participação % por Lead_Source: gráfico de rosca/pizza mostrando a participação de cada categoria da taxonomia (após normalização) nas oportunidades Closed Won.

Top 10 Oportunidades em Aberto: tabela com as 10 maiores oportunidades em pipeline (por Amount), mostrando: cliente, produto(s), estágio, valor, data esperada de fechamento.

Win rate por Lead_Source: % de Closed Won dentro de cada categoria (considere: Closed Won + Open Pipeline como base).

Ticket médio por Type: valor médio de deal por Type (Project - Competitive vs Project - Not Competitive vs Change Order/Upsell).

Pipeline em aberto por Stage: gráfico de barras com soma de Amount em cada estágio (apenas oportunidades em aberto).

Mix New Business vs Upsell ao longo do tempo: gráfico de barras empilhadas mostrando a proporção entre Project Competitive / Not Competitive (New Business) e Change Order/Upsell por mês de fechamento.

Ciclo de venda médio: dias entre Created_Date e Close_Date para oportunidades Closed Won, agrupado por Lead_Office.

Top 10 clientes Closed Won (YTD): tabela ou barra horizontal com os maiores clientes por valor total fechado em 2026.

Idade do pipeline aberto: histograma dos dias desde Created_Date para oportunidades ainda em aberto.

Nota: Cada gráfico/tabela deve vir acompanhado de uma observação curta (1-2 frases) sobre o que ele mostra.

Parte 3 - Apresentação

Monte uma apresentação (até 8 slides, PDF) que você apresentaria para a liderança do time de Operations. A apresentação deve conter:

Abertura / contexto do case.

Erros encontrados e corrigidos: principais problemas na planilha e o impacto da correção (ex: "após deduplicação, o número de oportunidades caiu de 413 linhas para X deals únicos").

Principais achados da análise: 3 a 5 insights dos dados limpos.

Recomendação de processo: como você preveniria esses problemas no futuro? Que processo, alerta ou ferramenta você sugeriria?

Conclusão: o que você aprendeu fazendo este case.

Como avaliamos

Critério

O que olhamos

Resultados obtidos interagindo com IA

Qualidade dos outputs que você conseguiu gerar usando IA, clareza da sua interação com a ferramenta, e capacidade de identificar quando não usar IA.

Qualidade da limpeza

Quantos tipos de problemas você detectou, se a explicação é clara, se as correções fazem sentido.

Rigor analítico

Os números batem, os gráficos são apropriados para cada análise, as observações mostram interpretação (não só descrição).

Comunicação final

Apresentação clara e bem priorizada, com linguagem de negócio, síntese boa dos achados mais relevantes, e recomendação acionável.

Dicas

Use IA generativa abertamente. Não estamos avaliando se você consegue resolver tudo sozinho – estamos avaliando como você usa as ferramentas disponíveis. Use Claude, Gemini, ChatGPT, GitHub Copilot – o que preferir.

Quando tiver dúvida sobre algo do negócio, documente sua suposição. Não precisa adivinhar nosso contexto – deixe claro o que você assumiu.

Simplicidade > Complexidade. Um gráfico bem explicado vale mais que 5 visualizações sem conclusão.

Boa sorte!