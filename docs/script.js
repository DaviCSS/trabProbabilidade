// Interface do simulador: a matemática fica no arquivo modelo.mjs.
// Apenas créditos fictícios. Sem apostas reais, contas ou pagamentos.
import {
  criarSessao, podeJogar, registrarRodada, sortearRodada,
  estatisticas, frequencias, SALDO_INICIAL, LIMITE_RODADAS
} from './modelo.mjs';

const pegar = id => document.getElementById(id);
const formatar = numero => numero.toLocaleString('pt-BR', { maximumFractionDigits: 2 });
let sessao = criarSessao();

function atualizarTabuleiro(resultado) {
  const casas = pegar('grade').children;
  for (let linha = 0; linha < 3; linha++) {
    for (let coluna = 0; coluna < 3; coluna++) {
      casas[linha * 3 + coluna].textContent = resultado.tabuleiro[linha][coluna];
    }
  }
  pegar('visor').classList.toggle('vencedor', resultado.premio > 0);
  pegar('visor').setAttribute('aria-label',
    `Tabuleiro de três rolos. Linha central: ${resultado.centro.split('').join(', ')}. ` +
    (resultado.premio ? `Prêmio: ${resultado.premio} créditos.` : 'Sem prêmio.'));
}

function atualizarGrafico() {
  const saldos = sessao.historicoSaldo;
  const minimo = Math.min(0, ...saldos);
  const maximo = Math.max(100, ...saldos);
  const alcance = Math.max(1, maximo - minimo);
  const esquerda = 50, direita = 700, topo = 25, base = 220;
  const fim = Math.max(1, saldos.length - 1);
  const pontos = saldos.map((saldo, i) => {
    const x = esquerda + (direita - esquerda) * i / fim;
    const y = base - (saldo - minimo) * (base - topo) / alcance;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  });
  if (pontos.length === 1) pontos.push(`${esquerda},${pontos[0].split(',')[1]}`);
  pegar('linha-saldo').setAttribute('points', pontos.join(' '));
  pegar('grafico-min').textContent = formatar(minimo);
  pegar('grafico-max').textContent = formatar(maximo);
  pegar('grafico-fim').textContent = `${sessao.rodadas.length} rodadas`;
  pegar('pontos-grafico').textContent = `${sessao.rodadas.length} rodadas`;
  pegar('grafico-saldo').setAttribute('aria-label',
    `Trajetória do saldo: de ${SALDO_INICIAL} até ${formatar(sessao.saldo)} créditos ` +
    `em ${sessao.rodadas.length} rodadas.`);
}

function atualizarHistorico() {
  const lista = pegar('historico');
  lista.replaceChildren();
  if (sessao.rodadas.length === 0) {
    const vazio = document.createElement('p');
    vazio.className = 'vazio';
    vazio.textContent = 'Suas rodadas aparecerão aqui.';
    lista.appendChild(vazio);
    return;
  }
  sessao.rodadas.slice(-8).reverse().forEach((resultado, i) => {
    const linha = document.createElement('div');
    linha.className = 'historico-item';
    const tripla = document.createElement('span');
    tripla.className = 'tripla';
    tripla.textContent = resultado.centro;
    const contexto = document.createElement('small');
    contexto.textContent = `Rodada ${sessao.rodadas.length - i}`;
    const premio = document.createElement('span');
    premio.className = `premio ${resultado.premio ? '' : 'zero'}`;
    premio.textContent = `Prêmio: ${formatar(resultado.premio)} · Lucro: ${resultado.lucro > 0 ? '+' : ''}${formatar(resultado.lucro)}`;
    linha.append(tripla, contexto, premio);
    lista.append(linha);
  });
}

function atualizarFrequencias() {
  const corpo = pegar('tabela-frequencias');
  corpo.replaceChildren();
  frequencias(sessao).forEach(dados => {
    const linha = document.createElement('tr');
    const valores = [dados.categoria, `${(dados.teorico * 100).toFixed(1).replace('.', ',')}%`,
      String(dados.contagem), sessao.rodadas.length ? `${(dados.observado * 100).toFixed(2).replace('.', ',')}%` : '—'];
    valores.forEach(valor => {
      const td = document.createElement('td');
      td.textContent = valor;
      linha.appendChild(td);
    });
    corpo.appendChild(linha);
  });
}

function atualizarTela() {
  const dados = estatisticas(sessao);
  pegar('saldo').textContent = formatar(sessao.saldo);
  pegar('saldo-progresso').style.width = `${Math.min(100, 100 * sessao.saldo / SALDO_INICIAL)}%`;
  pegar('rodadas').innerHTML = `${dados.total} <small>/ ${LIMITE_RODADAS}</small>`;
  pegar('vitorias').textContent = String(dados.vitorias);
  pegar('lucro').textContent = `${dados.lucroTotal > 0 ? '+' : ''}${formatar(dados.lucroTotal)}`;
  pegar('rtp').textContent = dados.total ? `${formatar(dados.rtp * 100)}%` : '—';
  pegar('girar').disabled = !podeJogar(sessao);
  pegar('girar10').disabled = !podeJogar(sessao);
  pegar('estado').textContent = podeJogar(sessao) ? 'PRONTO' : 'SESSÃO ENCERRADA';
  atualizarGrafico();
  atualizarHistorico();
  atualizarFrequencias();
}

function jogar(quantidade) {
  if (!podeJogar(sessao)) return;
  let ultima;
  let realizadas = 0;
  while (realizadas < quantidade && podeJogar(sessao)) {
    ultima = sortearRodada();
    registrarRodada(sessao, ultima);
    realizadas += 1;
  }
  atualizarTabuleiro(ultima);
  atualizarTela();
  const mensagem = pegar('mensagem');
  mensagem.classList.toggle('ganhou', ultima.premio > 0);
  mensagem.classList.toggle('perdeu', ultima.premio === 0);
  if (quantidade === 1) {
    mensagem.textContent = ultima.premio > 0
      ? `Combinação ${ultima.centro}! Você recebeu ${ultima.premio} créditos (lucro líquido +${ultima.lucro}).`
      : `Combinação ${ultima.centro}: sem prêmio. Lucro líquido −1 crédito.`;
  } else {
    const vitorias = sessao.rodadas.slice(-realizadas).filter(r => r.premio > 0).length;
    mensagem.textContent = `${realizadas} rodadas realizadas, ${vitorias} com prêmio. Saldo atual: ${formatar(sessao.saldo)} créditos.`;
  }
  if (!podeJogar(sessao)) {
    mensagem.textContent += sessao.saldo < 1
      ? ' Sessão encerrada: saldo insuficiente.'
      : ' Sessão encerrada: limite de 500 rodadas.';
  }
}

pegar('girar').addEventListener('click', () => jogar(1));
pegar('girar10').addEventListener('click', () => jogar(10));
pegar('reiniciar').addEventListener('click', () => {
  sessao = criarSessao();
  pegar('visor').classList.remove('vencedor');
  pegar('mensagem').classList.remove('ganhou', 'perdeu');
  pegar('mensagem').textContent = 'Nova sessão iniciada: 100 créditos fictícios e até 500 rodadas.';
  const casas = pegar('grade').children;
  'AAABBBCCC'.split('').forEach((simbolo, i) => { casas[i].textContent = simbolo; });
  pegar('visor').setAttribute('aria-label', 'Tabuleiro inicial. Nenhuma rodada realizada.');
  atualizarTela();
});

atualizarTela();
