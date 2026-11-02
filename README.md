# Máquina Estatística — Trabalho I de Probabilidade e Estatística

Simulador acadêmico de máquina de rolos, com **créditos fictícios** e regras públicas, desenvolvido em Python para a disciplina Probabilidade e Estatística I (IFES – Campus Serra, 2026/2).

**Integrantes:** Davi Campos Sutil e Karyna Martins Carbas

## Jogar pelo navegador (GitHub Pages)

**Site do simulador:** https://davicss.github.io/trabProbabilidade/

A versão interativa está em [`docs/`](docs/). É um site estático (HTML, CSS e JavaScript), sem backend, login, instalação ou dinheiro real. Funciona em computador e celular, com:

- Máquina de três rolos (tabuleiro 3 × 3), só com a linha central premiada.
- Botões **Girar 1 vez**, **Simular +10** e **Reiniciar**; interação pelo teclado.
- Saldo fictício inicial de 100 créditos, aposta fixa de 1 crédito e parada quando o saldo chega a zero ou após 500 rodadas. Reiniciar começa outra simulação, não adiciona créditos à sessão anterior.
- Estatísticas, histórico das últimas rodadas, gráfico de saldo e comparação teoria × observação.

O cálculo no navegador usa **Web Crypto**, enquanto o Python usa `random.Random`. Ambos têm as **mesmas regras e probabilidades**, mas não geram a mesma sequência, mesmo se comparados com uma semente numérica. **Os dados da sessão no site não substituem os experimentos reproduzíveis do trabalho**, que ficam no script Python e nos arquivos CSV.

## Jupyter Notebook — execução célula por célula

O arquivo **[`Maquina_Estatistica.ipynb`](Maquina_Estatistica.ipynb)** é um **Jupyter Notebook real**, com células de texto (explicação) e código (execução), tabelas e gráficos **dentro do notebook**. Ele substitui o antigo roteiro com separadores `# %%`.

1. Abra `Maquina_Estatistica.ipynb` no **VS Code (extensões Python e Jupyter)** ou no **Jupyter Notebook / JupyterLab**, ou importe o arquivo no **Google Colab**.
2. Clique em **Executar / Run Cell** na célula **1. Preparação**. Ela define as funções simples usadas pelos experimentos.
3. A partir daí, execute **qualquer experimento (1 a 5) separadamente**, na ordem que quiser. Cada experimento recria por semente as sequências necessárias; **não depende dos resultados das células anteriores**.
4. Leia a explicação e a interpretação junto de cada resultado. Os gráficos também aparecem no próprio notebook, e tabelas CSV são salvas na pasta `resultados_notebook/`.

É preciso ter o Python com `matplotlib` instalado (`python -m pip install -r requirements.txt`). O notebook é **autossuficiente**, sem depender de importações de `maquina.py`, e também funciona após upload no Colab. Ele já contém saídas executadas como exemplo, mas todas podem ser reproduzidas. A versão de linha de comando `maquina.py` e o site em `docs/` **continuam disponíveis**.

**Testes do projeto:** `python -m unittest discover -s tests -v` (Python), `node --test tests/test_site.mjs` (lógica web).

## Como executar

Tenha Python 3.10 ou superior. No terminal, dentro da pasta deste repositório:

```bash
python -m pip install -r requirements.txt
python maquina.py rodada --semente 2026
python maquina.py todos
python gerar_relatorio.py
python -m unittest discover -s tests -v
```

No Windows, caso `python` não funcione, tente `py` no lugar. A ação `rodada` mostra um tabuleiro 3 × 3, destaca a linha central e informa **prêmio bruto** e **lucro líquido**. `todos` executa os cinco experimentos e a análise de sensibilidade, exporta CSV, gráficos e `resultados/resumo.json`. O último comando executa os testes automatizados. **Não há plataforma comercial, depósitos nem apostas reais.**

## Regras do modelo

- Três rolos circulares A-B-C-D-E, sorteados por `random.Random` uma vez por sequência, com parada de 0 a 4 equiprovável.
- Cada coluna mostra as posições `K`, `(K+1) % 5`, `(K+2) % 5`. Só a linha central paga se as três letras forem iguais.
- Aposta fixa de **1 crédito**. Prêmios: AAA=5, BBB=10, CCC=15, DDD=25, EEE=50; demais combinações=0.
- Espaço amostral central de 125 resultados; 5 resultados premiados. Probabilidade de prêmio = **4%**.
- Prêmio esperado **0,84 crédito**, lucro esperado **−0,16 crédito**, RTP teórico **84%**. Esses valores não são de nenhum jogo comercial.

## Experimentos e arquivos

| Parte | Procedimento | Arquivos principais |
|---|---|---|
| E1 | 10.000 rodadas, semente 2026 | `experimento1_frequencias.csv`, gráfico de barras |
| E2 | 3 sequências, sementes 10/2026/123456; pontos 100/1.000/10.000 | `experimento2_medias.csv`, `experimento2_primeiros10.csv`, gráfico de trajetórias |
| E3 | 100 participantes, saldo 100, limite 500, semente 42 contínua entre pessoas | `experimento3_sessoes.csv`, `experimento3_trajetorias.csv`, gráfico dos cinco primeiros |
| E4 | 9.999 pares consecutivos do E1 | `experimento4_condicionais.csv` |
| E5 | Pagamentos base e +10% **nos mesmos resultados de E1** | `experimento5_tabelas.csv`, gráfico RTP |

Todos os CSV estão em **`resultados/`** e os gráficos em **`resultados/graficos/`**. O arquivo `resultados/resumo.json` traz estatísticas, sementes, versão do Python e versão do matplotlib. Relatório em **`relatorio/relatorio.pdf`**. O relatório é gerado por `gerar_relatorio.py` a partir dos resultados, não possui números digitados manualmente.

## Pontos extras selecionados

Escolhemos **dois extras**, para facilitar a explicação no relatório:

- **Validação automatizada (até 3 pontos):** testes de regras, pagamentos, semente, totais e casos-limite. Executar com `python -m unittest discover -s tests -v`.
- **Análise de sensibilidade (até 3 pontos):** sete cenários de pagamentos; tabela em `resultados/extra_sensibilidade.csv` e gráfico em `resultados/graficos/extra_sensibilidade.png`.

## Método e cuidados de interpretação

`random.Random` utiliza o gerador Mersenne Twister. As sementes não são reiniciadas por rodada. O E2 reaproveita as rodadas do E1, e o E5 usa as mesmas triplas para comparar tabelas. No E3, o gerador permanece no mesmo estado ao passar para o participante seguinte. A taxa de esgotamento é subconjunto das perdas. Nenhum resultado simulado é medida de problemas de saúde ou da situação financeira de famílias brasileiras.

Dados teóricos e experimentais **não precisam coincidir exatamente**. Não selecionar sementes nem excluir rodadas por causa dos resultados. Para nova execução, use versões das bibliotecas indicadas em `requirements.txt` e registre as versões efetivas em `resultados/resumo.json`.

## Transparência do uso de inteligência artificial

Ferramentas de IA foram utilizadas como apoio para **estruturação e implementação das funções, revisão de código, elaboração de testes, organização dos gráficos e da documentação**.
