// Rode com: node --test tests/test_site.mjs
// Confere as regras da versão do navegador, sem abrir uma página.
import test from 'node:test';
import assert from 'node:assert/strict';
import {
  montarTabuleiro, calcularResultado, criarSessao, registrarRodada,
  podeJogar, frequencias, estatisticas, sortearRodada,
} from '../docs/modelo.mjs';

test('uma parada K=4 mostra E, A, B na mesma coluna', () => {
  const tabuleiro = montarTabuleiro([4, 4, 4]);
  assert.deepEqual(tabuleiro.map(linha => linha[0]), ['E', 'A', 'B']);
  assert.equal(calcularResultado([4, 4, 4]).centro, 'AAA');
});

test('todos os 125 resultados: 5 premiados e 120 sem premio', () => {
  const contagem = new Map();
  let premiadas = 0;
  for (let a = 0; a < 5; a++) {
    for (let b = 0; b < 5; b++) {
      for (let c = 0; c < 5; c++) {
        const r = calcularResultado([a, b, c]);
        contagem.set(r.centro, (contagem.get(r.centro) || 0) + 1);
        if (r.premio) premiadas++;
        assert.equal(r.lucro, r.premio - 1);
      }
    }
  }
  assert.equal(contagem.size, 125);
  assert.equal(premiadas, 5);
  assert.ok([...contagem.values()].every(n => n === 1));
});

test('os cinco premios e lucros coincidem com o modelo-base', () => {
  const pagamentos = [5, 10, 15, 25, 50];
  for (let k = 0; k < 5; k++) {
    const r = calcularResultado([k, k, k]);
    assert.equal(r.premio, pagamentos[(k + 1) % 5]);
    assert.equal(r.lucro, r.premio - 1);
  }
  assert.equal(calcularResultado([0, 1, 2]).premio, 0);
});

test('RTP 84% e lucro medio esperado de -0,16', () => {
  let soma = 0;
  for (let a = 0; a < 5; a++)
    for (let b = 0; b < 5; b++)
      for (let c = 0; c < 5; c++) soma += calcularResultado([a, b, c]).premio;
  assert.equal(soma / 125, 0.84);
  assert.equal(soma / 125 - 1, -0.16000000000000003);
});

test('sessao começa com 100 e termina em 500 rodadas', () => {
  const s = criarSessao();
  assert.equal(s.saldo, 100);
  const sempreA = calcularResultado([4, 4, 4]);
  for (let i = 0; i < 500; i++) assert.equal(registrarRodada(s, sempreA), true);
  assert.equal(s.rodadas.length, 500);
  assert.equal(podeJogar(s), false);
  assert.equal(registrarRodada(s, sempreA), false);
});

test('saldo zero encerra sessao sem emprestimos', () => {
  const s = criarSessao();
  const perda = calcularResultado([0, 1, 2]);
  for (let i = 0; i < 100; i++) registrarRodada(s, perda);
  assert.equal(s.saldo, 0);
  assert.equal(podeJogar(s), false);
  assert.equal(s.rodadas.length, 100);
});

test('frequencias somam numero de rodadas, inclusive sem premio', () => {
  const s = criarSessao();
  registrarRodada(s, calcularResultado([4, 4, 4]));
  registrarRodada(s, calcularResultado([0, 1, 2]));
  assert.equal(frequencias(s).reduce((total, f) => total + f.contagem, 0), 2);
  assert.equal(estatisticas(s).vitorias, 1);
  assert.equal(estatisticas(s).rtp, 5 / 2);
});

test('sortearRodada aceita sorteador fixo para testes', () => {
  assert.equal(sortearRodada(() => 4).centro, 'AAA');
});
