"""Gera o relatório PDF a partir dos resultados, com reportlab."""
import json
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                Table, TableStyle, PageBreak, KeepTogether)

BASE = Path(__file__).parent
DADOS = json.loads((BASE / "resultados/resumo.json").read_text(encoding="utf-8"))
DESTINO = BASE / "relatorio"
DESTINO.mkdir(exist_ok=True)

FONTE = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
FONTE_BOLD = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
if FONTE.exists() and FONTE_BOLD.exists():
    pdfmetrics.registerFont(TTFont("DejaVu", str(FONTE)))
    pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(FONTE_BOLD)))
    NORMAL, NEGRITO = "DejaVu", "DejaVu-Bold"
else:
    NORMAL, NEGRITO = "Helvetica", "Helvetica-Bold"

VERDE = colors.HexColor("#185b42")
CINZA = colors.HexColor("#56616a")
ESTILOS = {
    "titulo": ParagraphStyle("Titulo", fontName=NEGRITO, fontSize=17, leading=23,
                             textColor=VERDE, spaceAfter=10),
    "secao": ParagraphStyle("Secao", fontName=NEGRITO, fontSize=11.5, leading=17,
                            textColor=VERDE, spaceBefore=10, spaceAfter=5),
    "corpo": ParagraphStyle("Corpo", fontName=NORMAL, fontSize=8.8, leading=13.4,
                            alignment=TA_JUSTIFY, spaceAfter=6),
    "legenda": ParagraphStyle("Legenda", fontName=NORMAL, fontSize=8.1, leading=12,
                              textColor=CINZA, spaceAfter=7),
    "celula": ParagraphStyle("Celula", fontName=NORMAL, fontSize=8, leading=11),
    "cabecalho": ParagraphStyle("Cabecalho", fontName=NEGRITO, fontSize=8, leading=11,
                                textColor=colors.white),
    "centro": ParagraphStyle("Centro", fontName=NORMAL, fontSize=9.4, leading=15,
                             alignment=TA_CENTER),
}


def p(texto, estilo="corpo"):
    return Paragraph(texto, ESTILOS[estilo])


def secao(titulo):
    return p(titulo, "secao")


def tabela(cabecalho, linhas, larguras=None):
    conteudo = [[p(escape(str(v)), "cabecalho") for v in cabecalho]]
    conteudo += [[p(escape(str(v)), "celula") for v in linha] for linha in linhas]
    t = Table(conteudo, colWidths=larguras, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), VERDE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef5f0")]),
        ("LINEBELOW", (0, -1), (-1, -1), 0.5, colors.HexColor("#b9c6be")),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def grafico(arquivo, legenda, largura=15.5*cm, altura=8*cm):
    return [Image(str(BASE / "resultados/graficos" / arquivo), width=largura, height=altura),
            p(legenda + " Fonte: simulação própria, sementes registradas no resumo.json.", "legenda")]


def porcento(valor):
    return f"{100*valor:.2f}%".replace(".", ",")


def numero(valor, casas=3):
    return f"{valor:.{casas}f}".replace(".", ",")


def rodape(canvas, doc):
    canvas.saveState()
    largura, _ = A4
    canvas.setStrokeColor(colors.HexColor("#c8d4cd"))
    canvas.line(2.1*cm, 1.35*cm, largura - 2.1*cm, 1.35*cm)
    canvas.setFont(NORMAL, 7.2)
    canvas.drawString(2.1*cm, 1.05*cm, "IFES · Probabilidade e Estatística I · Trabalho I · Modelo didático")
    canvas.drawRightString(largura - 2.1*cm, 1.05*cm, str(doc.page))
    canvas.restoreState()


def documento(caminho, conteudo, titulo):
    pdf = SimpleDocTemplate(str(caminho), pagesize=A4, rightMargin=2.1*cm,
                            leftMargin=2.1*cm, topMargin=2.0*cm,
                            bottomMargin=1.8*cm, title=titulo,
                            author="Trabalho acadêmico - integrantes a identificar")
    pdf.build(conteudo, onFirstPage=rodape, onLaterPages=rodape)


def relatorio():
    e1, e2, e3, e4, e5 = [DADOS[f"experimento{i}"] for i in range(1, 6)]
    ext = DADOS["extras"]
    linhas_e1 = __import__("csv").DictReader((BASE / "resultados/experimento1_frequencias.csv").open(encoding="utf-8"))
    contagens = list(linhas_e1)
    c = []

    # 1 - contexto e matematica
    c += [p("Máquina estatística: probabilidade, apostas e pensamento crítico", "titulo"),
          p("IFES – Campus Serra | Probabilidade e Estatística I | Trabalho I – 2026/2"),
          p("Integrantes: [preencher nomes antes da entrega]. Relatório produzido a partir de execução determinística do programa em Python."),
          secao("1. Contexto, problema e objetivos"),
          p("Este trabalho investiga a diferença entre a chance de receber um prêmio em uma rodada e o resultado financeiro esperado após muitas rodadas. Para isso, construímos uma máquina de rolos inteiramente fictícia, com regras públicas e resultados reproduzíveis. Nenhuma pessoa real foi observada; os 'participantes' são trajetórias calculadas por computador."),
          p("A motivação social não é inferida dos dados simulados. Ela é estudada separadamente por fontes como a Organização Mundial da Saúde (OMS), o Banco Central do Brasil e documentos de debate público. Esse cuidado evita transformar uma demonstração matemática em estimativa de prevalência ou de dano social."),
          secao("2. Regras, espaço amostral e variáveis"),
          p("Há três rolos com a sequência circular A, B, C, D, E. Para cada rolo, sorteia-se uma posição K entre 0 e 4 com chance de 1/5; a coluna mostra K, K+1 e K+2 (módulo 5). Só a linha central paga, quando os três símbolos são iguais. Cada rodada custa 1 crédito. Os rolos e as rodadas são independentes, mas as três posições de uma mesma coluna não são independentes entre si."),
          p("Existem 5³ = 125 triplas centrais equiprováveis. Cada tripla específica tem probabilidade 1/125. As cinco triplas premiadas ocupam 5/125 = 4% dos resultados; os outros 120/125 = 96% não geram prêmio. Definimos P como prêmio bruto e X = P - 1 como lucro líquido por rodada."),
          tabela(["Centro", "P: prêmio", "X: lucro", "Probabilidade"],
                 [[s*3, PAG, PAG-1, "1/125"] for s, PAG in zip("ABCDE", [5, 10, 15, 25, 50])] +
                 [["Outras 120", "0", "-1", "120/125"]],
                 [4.1*cm, 3.1*cm, 3.1*cm, 5.3*cm]),
          p("E[P] = (5 + 10 + 15 + 25 + 50)/125 = 0,84 crédito. Portanto E[X] = 0,84 - 1 = -0,16 crédito por rodada. RTP = E[P]/1 = 84% e a vantagem matemática do operador é 16%. O RTP não é a chance de prêmio nem garante devolução em uma sessão específica.")]
    c.append(PageBreak())

    # 2 E1
    c += [secao("3. Experimento 1 – Frequências e probabilidades"),
          p("Procedimento: foram realizadas exatamente 10.000 rodadas com semente 2026, sem limitação de saldo. Registramos as seis categorias de lucro, suas probabilidades teóricas, contagens e frequências relativas."),
          tabela(["Resultado", "X", "Teoria", "Contagem", "Observado"],
                 [[d["resultado"], d["lucro"], porcento(float(d["probabilidade_teorica"])),
                   d["contagem"], porcento(float(d["frequencia_relativa"]))]
                  for d in contagens],
                 [3.3*cm, 1.7*cm, 2.8*cm, 3.2*cm, 4.5*cm]),
          Spacer(1, 6),
          *grafico("experimento1_frequencias.png", "Figura 1. Comparação entre frequência observada e probabilidade do modelo.", altura=7.0*cm),
          p(f"As contagens totalizaram 10.000. O lucro médio foi {numero(e1['lucro_medio'],4)} crédito, o desvio-padrão amostral foi {numero(e1['desvio_amostral'])} créditos, o RTP observado foi {porcento(e1['rtp_observado'])} e a frequência de prêmio foi {porcento(e1['frequencia_premio'])}. A média negativa descreve o saldo médio por rodada; o desvio-padrão descreve a dispersão dos lucros, que inclui prêmios raros e grandes."),
          p("As proporções observadas oscilam ao redor de 0,8% para cada tripla premiada e 96% para as demais. Não se espera igualdade exata em 10.000 observações. A frequência de prêmios conta quantas rodadas pagam; o RTP considera também quanto essas rodadas pagam. Por isso são medidas diferentes.")]
    c.append(PageBreak())

    # 3 E2
    c += [secao("4. Experimento 2 – Médias acumuladas"),
          p("Procedimento: três execuções de 10.000 rodadas usaram sementes 10, 2026 e 123456. Reaproveitamos integralmente a sequência 2026 do Experimento 1. Para cada execução, observamos o lucro médio acumulado nas rodadas 100, 1.000 e 10.000."),
          tabela(["Semente", "100 rodadas", "1.000 rodadas", "10.000 rodadas"],
                 [[str(seed)] + [numero(next(r["lucro_medio_acumulado"] for r in e2["medias"]
                                       if r["semente"] == seed and r["rodadas"] == n), 4)
                                 for n in (100, 1000, 10000)] for seed in (10, 2026, 123456)],
                 [3.3*cm, 4.0*cm, 4.1*cm, 4.1*cm]),
          Spacer(1, 9),
          *grafico("experimento2_medias.png", "Figura 2. Três médias acumuladas e referência teórica de -0,16 crédito.", altura=9*cm),
          p("A Lei dos Grandes Números afirma uma convergência probabilística da média à esperança sob independência e distribuição fixa. Ela não exige trajetória monotônica, nem determina um erro máximo para 10.000 rodadas. Ganhos iniciais não modificam as probabilidades das rodadas futuras."),
          p(f"Reprodutibilidade: com o mesmo ambiente e a semente 2026, os dez primeiros resultados centrais foram repetidos? {'Sim' if e2['primeiros10_reproduzidos'] else 'Não'}. As dez linhas foram preservadas em CSV. O gerador é random.Random (Mersenne Twister); a semente é definida uma única vez no começo de cada sequência.")]
    c.append(PageBreak())

    # 4 E3
    c += [secao("5. Experimento 3 – Limite de saldo"),
          p("Procedimento: simulamos 100 participantes virtuais, cada um iniciando com 100 créditos, apostando 1 por rodada. A sessão termina ao completar 500 rodadas ou quando saldo &lt; 1. A semente 42 inicia um único gerador, cujo estado continua entre as pessoas; não há empréstimos nem reposição de saldo."),
          tabela(["Indicador", "Resultado"],
                 [["Ganho", porcento(e3["ganho"])],
                  ["Empate", porcento(e3["empate"])],
                  ["Perda", porcento(e3["perda"])],
                  ["Esgotamento (dentro das perdas)", porcento(e3["esgotamento"])],
                  ["Saldo final médio", numero(e3["saldo_medio"],2) + " créditos"],
                  ["Saldo final mediano", numero(e3["saldo_mediano"],2) + " créditos"],
                  ["Rodadas médias", numero(e3["rodadas_medias"],2)]], [9*cm, 6.5*cm]),
          Spacer(1, 8),
          *grafico("experimento3_trajetorias.png", "Figura 3. Saldo dos cinco primeiros participantes, sem seleção de casos. Após a parada, o saldo permanece constante.", altura=8.8*cm),
          p("O esgotamento é subconjunto das perdas, não uma categoria independente. A média resume os saldos de todas as pessoas; a mediana localiza o centro da distribuição sem ser tão influenciada pelos maiores ganhos. Um participante que termina acima de 100 não altera a expectativa negativa por rodada."),
          p("Como o número de rodadas varia por participante, não podemos aplicar 100 - 500×0,16 à média de saldos finais. As sessões dependem da condição de parada. São resultados de um modelo com horizonte e saldo fixados, não previsões sobre famílias brasileiras.")]
    c.append(PageBreak())

    # 5 E4 E5
    c += [secao("6. Experimento 4 – Probabilidade condicional"),
          p("Usamos os 9.999 pares consecutivos das 10.000 rodadas do Experimento 1. Separamos os pares conforme a primeira rodada teve prêmio, e dividimos o número de prêmios na rodada seguinte pelo total de pares de cada grupo."),
          tabela(["Rodada anterior", "Pares", "Prêmios seguintes", "Proporção"],
                 [[x["resultado_anterior"], x["total_pares"], x["premios_rodada_seguinte"],
                   porcento(x["proporcao"]) if isinstance(x["proporcao"], (int,float)) else x["proporcao"]]
                  for x in e4], [4.8*cm, 2.2*cm, 4.3*cm, 4.2*cm]),
          p("Pelo modelo, Pr(prêmio seguinte | prêmio anterior) = Pr(prêmio seguinte | perda anterior) = 4%. Diferenças entre frequências experimentais são esperadas, especialmente após prêmio, grupo menor. O sorteio não tem memória nem passa a 'dever' compensação; acreditar nisso é a falácia do jogador."),
          secao("7. Experimento 5 – Aumento dos pagamentos"),
          p("Para as duas tabelas, aplicamos os pagamentos aos mesmos 10.000 resultados, sem novo sorteio. A base paga (5, 10, 15, 25, 50); a outra paga 10% a mais, inclusive valores fracionários."),
          tabela(["Tabela", "Prêmio médio", "Lucro médio", "RTP teórico", "RTP observado"],
                 [["Base" if i == 0 else "+10%", numero(x["premio_medio"],4),
                   numero(x["lucro_medio"],4), porcento(x["rtp_teorico"]),
                   porcento(x["rtp_observado"])] for i,x in enumerate(e5)],
                 [2.7*cm, 3.0*cm, 3.0*cm, 3.1*cm, 3.7*cm]),
          Spacer(1, 8),
          *grafico("experimento5_rtp.png", "Figura 4. RTP teórico das duas tabelas. O risco de retorno negativo permanece.", altura=6.8*cm),
          p("A probabilidade de qualquer prêmio continua 4%. O RTP sobe de 84% a 92,4% e E[X] passa de -0,16 a -0,076, ainda negativos. Um prêmio maior não representa maior frequência nem, por si só, vantagem do jogador.")]
    c.append(PageBreak())

    # Extras escolhidos: somente validação e análise de sensibilidade.
    c += [secao("8. Extras selecionados"),
          p("Validação automatizada: usamos testes unittest para verificar tabuleiro circular, cinco pagamentos, rodada sem prêmio, desconto da aposta, reprodução por semente, 10.000 rodadas, 9.999 pares, saldo zero, categorias de 100 participantes e os valores de RTP. Execução: python -m unittest discover -s tests -v."),
          p("Análise de sensibilidade: foram calculados sete cenários, multiplicando os cinco pagamentos por 0,50; 0,75; 1,00; 1,10; 1,20; 1,25 e 1,50. As chances permanecem em 4%; RTP = 0,84 × fator e E[X] = RTP - 1. O cenário 1,20 supera ligeiramente 100% de RTP, mostrando que alterar pagamentos, mesmo sem mudar as chances, pode mudar a esperança."),
          tabela(["Fator de pagamento", "RTP teórico", "Lucro esperado"],
                 [[numero(x["fator_pagamento"],2), porcento(x["rtp_teorico"]),
                   numero(x["lucro_esperado"],3)] for x in ext["sensibilidade"]],
                 [5.4*cm, 4.5*cm, 5.6*cm]),
          p("A tabela e o gráfico completo em resultados/graficos/extra_sensibilidade.png permitem conferir os cenários. Os testes demonstram a consistência da implementação, sem substituir a interpretação dos cinco experimentos.")]

    # 8 discussion
    c += [secao("9. Discussão crítica: mecanismo, renda e saúde"),
          p(f"A matemática responde à pergunta inicial: embora apenas 4% das rodadas tenham prêmio, algumas delas geram lucros de 4 a 49 créditos; ao mesmo tempo, 96% retiram 1 crédito. A soma ponderada dá E[X] = -0,16. No experimento, o lucro médio foi {numero(e1['lucro_medio'],4)}, mas {porcento(e3['ganho'])} dos participantes virtuais do E3 terminaram acima do saldo inicial. Assim, ganhos pontuais e expectativa negativa são compatíveis. Um relato isolado de vitória oculta a distribuição completa e as perdas de outras sessões."),
          p("A OMS (2024) associa danos do jogo a dificuldades financeiras, sofrimento mental, conflitos familiares e desvio de recursos de necessidades básicas [1]. Isso diz respeito a pessoas reais e a múltiplas modalidades, não a uma inferência clínica produzida por nossos personagens simulados. O modelo não mede transtorno do jogo, renda familiar ou comportamento humano."),
          secao("9.1. O Brasil: dado observado versus estimativa"),
          p("O Estudo Especial 119/2024 do Banco Central identificou transferências brutas por Pix a empresas de apostas na ordem de R$ 18 a 21 bilhões mensais em 2024 [2]. O indicador mede transferências, não a perda líquida de usuários e não o lucro operacional final. Apresentá-lo como dinheiro perdido confundiria conceitos e exageraria o significado do número. Também não se deve igualar esse agregado a créditos fictícios."),
          secao("9.2. Política pública e argumentos em disputa"),
          p("A MP 1.394/2026, publicada em 25 de setembro, estabeleceu proibição da exploração, oferta, intermediação e publicidade das apostas de quota fixa [3]. A página de tramitação do Congresso Nacional registrava a matéria ainda em apreciação na consulta de 30/10/2026; existência de uma MP não equivale a uma decisão judicial final. A defesa de restrições prioriza proteção de saúde e renda, especialmente de grupos vulneráveis. A posição encontra apoio no reconhecimento dos danos pela OMS, mas a eficiência de uma medida particular requer acompanhamento de resultados."),
          p("As entidades ANJL e IBJR solicitaram ao STF a suspensão da MP, segundo a Agência Brasil em 28/09/2026, alegando insegurança jurídica e impactos sobre investimentos [4]. Trata-se de argumento e pedido das entidades, não de decisão do STF nem de prova de que a proibição fracassará. A fiscalização da oferta irregular, a publicidade e o respeito à autonomia integram a controvérsia. Para julgar efeitos concretos da política, seriam necessários dados reais posteriores e desenhos de pesquisa apropriados."),
          secao("9.3. Responsabilidade em Sistemas de Informação"),
          p("Animações, cores e destaque dos maiores prêmios podem tornar a raridade pouco perceptível. Uma interface responsável deveria informar separadamente probabilidade de prêmio, RTP e lucro esperado, em linguagem compreensível, e evitar sugerir que perdas recentes tornaram a próxima vitória mais provável. Transparência técnica e fiscalização são complementares: o código pode estar correto e a comunicação ainda induzir erro."),
          secao("10. Conclusão e limites"),
          p("Concluímos que a desvantagem econômica é propriedade da distribuição probabilística dos pagamentos, não da ausência de prêmios. A simulação reproduziu padrões coerentes com a teoria, exibindo variação amostral legítima. Nenhum resultado sugere estratégia de lucro ou diagnostica problemas de saúde. A pesquisa documental amplia o debate, sem converter uma máquina didática em representação fiel de um produto comercial ou da população brasileira."),
          p("Uso de IA: houve apoio na implementação das funções e verificações, estruturação e revisão dos textos, geração dos gráficos e documentação. As regras, fórmulas, sementes e saídas ficam disponíveis para conferência dos integrantes; é necessário revisar e personalizar o texto antes de entregar.")]
    c.append(PageBreak())

    # Bibliografia, fora da contagem de conteudo
    c += [secao("Referências (fora da contagem de páginas de conteúdo)"),
          p("[1] ORGANIZAÇÃO MUNDIAL DA SAÚDE. Gambling. 2 dez. 2024. https://www.who.int/news-room/fact-sheets/detail/gambling"),
          p("[2] BANCO CENTRAL DO BRASIL. Análise técnica sobre o mercado de apostas online no Brasil e o perfil dos apostadores. Estudo Especial 119, 2024. https://www.bcb.gov.br/conteudo/relatorioinflacao/EstudosEspeciais/EE119_Analise_tecnica_sobre_o_mercado_de_apostas_online_no_Brasil_e_o_perfil_dos_apostadores.pdf"),
          p("[3] CONGRESSO NACIONAL. Medida Provisória 1.394/2026. Texto e tramitação. https://www.congressonacional.leg.br/materias/medidas-provisorias/-/mpv/175871"),
          p("[4] AGÊNCIA BRASIL. Associações de jogos acionam STF contra MP que proibiu apostas online. 28 set. 2026. https://agenciabrasil.ebc.com.br/justica/noticia/2026-09/associacoes-de-jogos-acionam-stf-contra-mp-que-proibiu-apostas-online"),
          p("[5] PYTHON SOFTWARE FOUNDATION. random — Generate pseudo-random numbers. https://docs.python.org/3/library/random.html"),
          p("[6] ILLOWSKY, B.; DEAN, S. Introductory Statistics 2e. OpenStax, 2023. https://openstax.org/details/books/introductory-statistics-2e"),
          p("Consulta às fontes públicas: 30 out. 2026. Registrar eventuais atualizações posteriores à entrega."),
          secao("Rastreabilidade"),
          p("CSV: resultados/*.csv; gráficos: resultados/graficos/*.png; ambiente, sementes e números: resultados/resumo.json; programa: maquina.py; verificações: tests/test_maquina.py; gerador deste PDF: gerar_relatorio.py."),
          p("Observação final: preencher os nomes dos integrantes e verificar a versão final dos documentos antes do envio.")]
    documento(DESTINO / "relatorio.pdf", c, "Relatório – Máquina Estatística")


if __name__ == "__main__":
    relatorio()
    print("Relatório PDF criado em", DESTINO)
