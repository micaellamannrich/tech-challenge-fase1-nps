# Tech Challenge Fase 1 · Case NPS Preditivo

Projeto da Pós Tech em AI Scientist (FIAP), Tech Challenge da Fase 1.

## Objetivo do projeto

Este projeto atende um e-commerce que cresceu rápido e passou a processar muito mais pedidos, entregas e atendimentos. O NPS varia entre clientes com indicadores operacionais parecidos, e a empresa não sabe quais fatores operacionais explicam essa variação.

A empresa coleta o NPS só no fim da jornada de compra, então descobre a insatisfação depois que o problema já aconteceu, sem chance de agir antes. A pergunta central: quais fatores operacionais influenciam a satisfação do cliente, e como a empresa pode agir antes da pesquisa de NPS?

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

[`notebooks/01_exploracao_dados.ipynb`](notebooks/01_exploracao_dados.ipynb) tem 13 seções: tamanho e tipos da base, valores ausentes e duplicados, resumo estatístico, distribuição e cálculo do NPS, outliers, variáveis de entrega e atendimento, NPS por região, coerência entre colunas, correlações com o NPS, tempo real de entrega, ponto de ruptura, pricing e perfil do cliente, e resumo de decisões.

Principais decisões e achados:

- NPS da empresa: -74,1 (2.001 detratores, 351 passivos, 148 promotores), calculado com `.round()` do pandas e faixas clássicas.
- O atraso na entrega (`delivery_delay_days`) pesa mais na nota: correlação de -0,60. Reclamações vêm em seguida (-0,50), depois contatos com atendimento (-0,35). O prazo estimado (`delivery_time_days`) não tem relação com a nota (correlação 0,00).
- `csat_internal_score` e `repeat_purchase_30d` ficam fora do modelo por risco de vazamento.
- O projeto trata `complaints_count` como uma métrica que inclui `customer_service_contacts` mais reclamações de outros canais. Essa é uma premissa assumida, não confirmada pelo dicionário de dados.
- Pricing (valor do pedido, desconto, frete) e perfil do cliente (idade, tempo de casa) não correlacionam com a nota, todos entre -0,04 e 0,04.

### 2. Modelagem preditiva

[`notebooks/02_modelagem.ipynb`](notebooks/02_modelagem.ipynb) usa regressão linear (`sm.OLS` e `LinearRegression`) para estimar a nota de NPS.

- O primeiro ajuste usa 12 variáveis (todas as não vazadas, exceto `customer_region`). O ajuste reduzido usa 3 variáveis (`delivery_delay_days`, `complaints_count`, `resolution_time_days`). As 3 variáveis sozinhas explicam quase o mesmo que as 12: R² de 0,546 contra 0,550.
- A separação treino e teste usa 80/20 (`random_state=42`). No teste: MAE 1,340, MSE 2,847, RMSE 1,687, R² 0,550. Os números de treino ficam quase iguais, sem sinal de overfitting.
- `customer_region` fica fora do modelo, porque o projeto não testou nenhuma codificação de variável categórica.
- Recomendação: invista primeiro na logística de entrega, já que o atraso tem o maior peso no modelo (coeficiente -0,91). Para confirmar se reduzir o atraso melhora a nota, a empresa precisa de um teste controlado (teste A/B), que esta análise observacional não cobre.

## Como reproduzir os resultados

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\jupyter notebook notebooks/01_exploracao_dados.ipynb
.venv\Scripts\jupyter notebook notebooks/02_modelagem.ipynb
```

Os notebooks leem `data/01_raw/desafio_nps_fase_1.csv` e rodam do início ao fim. Nenhuma dependência externa além das listadas em `requirements.txt`. O notebook de modelagem só depende do CSV, não do notebook de exploração.
