// Regras didaticas iguais as do simulador Python (maquina.py).
// Este arquivo funciona no navegador e tambem pode ser testado no Node.js.

export const SIMBOLOS = 'ABCDE';
export const PAGAMENTOS = { A: 5, B: 10, C: 15, D: 25, E: 50 };
export const APOSTA = 1;
export const SALDO_INICIAL = 100;
export const LIMITE_RODADAS = 500;

// Os tres rolos usam a sequencia circular A, B, C, D, E.
export function montarTabuleiro(paradas) {
  if (paradas.length !== 3 || paradas.some(k => !Number.isInteger(k) || k < 0 || k > 4)) {
    throw new Error('São necessárias três paradas entre 0 e 4.');
  }
  return [0, 1, 2].map(linha =>
    paradas.map(k => SIMBOLOS[(k + linha) % 5])
  );
}

export function calcularResultado(paradas, pagamentos = PAGAMENTOS) {
  const tabuleiro = montarTabuleiro(paradas);
  const centro = tabuleiro[1].join('');
  const ganhou = centro[0] === centro[1] && centro[1] === centro[2];
  const premio = ganhou ? pagamentos[centro[0]] : 0;
  return { paradas: [...paradas], tabuleiro, centro, premio, lucro: premio - APOSTA };
}

// Amostragem uniforme sem vies do resto da divisao.
// O navegador fornece numeros via Web Crypto (nao e o mesmo gerador do Python).
export function sortearParada() {
  const limite = Math.floor(4294967296 / 5) * 5;
  const numeros = new Uint32Array(1);
  let numero;
  do {
    globalThis.crypto.getRandomValues(numeros);
    numero = numeros[0];
  } while (numero >= limite);
  return numero % 5;
}

export function sortearRodada(sorteador = sortearParada) {
  return calcularResultado([sorteador(), sorteador(), sorteador()]);
}

export function criarSessao() {
  return { saldo: SALDO_INICIAL, rodadas: [], historicoSaldo: [SALDO_INICIAL] };
}

export function podeJogar(sessao) {
  return sessao.saldo >= APOSTA && sessao.rodadas.length < LIMITE_RODADAS;
}

export function registrarRodada(sessao, resultado) {
  if (!podeJogar(sessao)) return false;
  sessao.saldo += resultado.lucro;
  sessao.rodadas.push(resultado);
  sessao.historicoSaldo.push(sessao.saldo);
  return true;
}

export function estatisticas(sessao) {
  const n = sessao.rodadas.length;
  const totalPremios = sessao.rodadas.reduce((soma, r) => soma + r.premio, 0);
  const vitorias = sessao.rodadas.filter(r => r.premio > 0).length;
  return {
    total: n, vitorias, frequenciaPremio: n ? vitorias / n : 0,
    rtp: n ? totalPremios / n : 0,
    lucroTotal: sessao.saldo - SALDO_INICIAL,
    lucroMedio: n ? (sessao.saldo - SALDO_INICIAL) / n : 0
  };
}

export function frequencias(sessao) {
  const categorias = ['AAA', 'BBB', 'CCC', 'DDD', 'EEE', 'sem premio'];
  return categorias.map(categoria => {
    const contagem = sessao.rodadas.filter(r =>
      categoria === 'sem premio' ? r.premio === 0 : r.centro === categoria
    ).length;
    return {
      categoria, contagem,
      observado: sessao.rodadas.length ? contagem / sessao.rodadas.length : 0,
      teorico: categoria === 'sem premio' ? 120 / 125 : 1 / 125
    };
  });
}
