// Sessão do usuário logado: { token, usuario }. Fica em memória e também no
// localStorage, para sobreviver a um recarregamento da página.
const CHAVE = "sessao";

function ler() {
  try {
    return JSON.parse(localStorage.getItem(CHAVE));
  } catch {
    return null;
  }
}

let atual = ler();

export function sessaoAtual() {
  return atual;
}

export function iniciarSessao(sessao) {
  atual = sessao;
  try {
    localStorage.setItem(CHAVE, JSON.stringify(sessao));
  } catch {
    // Sem armazenamento disponível a sessão dura só até recarregar a página.
  }
}

export function encerrarSessao() {
  atual = null;
  try {
    localStorage.removeItem(CHAVE);
  } catch {
    // Nada a limpar.
  }
}
