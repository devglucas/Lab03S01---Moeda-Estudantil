import { useEffect, useState } from "react";

import Alunos from "./pages/Alunos.jsx";
import Empresas from "./pages/Empresas.jsx";
import Extrato from "./pages/Extrato.jsx";
import Professores from "./pages/Professores.jsx";
import Transacao from "./pages/Transacao.jsx";
import Login from "./pages/Login.jsx";
import Cadastro from "./pages/Cadastro.jsx";
import Vantagem from "./pages/Vantagem.jsx";

const ABAS_SEM_LOGIN = [
  { id: "entrar", rotulo: "Entrar", Pagina: Login },
  { id: "cadastro", rotulo: "Cadastro", Pagina: Cadastro },
];

const ABAS_ALUNO = [
  { id: "regatarVantagem", rotulo: "Restagar Vantagem", Pagina: Transacao },
  { id: "extrato", rotulo: "Extrato", Pagina: Extrato }
];
const ABAS_EMPRESA = [{ id: "cadastroVantagem", rotulo: "Cadastro Vantagem", Pagina: Vantagem }];

const ABAS_PROFESSOR = [
  { id: "alunos", rotulo: "Alunos", Pagina: Alunos },
  { id: "empresas", rotulo: "Empresas parceiras", Pagina: Empresas },
  { id: "professores", rotulo: "Professores", Pagina: Professores },
  { id: "transacoes", rotulo: "Transacoes", Pagina: Transacao },
  { id: "extrato", rotulo: "Extrato", Pagina: Extrato },
];

// Qualquer tipo logado que não seja aluno usa as abas de professor (como antes).
function abasDoTipo(tipo) {
  console.log(tipo)
  if (tipo == null) return ABAS_SEM_LOGIN;
  if (tipo == "aluno") return ABAS_ALUNO;
  if (tipo == "professor") return ABAS_PROFESSOR;
  if (tipo == "empresa") return ABAS_EMPRESA;
  return ABAS_SEM_LOGIN;
}

// Usuário logado: { email, tipo }. Fica na chave "usuario" (a lista de cadastros é "usuarios").
function lerUsuario() {
  try {
    return JSON.parse(localStorage.getItem("usuario"));
  } catch {
    return null;
  }
}

export default function App() {
  // Lido direto do localStorage na primeira renderização (sem piscar a tela de login).
  let usuario = null;
  const [abaId, setAbaId] = useState(null);
  const [abas, setAbas] = useState(ABAS_SEM_LOGIN);

  let tipo = null;
  const [tipoState, setTipoState] = useState(null);

  // let abas = abasDoTipo(tipo);
  // Se a aba escolhida não existe no conjunto atual (ex.: após login/logout), usa a primeira.
  const abaAtual = abas.find((aba) => aba.id === abaId) ?? abas[0];
  const { Pagina } = abaAtual;

  // function entrar({ email, tipo }) {
  //   const logado = { email, tipo };
  //   localStorage.setItem("usuario", JSON.stringify(logado));
  //   setUsuario(logado);
  //   setAbaId(null);
  // }

  useEffect(() => {
    usuario = lerUsuario()
    console.log(usuario)
    tipo = usuario?.tipo ?? null
    setTipoState(tipo)
    console.log(tipo)
    // tipo = usuario?.tipo ?? null
    setAbas(abasDoTipo(tipo))
    // console.log(tipo)
    // console.log(abas)
  }, [])

  function sair() {
    localStorage.removeItem("usuario");
    usuario = null;
    setAbaId(null);
    tipoState(null)
    tipo = null
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
          {tipoState != null && (
            <button type="button" className="aba" onClick={sair}>
              Sair
            </button>
          )}
        </nav>
      </header>

      <main>
        <Pagina
        // onLogin={entrar}
        // onCadastrado={() => setAbaId("entrar")}
        // onVoltar={() => setAbaId("entrar")}
        />
      </main>
    </>
  );
}