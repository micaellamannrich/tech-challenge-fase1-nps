# Tech Challenge Fase 1 · Case NPS Preditivo

Projeto da Pós Tech em AI Scientist (FIAP), Tech Challenge da Fase 1.

## Objetivo do projeto

Este projeto atende um e-commerce que cresceu rápido e passou a processar muito mais pedidos, entregas e atendimentos. O NPS varia entre clientes com indicadores operacionais parecidos, e a empresa não sabe quais fatores operacionais explicam essa variação.

A empresa coleta o NPS só no fim da jornada de compra, então descobre a insatisfação depois que o problema já aconteceu, sem chance de agir antes. A pergunta central: quais fatores operacionais influenciam a satisfação do cliente, e como a empresa pode agir antes da pesquisa de NPS?

## Principais resultados

- NPS da empresa: **-74,1** (80% detratores, 14% passivos, 6% promotores).
- Os três fatores que mais pesam na nota, nesta ordem: **atraso na entrega** (correlação -0,60), **número de reclamações** (-0,50) e **contatos com o atendimento** (-0,35).
- O tempo total de entrega não muda a nota (correlação 0,00). O que pesa é atrasar em relação ao prometido, não a duração da entrega em si.
- Ponto de ruptura: a cada dia de atraso, a chance de o pedido ser de um detrator sobe rápido. De 45,1% sem atraso para 83,1% com 2 dias de atraso e 100% a partir de 5 dias.
- Pricing (valor do pedido, desconto, frete) e perfil do cliente (idade, tempo de casa, região) não têm relação com a nota.

| Modelo | Pergunta que responde | Resultado no teste |
|---|---|---|
| Regressão linear | Qual a nota exata de NPS? | R² = 0,550, MAE = 1,34 |
| Regressão logística | Este pedido vira um detrator? | ROC-AUC = 0,882, recall = 0,941 |

## Definição da target

**Qual variável representa a satisfação do cliente?**
`nps_score`, a nota de 0 a 10 que o cliente dá depois da compra.

**Por que ela foi escolhida?**
É a única medida de satisfação que vem direto do cliente. `csat_internal_score` é um indicador interno da empresa, não a resposta do cliente, por isso não serve como alvo. Ele entra como possível preditor, com risco de vazamento (veja abaixo).

**Em que momento da jornada é coletada?**
No fim, depois que a compra já aconteceu. Esse é o problema central do case: a empresa só descobre a insatisfação depois que ela ocorre.

**Existe risco de usar essa variável de forma inadequada?**
Sim, quatro riscos:

1. A nota é decimal, não inteira, e a classificação clássica (detrator, passivo, promotor) depende de uma regra de arredondamento. Regras diferentes mudam o NPS reportado de -74,1 a -80,0, então o número depende de uma escolha metodológica explícita.
2. As classes são desbalanceadas: 80% dos clientes são detratores. Um modelo de classificação binária que sempre aposta em "detrator" acerta 80% sem aprender nada.
3. `csat_internal_score` e `repeat_purchase_30d` correlacionam fortemente com a nota, mas a empresa pode medi-los junto ou depois da pesquisa de NPS. Usá-los para prever o NPS seria usar a resposta para prever a própria resposta.
4. A base não explica por que a nota tem casas decimais. Essa é uma limitação registrada, não escondida.

## Descrição da base de dados

O arquivo `data/01_raw/desafio_nps_fase_1.csv` tem 2.500 pedidos e 19 colunas, sem valores ausentes nem duplicados.

O dicionário completo de colunas está em [`docs/material-curso`](docs/material-curso) e no enunciado ([`docs/Tech Challenge - Enunciado NPS.pdf`](<docs/Tech Challenge - Enunciado NPS.pdf>)).

## Metodologia utilizada

O projeto segue o fluxo CRISP-DM, conforme o roteiro das aulas da Fase 1.

### 1. Exploração dos dados

[`notebooks/01_exploracao_dados.ipynb`](notebooks/01_exploracao_dados.ipynb) tem 13 seções: tamanho e tipos da base, o que a base não conta, valores ausentes e duplicados, resumo estatístico, distribuição e cálculo do NPS, outliers, variáveis de entrega e atendimento, NPS por região (com teste ANOVA), coerência entre colunas, correlações com o NPS, tempo real de entrega, ponto de ruptura, pricing e perfil do cliente, e resumo de decisões.

Decisões que sustentam os resultados acima:

- `csat_internal_score` e `repeat_purchase_30d` ficam fora do modelo por risco de vazamento.
- O projeto trata `complaints_count` como uma métrica que inclui `customer_service_contacts` mais reclamações de outros canais. Essa é uma premissa assumida, não confirmada pelo dicionário de dados.
- O teste ANOVA (F = 0,826, p = 0,508) confirma que a região não explica a variação do NPS.

### 2. Modelagem preditiva

[`notebooks/02_modelagem.ipynb`](notebooks/02_modelagem.ipynb) usa regressão linear (`sm.OLS` e `LinearRegression`) para estimar a nota, e regressão logística (`LogisticRegression`) para classificar detrator ou não.

- O primeiro ajuste da regressão usa 12 variáveis (todas as não vazadas, exceto `customer_region`). O ajuste reduzido usa 3 variáveis (`delivery_delay_days`, `complaints_count`, `resolution_time_days`). As 3 variáveis sozinhas explicam quase o mesmo que as 12: R² de 0,546 contra 0,550.
- Mesmas 3 variáveis e mesma separação treino/teste (80/20, `random_state=42`) na regressão logística.
- `customer_region` fica fora de ambos os modelos, porque o projeto não testou nenhuma codificação de variável categórica.
- O modelo de regressão pode prever notas fora da faixa válida (0 a 10) em cerca de 1% dos casos, uma limitação registrada da regressão linear.
- Recomendação: invista primeiro na logística de entrega, já que o atraso tem o maior peso nos dois modelos. Para confirmar se reduzir o atraso melhora a nota, a empresa precisa de um teste controlado (teste A/B), que esta análise observacional não cobre.

## Como reproduzir os resultados

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\jupyter notebook notebooks/01_exploracao_dados.ipynb
.venv\Scripts\jupyter notebook notebooks/02_modelagem.ipynb
```

Os notebooks leem `data/01_raw/desafio_nps_fase_1.csv` e rodam do início ao fim. Nenhuma dependência externa além das listadas em `requirements.txt`. O notebook de modelagem só depende do CSV, não do notebook de exploração.
