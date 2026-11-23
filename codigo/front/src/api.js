// Comunicação com a API Flask (back-end).
import { encerrarSessao, sessaoAtual } from "./sessao.js";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:5000/api";
// As fotos das vantagens ficam fora de /api, em /uploads.
const SERVIDOR_URL = API_URL.replace(/\/api\/?$/, "");

export const EVENTO_SESSAO_EXPIRADA = "sessao-expirada";

export class ErroApi extends Error {
  constructor(mensagem, campos = {}) {
    super(mensagem);
    this.campos = campos;
  }
}

async function requisicao(caminho, opcoes = {}) {
  const token = sessaoAtual()?.token;
  const headers = { ...opcoes.headers };
  // O FormData define o próprio Content-Type (com o boundary do multipart).
  if (!(opcoes.body instanceof FormData)) headers["Content-Type"] = "application/json";
  if (token) headers.Authorization = `Bearer ${token}`;

  let resposta;
  try {
    resposta = await fetch(`${API_URL}${caminho}`, { ...opcoes, headers });
  } catch {
    throw new ErroApi("Não foi possível conectar ao servidor.");
  }

  if (resposta.status === 204) return null;

  const corpo = await resposta.json().catch(() => null);
  if (!resposta.ok) {
    // Token vencido ou de um usuário removido: volta para a tela de login.
    if (resposta.status === 401 && token) {
      encerrarSessao();
      window.dispatchEvent(new Event(EVENTO_SESSAO_EXPIRADA));
    }
    throw new ErroApi(corpo?.erro ?? "Erro inesperado no servidor.", corpo?.campos);
  }
  return corpo;
}

function enviarJson(caminho, metodo, dados) {
  return requisicao(caminho, { method: metodo, body: JSON.stringify(dados) });
}

function recurso(caminho) {
  return {
    listar: () => requisicao(caminho),
    criar: (dados) => enviarJson(caminho, "POST", dados),
    atualizar: (id, dados) => enviarJson(`${caminho}/${id}`, "PUT", dados),
    remover: (id) => requisicao(`${caminho}/${id}`, { method: "DELETE" }),
  };
}

export function urlDaFoto(nome) {
  return nome ? `${SERVIDOR_URL}/uploads/${nome}` : null;
}

export const authApi = {
  entrar: (dados) => enviarJson("/auth/login", "POST", dados),
  eu: () => requisicao("/auth/eu"),
};
export const transacoesApi = {
  enviar: (dados) => enviarJson("/transacoes", "POST", dados),
};
export const extratoApi = {
  meu: () => requisicao("/transacoes/extrato"),
};
// Vantagens vão como FormData por causa da foto.
export const vantagemApi = {
  catalogo: () => requisicao("/vantagens"),
  minhas: () => requisicao("/vantagens/minhas"),
  criar: (formulario) => requisicao("/vantagens", { method: "POST", body: formulario }),
  atualizar: (id, formulario) =>
    requisicao(`/vantagens/${id}`, { method: "PUT", body: formulario }),
  remover: (id) => requisicao(`/vantagens/${id}`, { method: "DELETE" }),
};
export const trocasApi = {
  trocar: (vantagemId) => enviarJson("/trocas", "POST", { vantagemId }),
  daEmpresa: () => requisicao("/trocas"),
};
export const professorApi = recurso("/professores");
export const alunosApi = recurso("/alunos");
export const empresasApi = recurso("/empresas");
export const instituicoesApi = recurso("/instituicoes");
