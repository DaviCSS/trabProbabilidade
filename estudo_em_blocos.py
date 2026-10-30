"""Roteiro do trabalho para executar em blocos no VS Code ou no Spyder.

No VS Code, instale as extensoes Python e Jupyter. O marcador # %%
cria uma celula executavel: clique em "Run Cell" acima de cada bloco.

Tambem funciona como script comum: python estudo_em_blocos.py
Use as celulas na ordem, pois alguns experimentos reutilizam resultados.
"""

# %% 1 - IMPORTACOES E REGRAS DO MODELO
import random
from maquina import (
    SIMBOLOS, PAGAMENTOS, mostrar_rodada, rodada, simular_rodadas,
    experimento_1, experimento_2, experimento_3,
    experimento_4, experimento_5, executar_todos,
)

print("Simulador acadêmico - somente créditos fictícios")
print("Símbolos:", SIMBOLOS)
print("Pagamentos:", PAGAMENTOS)
print("Aposta fixa: 1 crédito fictício")

# %% 2 - UMA RODADA (VISUALIZAR O TABULEIRO 3 x 3)
# O gerador recebe a semente apenas uma vez, ANTES de sortear.
gerador = random.Random(2026)
resultado = rodada(gerador)
mostrar_rodada(resultado)

# %% 3 - CONTAS TEORICAS (SEM SIMULACAO)
resultados_possiveis = 5 ** 3
triplas_premiadas = 5
probabilidade_premio = triplas_premiadas / resultados_possiveis
premio_esperado = sum(PAGAMENTOS.values()) / resultados_possiveis
lucro_esperado = premio_esperado - 1
print("Resultados centrais possíveis:", resultados_possiveis)
print("Chance de prêmio:", f"{100 * probabilidade_premio:.1f}%")
print("Prêmio médio teórico:", f"{premio_esperado:.3f}")
print("Lucro médio teórico:", f"{lucro_esperado:.3f}")
print("RTP teórico:", f"{100 * premio_esperado:.1f}%")

# %% 4 - EXPERIMENTO 1: FREQUENCIAS DE 10.000 RODADAS
# A mesma lista e reaproveitada nos experimentos 2, 4 e 5.
rodadas_2026 = simular_rodadas(10000, 2026)
resumo_1, frequencias_1 = experimento_1(rodadas_2026)
for item in frequencias_1:
    print(item["resultado"], "->", item["contagem"], "ocorrências")
print("Lucro médio:", round(resumo_1["lucro_medio"], 4))
print("RTP observado:", round(100 * resumo_1["rtp_observado"], 2), "%")
print("Desvio-padrão amostral:", round(resumo_1["desvio_amostral"], 4))

# %% 5 - EXPERIMENTO 2: LEI DOS GRANDES NUMEROS
resumo_2, curvas_2 = experimento_2(rodadas_2026)
for item in resumo_2["medias"]:
    print("Semente", item["semente"], "em", item["rodadas"],
          "rodadas -> lucro médio", round(item["lucro_medio_acumulado"], 4))
print("Dez primeiros resultados reproduzidos:",
      resumo_2["primeiros10_reproduzidos"])

# %% 6 - EXPERIMENTO 3: 100 PARTICIPANTES, SALDO LIMITADO
# O gerador nao e reiniciado a cada participante (semente 42).
resumo_3, trajetorias_3 = experimento_3()
print("Ganho:", round(100 * resumo_3["ganho"], 1), "%")
print("Empate:", round(100 * resumo_3["empate"], 1), "%")
print("Perda:", round(100 * resumo_3["perda"], 1), "%")
print("Esgotamento:", round(100 * resumo_3["esgotamento"], 1), "%")
print("Saldo médio:", round(resumo_3["saldo_medio"], 2))
print("Saldo mediano:", round(resumo_3["saldo_mediano"], 2))

# %% 7 - EXPERIMENTO 4: CHANCE APOS PERDER OU GANHAR
# Usamos os 9.999 pares consecutivos do Experimento 1.
resultados_4 = experimento_4(rodadas_2026)
for item in resultados_4:
    print(item["resultado_anterior"], "->", item["total_pares"], "pares;",
          item["premios_rodada_seguinte"], "prêmios seguintes;",
          "proporção:", item["proporcao"])
print("Referência teórica em ambos os casos: 4%")

# %% 8 - EXPERIMENTO 5: PREMIOS 10% MAIORES, MESMOS SORTEIOS
resultados_5 = experimento_5(rodadas_2026)
for item in resultados_5:
    print(item["tabela"], "-> RTP teórico",
          f"{100 * item['rtp_teorico']:.1f}%", "| RTP observado",
          f"{100 * item['rtp_observado']:.2f}%")

# %% 9 - GERAR TODOS OS GRAFICOS E EXTRAS (OPCIONAL)
# Descomente as duas linhas abaixo para exportar novamente todos os arquivos.
# Precisa ter instalado: pip install -r requirements.txt
# dados = executar_todos()
# from gerar_relatorio import relatorio, divulgacao
# relatorio()
# divulgacao()

print("\nCélulas concluídas. Os CSV dos cinco experimentos estão em resultados/.")
