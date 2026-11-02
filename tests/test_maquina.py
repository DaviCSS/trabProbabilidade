"""Verificações automáticas usando unittest (sem dependencia adicional)."""
import math
import random
import unittest

from maquina import (PAGAMENTOS, PAGAMENTOS_10,
                     experimento_4, rodada, simular_rodadas, simular_sessoes,
                     resumo_sessoes)


class TesteMaquina(unittest.TestCase):
    def test_tabuleiro_circular(self):
        resultado = rodada(random.Random(42))
        for k, coluna in zip(resultado["paradas"], zip(*resultado["tabuleiro"])):
            self.assertEqual(tuple("ABCDE"[(k+i) % 5] for i in range(3)), coluna)

    def test_pagamentos_das_cinco_triplas(self):
        for indice, simbolo in enumerate("ABCDE"):
            class GeradorFixo:
                def randrange(self, n):
                    return (indice - 1) % n  # meio da coluna = simbolo
            self.assertEqual(rodada(GeradorFixo())["premio"], PAGAMENTOS[simbolo])

    def test_sem_premio(self):
        class Gerador:
            posicoes = iter([0, 1, 2])
            def randrange(self, n):
                return next(self.posicoes)
        self.assertEqual(rodada(Gerador())["premio"], 0)

    def test_aposta_descontada(self):
        r = rodada(random.Random(123))
        self.assertEqual(r["lucro"], r["premio"] - 1)

    def test_reprodutibilidade(self):
        a = simular_rodadas(10, 2026)
        b = simular_rodadas(10, 2026)
        self.assertEqual(a, b)

    def test_contagem_10000(self):
        self.assertEqual(len(simular_rodadas(10000, 2026)), 10000)

    def test_pares_consecutivos(self):
        linhas = experimento_4(simular_rodadas(10000, 2026))
        self.assertEqual(sum(l["total_pares"] for l in linhas), 9999)

    def test_limite_com_saldo_zero(self):
        sessoes, _ = simular_sessoes(participantes=1, saldo_inicial=0)
        self.assertEqual(sessoes[0]["rodadas"], 0)
        self.assertEqual(sessoes[0]["saldo_final"], 0)
        self.assertEqual(sessoes[0]["esgotou"], 1)

    def test_categorias_de_100_participantes(self):
        sessoes, _ = simular_sessoes()
        r = resumo_sessoes(sessoes)
        self.assertEqual(len(sessoes), 100)
        self.assertAlmostEqual(r["ganho"] + r["empate"] + r["perda"], 1)
        self.assertLessEqual(r["esgotamento"], r["perda"])

    def test_esperanca_e_rtp(self):
        self.assertAlmostEqual(sum(PAGAMENTOS.values()) / 125, 0.84)
        self.assertAlmostEqual(sum(PAGAMENTOS_10.values()) / 125, 0.924)


if __name__ == "__main__":
    unittest.main()
