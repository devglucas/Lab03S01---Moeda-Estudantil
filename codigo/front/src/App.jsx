import { useEffect, useState } from "react";

import { EVENTO_SESSAO_EXPIRADA } from "./api.js";
import Cadastro from "./pages/Cadastro.jsx";
import CatalogoVantagens from "./pages/CatalogoVantagens.jsx";
import Extrato from "./pages/Extrato.jsx";
import Login from "./pages/Login.jsx";
import Transacao from "./pages/Transacao.jsx";
import Vantagem from "./pages/Vantagem.jsx";
import { encerrarSessao, iniciarSessao, sessaoAtual } from "./sessao.js";

const ABAS_VISITANTE = [
  { id: "entrar", rotulo: "Entrar", Pagina: Login },
  { id: "cadastro", rotulo: "Criar conta", Pagina: Cadastro },
];

// Cada perfil só vê as funcionalidades que são responsabilidade dele.
const ABAS_POR_TIPO = {
  aluno: [
    { id: "vantagens", rotulo: "Vantagens", Pagina: CatalogoVantagens },
    { id: "extrato", rotulo: "Extrato", Pagina: Extrato },
  ],
  professor: [
    { id: "enviar", rotulo: "Enviar moedas", Pagina: Transacao },
    { id: "extrato", rotulo: "Extrato", Pagina: Extrato },
  ],
  empresa: [{ id: "vantagens", rotulo: "Minhas vantagens", Pagina: Vantagem }],
};

export default function App() {
  const [sessao, setSessao] = useState(sessaoAtual);
  const [abaId, setAbaId] = useState(null);
  // Mensagem mostrada na tela de login (conta criada, sessão expirada).
  const [aviso, setAviso] = useState(null);

  useEffect(() => {
    function expirou() {
      setSessao(null);
      setAbaId("entrar");
      setAviso({ tipo: "erro", texto: "Sua sessão expirou. Entre novamente." });
    }
    window.addEventListener(EVENTO_SESSAO_EXPIRADA, expirou);
    return () => window.removeEventListener(EVENTO_SESSAO_EXPIRADA, expirou);
  }, []);

  const usuario = sessao?.usuario ?? null;
  const abas = (usuario && ABAS_POR_TIPO[usuario.tipo]) || ABAS_VISITANTE;
  const abaAtual = abas.find((aba) => aba.id === abaId) ?? abas[0];
  const { Pagina } = abaAtual;

  function entrar(novaSessao) {
    iniciarSessao(novaSessao);
    setSessao(novaSessao);
    setAbaId(null);
    setAviso(null);
  }

  function sair() {
    encerrarSessao();
    setSessao(null);
    setAbaId(null);
    setAviso(null);
  }

  function cadastrado() {
    setAbaId("entrar");
    setAviso({ tipo: "sucesso", texto: "Conta criada. Entre com seu e-mail e senha." });
  }

  return (
    <>
      <header className="topo">
        <h1>Moeda Estudantil</h1>
        <nav>
          {abas.map((aba) => (
            <button
              key={aba.id}
              type="button"
              className={aba.id === abaAtual.id ? "aba ativa" : "aba"}
              onClick={() => setAbaId(aba.id)}
            >
              {aba.rotulo}
            </button>
          ))}
        </nav>
        {usuario && (
          <div className="usuario-logado">
            <span>{usuario.nome}</span>
            <button type="button" className="secundario" onClick={sair}>
              Sair
            </button>
          </div>
        )}
      </header>

      <main>
        <Pagina
          key={abaAtual.id}
          usuario={usuario}
          aviso={aviso}
          onLogin={entrar}
          onCadastrado={cadastrado}
          onVoltar={() => setAbaId("entrar")}
        />
      </main>
    </>
  );
}
