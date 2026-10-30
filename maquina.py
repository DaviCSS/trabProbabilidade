"""Maquina estatistica do Trabalho I de Probabilidade e Estatistica.

Tudo funciona com creditos FICTICIOS. Sem acesso a sites de apostas.
"""
import argparse
import csv
import json
import math
import platform
import random
import statistics
from pathlib import Path

SIMBOLOS = "ABCDE"
PAGAMENTOS = {"A": 5, "B": 10, "C": 15, "D": 25, "E": 50}
PAGAMENTOS_10 = {letra: valor * 1.10 for letra, valor in PAGAMENTOS.items()}
PAGAMENTOS_MESMA_MEDIA = {letra: 21 for letra in SIMBOLOS}
RESULTADOS = Path(__file__).parent / "resultados"


def rodada(gerador, pagamentos=None):
    """Sorteia tres paradas independentes; devolve tabuleiro, premio e lucro."""
    if pagamentos is None:
        pagamentos = PAGAMENTOS
    paradas = [gerador.randrange(5) for _ in range(3)]
    tabuleiro = [
        [SIMBOLOS[(k + linha) % 5] for k in paradas]
        for linha in range(3)
    ]
    centro = "".join(tabuleiro[1])
    premio = pagamentos[centro[0]] if centro.count(centro[0]) == 3 else 0
    return {
        "paradas": paradas,
        "tabuleiro": tabuleiro,
        "centro": centro,
        "premio": premio,
        "lucro": premio - 1,
    }


def mostrar_rodada(resultado):
    print("Simulador acadêmico - somente créditos fictícios")
    print("        Rolo 1   Rolo 2   Rolo 3")
    for indice, linha in enumerate(resultado["tabuleiro"]):
        marca = " < linha avaliada" if indice == 1 else ""
        print("           " + "        ".join(linha) + marca)
    print("Linha central:", "-".join(resultado["centro"]))
    print("Prêmio bruto:", resultado["premio"], "créditos")
    print("Lucro líquido:", resultado["lucro"], "créditos")


def simular_rodadas(n, semente):
    gerador = random.Random(semente)  # Uma inicializacao por sequencia.
    return [rodada(gerador) for _ in range(n)]


def escrever_csv(nome, colunas, linhas):
    RESULTADOS.mkdir(parents=True, exist_ok=True)
    with (RESULTADOS / nome).open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas)
        escritor.writeheader()
        escritor.writerows(linhas)


def media(lista):
    return sum(lista) / len(lista)


def resumo_rodadas(rodadas, pagamentos=PAGAMENTOS):
    premios = [pagamentos[r["centro"][0]] if len(set(r["centro"])) == 1 else 0
               for r in rodadas]
    lucros = [p - 1 for p in premios]
    return {
        "rodadas": len(rodadas),
        "premios": sum(p > 0 for p in premios),
        "frequencia_premio": sum(p > 0 for p in premios) / len(rodadas),
        "premio_medio": media(premios),
        "lucro_medio": media(lucros),
        "rtp_observado": media(premios),  # Aposta fixa de 1 credito.
        "desvio_amostral": statistics.stdev(lucros),
    }


def experimento_1(rodadas):
    grupos = [("AAA", 4, 1 / 125), ("BBB", 9, 1 / 125),
              ("CCC", 14, 1 / 125), ("DDD", 24, 1 / 125),
              ("EEE", 49, 1 / 125), ("sem premio", -1, 120 / 125)]
    linhas = []
    for nome, lucro, prob in grupos:
        quantidade = sum((r["centro"] == nome if nome != "sem premio"
                          else r["premio"] == 0) for r in rodadas)
        linhas.append({"resultado": nome, "lucro": lucro,
                       "probabilidade_teorica": prob, "contagem": quantidade,
                       "frequencia_relativa": quantidade / len(rodadas)})
    assert sum(linha["contagem"] for linha in linhas) == 10000
    escrever_csv("experimento1_frequencias.csv", list(linhas[0]), linhas)
    return resumo_rodadas(rodadas), linhas


def experimento_2(rodadas_2026):
    registros = []
    trajetorias = {}
    primeiras = [r["centro"] for r in rodadas_2026[:10]]
    replicadas = [r["centro"] for r in simular_rodadas(10000, 2026)[:10]]
    for semente in [10, 2026, 123456]:
        sequencia = rodadas_2026 if semente == 2026 else simular_rodadas(10000, semente)
        acumulado = 0
        curva = []
        for indice, r in enumerate(sequencia, start=1):
            acumulado += r["lucro"]
            curva.append(acumulado / indice)
            if indice in (100, 1000, 10000):
                registros.append({"semente": semente, "rodadas": indice,
                                  "lucro_medio_acumulado": acumulado / indice})
        trajetorias[semente] = curva
    escrever_csv("experimento2_medias.csv", list(registros[0]), registros)
    escrever_csv("experimento2_primeiros10.csv", ["ordem", "centro_original", "centro_repetido"],
                 [{"ordem": i + 1, "centro_original": a, "centro_repetido": b}
                  for i, (a, b) in enumerate(zip(primeiras, replicadas))])
    return {"medias": registros, "primeiros10_reproduzidos": primeiras == replicadas}, trajetorias


def simular_sessoes(semente=42, participantes=100, limite=500,
                     pagamentos=None, saldo_inicial=100):
    """Cada participante usa o mesmo gerador, SEM reinicializar entre pessoas."""
    if pagamentos is None:
        pagamentos = PAGAMENTOS
    gerador = random.Random(semente)
    sessoes, trajetorias = [], []
    for pessoa in range(1, participantes + 1):
        saldo = saldo_inicial
        caminho = [saldo]
        quantidade = 0
        while quantidade < limite and saldo >= 1:
            r = rodada(gerador, pagamentos)
            saldo += r["lucro"]
            quantidade += 1
            caminho.append(saldo)
        sessoes.append({"participante": pessoa, "saldo_final": saldo,
                        "rodadas": quantidade, "esgotou": int(saldo < 1),
                        "resultado": "ganho" if saldo > saldo_inicial else
                                     "empate" if saldo == saldo_inicial else "perda"})
        if pessoa <= 5:
            trajetorias.append(caminho + [saldo] * (limite + 1 - len(caminho)))
    return sessoes, trajetorias


def resumo_sessoes(sessoes):
    total = len(sessoes)
    return {
        "participantes": total,
        "ganho": sum(s["resultado"] == "ganho" for s in sessoes) / total,
        "empate": sum(s["resultado"] == "empate" for s in sessoes) / total,
        "perda": sum(s["resultado"] == "perda" for s in sessoes) / total,
        "esgotamento": sum(s["esgotou"] for s in sessoes) / total,
        "saldo_medio": media([s["saldo_final"] for s in sessoes]),
        "saldo_mediano": statistics.median([s["saldo_final"] for s in sessoes]),
        "rodadas_medias": media([s["rodadas"] for s in sessoes]),
    }


def experimento_3():
    sessoes, trajetorias = simular_sessoes()
    assert len(sessoes) == 100
    assert sum(s["resultado"] in ("ganho", "empate", "perda") for s in sessoes) == 100
    escrever_csv("experimento3_sessoes.csv", list(sessoes[0]), sessoes)
    escrever_csv("experimento3_trajetorias.csv", ["rodada", "p1", "p2", "p3", "p4", "p5"],
                 [dict(rodada=i, **{f"p{j+1}": trajetorias[j][i] for j in range(5)})
                  for i in range(501)])
    return resumo_sessoes(sessoes), trajetorias


def experimento_4(rodadas):
    grupos = {False: {"pares": 0, "premios_seguinte": 0},
              True: {"pares": 0, "premios_seguinte": 0}}
    for anterior, seguinte in zip(rodadas, rodadas[1:]):
        chave = anterior["premio"] > 0
        grupos[chave]["pares"] += 1
        grupos[chave]["premios_seguinte"] += int(seguinte["premio"] > 0)
    linhas = []
    for chave, nome in [(False, "apos perda"), (True, "apos premio")]:
        dados = grupos[chave]
        linhas.append({"resultado_anterior": nome,
                       "total_pares": dados["pares"],
                       "premios_rodada_seguinte": dados["premios_seguinte"],
                       "proporcao": (dados["premios_seguinte"] / dados["pares"]
                                     if dados["pares"] else "nao estimavel")})
    assert sum(l["total_pares"] for l in linhas) == 9999
    escrever_csv("experimento4_condicionais.csv", list(linhas[0]), linhas)
    return linhas


def experimento_5(rodadas):
    linhas = []
    for nome, tabela in [("base", PAGAMENTOS), ("premios_mais_10_porcento", PAGAMENTOS_10)]:
        medidas = resumo_rodadas(rodadas, tabela)
        teoria = sum(tabela.values()) / 125
        linhas.append({"tabela": nome, "probabilidade_premio_teorica": 0.04,
                       "frequencia_premio_observada": medidas["frequencia_premio"],
                       "premio_medio": medidas["premio_medio"],
                       "lucro_medio": medidas["lucro_medio"],
                       "rtp_teorico": teoria, "rtp_observado": medidas["rtp_observado"]})
    assert math.isclose(linhas[1]["rtp_teorico"], 0.924)
    escrever_csv("experimento5_tabelas.csv", list(linhas[0]), linhas)
    return linhas


def extras(rodadas, sessoes_base):
    # IC aproximado bilateral de 95% para a media de 10 mil observacoes independentes.
    medidas = resumo_rodadas(rodadas)
    erro = 1.96 * medidas["desvio_amostral"] / math.sqrt(len(rodadas))
    intervalo = {"metodo": "normal aproximado (1,96 * s / raiz(N))",
                 "N": len(rodadas), "lucro_medio": medidas["lucro_medio"],
                 "limite_inferior": medidas["lucro_medio"] - erro,
                 "limite_superior": medidas["lucro_medio"] + erro}
    escrever_csv("extra_intervalo_confianca.csv", list(intervalo), [intervalo])

    # Soma dos cinco pagamentos permanece 105: o RTP teorico segue em 84%.
    outro, _ = simular_sessoes(pagamentos=PAGAMENTOS_MESMA_MEDIA)
    risco = []
    for nome, tabela, sessoes in [("base", PAGAMENTOS, sessoes_base),
                                  ("mesma_media", PAGAMENTOS_MESMA_MEDIA, outro)]:
        lucros = [tabela[s] - 1 for s in SIMBOLOS] + [-1] * 120
        risco.append({"tabela": nome, "rtp_teorico": sum(tabela.values()) / 125,
                      "desvio_teorico_lucro": statistics.pstdev(lucros),
                      "saldo_medio": resumo_sessoes(sessoes)["saldo_medio"],
                      "saldo_mediano": resumo_sessoes(sessoes)["saldo_mediano"],
                      "esgotamento": resumo_sessoes(sessoes)["esgotamento"]})
    escrever_csv("extra_mesma_media_riscos.csv", list(risco[0]), risco)

    # Duas regras predefinidas: 100 ou 500 rodadas, usando mesmos 100 caminhos potenciais.
    gerador = random.Random(2027)
    exposicao = {100: [], 500: []}
    for pessoa in range(1, 101):
        lucros = [rodada(gerador)["lucro"] for _ in range(500)]
        for limite in (100, 500):
            saldo, n = 100, 0
            for lucro in lucros[:limite]:
                if saldo < 1:
                    break
                saldo += lucro
                n += 1
            exposicao[limite].append({"participante": pessoa,
                                      "saldo_final": saldo, "rodadas": n,
                                      "esgotou": int(saldo < 1),
                                      "resultado": "ganho" if saldo > 100 else
                                      "empate" if saldo == 100 else "perda"})
    comparar = []
    for limite in (100, 500):
        resumo = resumo_sessoes(exposicao[limite])
        comparar.append({"limite_rodadas": limite, **resumo})
    escrever_csv("extra_exposicao.csv", list(comparar[0]), comparar)

    cenarios = []
    for fator in (0.50, 0.75, 1.00, 1.10, 1.20, 1.25, 1.50):
        rtp = 0.84 * fator
        cenarios.append({"fator_pagamento": fator, "rtp_teorico": rtp,
                         "lucro_esperado": rtp - 1, "chance_premio": 0.04})
    escrever_csv("extra_sensibilidade.csv", list(cenarios[0]), cenarios)
    return {"intervalo_confianca": intervalo, "mesma_media": risco,
            "exposicao": comparar, "sensibilidade": cenarios}


def gerar_graficos(tabela1, medias, trajetorias, tabela5, adicionais):
    # Matplotlib e a unica dependencia externa.
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    pasta = RESULTADOS / "graficos"
    pasta.mkdir(parents=True, exist_ok=True)

    def finalizar(nome):
        plt.tight_layout()
        plt.savefig(pasta / nome, dpi=170)
        plt.close()

    rotulos = [linha["resultado"] for linha in tabela1]
    eixos = list(range(len(rotulos)))
    largura = 0.38
    plt.figure(figsize=(8, 4.3))
    plt.bar([p - largura/2 for p in eixos],
            [100*l["probabilidade_teorica"] for l in tabela1], largura, label="Teórica")
    plt.bar([p + largura/2 for p in eixos],
            [100*l["frequencia_relativa"] for l in tabela1], largura, label="Observada")
    plt.xticks(eixos, rotulos)
    plt.ylabel("Probabilidade / frequência (%)")
    plt.xlabel("Resultado central")
    plt.legend()
    finalizar("experimento1_frequencias.png")

    plt.figure(figsize=(8, 4.3))
    for semente, curva in medias.items():
        plt.plot(range(1, 10001, 20), curva[::20], label=f"Semente {semente}", linewidth=1.2)
    plt.axhline(-0.16, linestyle="--", color="black", label="Esperança: -0,16")
    plt.xlabel("Número de rodadas")
    plt.ylabel("Lucro médio acumulado (créditos)")
    plt.legend()
    finalizar("experimento2_medias.png")

    plt.figure(figsize=(8, 4.3))
    for i, caminho in enumerate(trajetorias, start=1):
        plt.plot(range(501), caminho, label=f"Participante {i}", linewidth=1.3)
    plt.axhline(100, linestyle="--", color="black", label="Saldo inicial")
    plt.xlabel("Rodadas")
    plt.ylabel("Saldo (créditos)")
    plt.legend()
    finalizar("experimento3_trajetorias.png")

    plt.figure(figsize=(7, 4))
    x = [0, 1]
    plt.bar(x, [100*t["rtp_teorico"] for t in tabela5])
    plt.xticks(x, ["Base", "Prêmios +10%"])
    plt.ylabel("RTP teórico (%)")
    plt.axhline(100, linestyle="--", color="black", label="Equilíbrio (100%)")
    plt.legend()
    finalizar("experimento5_rtp.png")

    plt.figure(figsize=(7, 4))
    dados = adicionais["sensibilidade"]
    plt.plot([100*d["fator_pagamento"] for d in dados],
             [100*d["rtp_teorico"] for d in dados], marker="o")
    plt.axhline(100, linestyle="--", color="black", label="RTP = 100%")
    plt.xlabel("Pagamento em relação à tabela-base (%)")
    plt.ylabel("RTP teórico (%)")
    plt.legend()
    finalizar("extra_sensibilidade.png")


def executar_todos():
    print("Simulador acadêmico - somente créditos fictícios")
    RESULTADOS.mkdir(exist_ok=True)
    rodadas = simular_rodadas(10000, 2026)
    e1, tabela1 = experimento_1(rodadas)
    e2, medias = experimento_2(rodadas)
    e3, trajetorias = experimento_3()
    e4 = experimento_4(rodadas)
    e5 = experimento_5(rodadas)
    sessoes_base, _ = simular_sessoes()
    adicionais = extras(rodadas, sessoes_base)
    gerar_graficos(tabela1, medias, trajetorias, e5, adicionais)
    import matplotlib
    dados = {"modelo": {"simbolos": SIMBOLOS, "pagamentos": PAGAMENTOS,
                        "aposta": 1, "chance_premio": 0.04,
                        "premio_esperado": 0.84, "lucro_esperado": -0.16,
                        "rtp": 0.84},
             "ambiente": {"python": platform.python_version(),
                          "biblioteca_sorteio": "random.Random / Mersenne Twister",
                          "matplotlib": matplotlib.__version__,
                          "semente_e1_e4_e5": 2026,
                          "sementes_e2": [10, 2026, 123456], "semente_e3": 42,
                          "semente_extra_exposicao": 2027},
             "experimento1": e1, "experimento2": e2, "experimento3": e3,
             "experimento4": e4, "experimento5": e5, "extras": adicionais}
    (RESULTADOS / "resumo.json").write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")
    print("E1 - lucro médio:", round(e1["lucro_medio"], 5), "| RTP:", round(100*e1["rtp_observado"], 2), "%")
    print("E2 - primeira dezena reproduzida:", e2["primeiros10_reproduzidos"])
    print("E3 - saldo médio:", round(e3["saldo_medio"], 2), "| esgotamento:", round(100*e3["esgotamento"], 2), "%")
    print("E4 - total de pares:", sum(v["total_pares"] for v in e4))
    print("E5 - RTP teórico base / +10%:", e5[0]["rtp_teorico"], e5[1]["rtp_teorico"])
    print("Arquivos gerados em:", RESULTADOS)
    return dados


def main():
    parser = argparse.ArgumentParser(description="Máquina estatística: apenas créditos fictícios")
    parser.add_argument("acao", choices=["rodada", "todos"], nargs="?", default="todos",
                        help="rodada: mostra tabuleiro; todos: gera experimentos e arquivos")
    parser.add_argument("--semente", type=int, default=2026, help="semente para a rodada demonstrativa")
    args = parser.parse_args()
    if args.acao == "rodada":
        mostrar_rodada(rodada(random.Random(args.semente)))
    else:
        executar_todos()


if __name__ == "__main__":
    main()
