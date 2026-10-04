# tcc-ia-code-smells-analysis
Análise comparativa de code smells: IA Gratuita vs IA Paga - TCC

## Gerar as visualizações

Os dados de entrada estão em `data/code_smells.csv`. Para gerar os oito gráficos/tabela em `figures/`:

```bash
python -m pip install -r requirements.txt
python scripts/gerar_graficos.py
```

Para escolher outro diretório de saída:

```bash
python scripts/gerar_graficos.py --output-dir /caminho/para/figuras
```

As imagens em PNG são exportadas em 300 dpi. O total geral soma somente os valores de
“Code Smells Individuais” (87 gratuitos e 193 pagos); os 43 smells do projeto base são
mostrados como referência e não são somados aos resultados das IAs. A densidade é calculada
como smells individuais por 1.000 linhas.

A diversidade de tipos não pode ser calculada com os dados atuais: eles não informam quais
tipos de smells foram encontrados. O gráfico correspondente documenta essa limitação; não
foram estimadas contagens ausentes. As diferentes variantes permanecem separadas nos gráficos,
e não há comparação pareada onde os dados não fornecem uma variante equivalente.

Os testes focados usam somente a biblioteca padrão:

```bash
python -m unittest discover -s tests
```
