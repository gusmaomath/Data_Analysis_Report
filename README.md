# Desenvolvimento do 2º Checkpoint - Data Science & Statistical Computing
![Badge Concluido](https://img.shields.io/badge/STATUS-CONCLUIDO-GREEN)

**Nomes + RM dos integrantes:**
- Júlia Marques - 98680
- Matheus Gusmão - 550826
- Guilherme Morais - 551981

**Turma:** 2ESPW

**Ano:** 2024
___
## Descrição do Projeto
Este projeto é uma ferramenta para gerar relatórios HTML de análise de dados a partir de um `DataFrame` do Pandas. Ele oferece estatísticas descritivas, gráficos de distribuição e análise de correlação para as colunas do conjunto de dados, facilitando a análise exploratória de dados.

Como base de teste do script foi usado o dataset "sabrina_carpenter_discography.csv" retirado do site kaggle
> Fonte: https://www.kaggle.com/datasets/delfinaoliva/sabrina-carpenter-discography?resource=download

___
##Funcionamento
- Geração automática de relatórios HTML com:
  - Informações gerais sobre o conjunto de dados (formato, linhas duplicadas, valores ausentes).
  - Análise descritiva para cada coluna.
  - Histogramas para colunas numéricas e gráficos de barras para colunas categóricas.
  - Análise de correlação entre variáveis numéricas.
- Uso de bibliotecas populares de visualização de dados, como `matplotlib` e `seaborn`.
- Interface interativa no relatório gerado, com navegação entre as análises das colunas.

___
## Como executar o projeto
Antes de executar o script, certifique-se de que as bibliotecas necessárias estão instaladas:

- Python 3.7 ou superior
- Pandas
- Matplotlib
- Seaborn

Você pode instalar essas dependências com:

```bash
pip install pandas matplotlib seaborn base64 BytesIO
```
## Analisando seu DataFrame:

Você pode adicionar ao código o dataframe escolhido:
```
# Carregue seu DataFrame
df = pd.read_csv("seu_arquivo.csv")
```
## Executando o relatório
Para utilizar o codigo basta adicionar a linha abaixo no final do script e executar:
```
generate_html_analysis(df, output_html="output.html", max_categories=10)
```
> O parametro "max_categories=10" é o volume de dados que voce deseja ver
_____
