import { useState } from "react";

import Alunos from "./pages/Alunos.jsx";
import Empresas from "./pages/Empresas.jsx";
import Extrato from "./pages/Extrato.jsx";
import Professores from "./pages/Professores.jsx";
import Transacao from "./pages/Transacao.jsx";

const ABAS = [
  { id: "alunos", rotulo: "Alunos", Pagina: Alunos },
  { id: "empresas", rotulo: "Empresas parceiras", Pagina: Empresas },
  { id: "professores", rotulo: "Professores", Pagina: Professores },
  { id: "transacoes", rotulo: "Transações", Pagina: Transacao },
  { id: "extrato", rotulo: "Extrato", Pagina: Extrato },
];

export default function App() {
  const [abaAtual, setAbaAtual] = useState(ABAS[0].id);
  const { Pagina } = ABAS.find((aba) => aba.id === abaAtual);

  return (
    <>
      <header className="topo">
        <h1>Moeda Estudantil</h1>
        <nav>
          {ABAS.map((aba) => (
            <button
              key={aba.id}
              type="button"
              className={aba.id === abaAtual ? "aba ativa" : "aba"}
              onClick={() => setAbaAtual(aba.id)}
            >
              {aba.rotulo}
            </button>
          ))}
        </nav>
      </header>

      <main>
        <Pagina />
      </main>
    </>
  );
}
