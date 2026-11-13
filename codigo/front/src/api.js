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
    const headers = { ...opcoes.headers };

    // FormData precisa definir seu próprio Content-Type e boundary
    if (!(opcoes.body instanceof FormData)) {
      headers["Content-Type"] = "application/json";
    }

    resposta = await fetch(`${API_URL}${caminho}`, {
      ...opcoes,
      headers,
    });

  } catch {
    throw new ErroApi("Não foi possível conectar ao servidor.");
  }

  if (resposta.status === 204) return null;

  const corpo = await resposta.json().catch(() => null);

  if (!resposta.ok) {
    throw new ErroApi(
      corpo?.erro ?? "Erro inesperado no servidor.",
      corpo?.campos
    );
  }

  return corpo;
}


function recursoForm(caminho) {
  return {
    listar: () => requisicao(caminho),

    criar: (dados) =>
      requisicao(caminho, {
        method: "POST",
        body: dados instanceof FormData
          ? dados
          : JSON.stringify(dados),
      }),

    atualizar: (id, dados) =>
      requisicao(`${caminho}/${id}`, {
        method: "PUT",
        body: dados instanceof FormData
          ? dados
          : JSON.stringify(dados),
      }),

    remover: (id) =>
      requisicao(`${caminho}/${id}`, { method: "DELETE" }),
  };
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

export const transacoesApi = recurso("/transacoes");
export const professorApi = recurso("/professores");
export const alunosApi = recurso("/alunos");
export const empresasApi = recurso("/empresas");
export const instituicoesApi = recurso("/instituicoes");
export const vantagemApi = recursoForm("/vantagens");
