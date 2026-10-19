// Comunicação com a API Flask (back-end).
const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:5000/api";

export class ErroApi extends Error {
  constructor(mensagem, campos = {}) {
    super(mensagem);
    this.campos = campos;
  }
}

async function requisicao(caminho, opcoes = {}) {
  let resposta;
  try {
    resposta = await fetch(`${API_URL}${caminho}`, {
      headers: { "Content-Type": "application/json" },
      ...opcoes,
    });
  } catch {
    throw new ErroApi("Não foi possível conectar ao servidor.");
  }

  if (resposta.status === 204) return null;

  const corpo = await resposta.json().catch(() => null);
  if (!resposta.ok) {
    throw new ErroApi(corpo?.erro ?? "Erro inesperado no servidor.", corpo?.campos);
  }
  return corpo;
}

function recurso(caminho) {
  return {
    listar: () => requisicao(caminho),
    criar: (dados) =>
      requisicao(caminho, { method: "POST", body: JSON.stringify(dados) }),
    atualizar: (id, dados) =>
      requisicao(`${caminho}/${id}`, { method: "PUT", body: JSON.stringify(dados) }),
    remover: (id) => requisicao(`${caminho}/${id}`, { method: "DELETE" }),
  };
}

export const alunosApi = recurso("/alunos");
export const empresasApi = recurso("/empresas");
export const instituicoesApi = recurso("/instituicoes");
