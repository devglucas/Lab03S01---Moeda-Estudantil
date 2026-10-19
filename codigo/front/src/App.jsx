import { useState } from "react";

import Alunos from "./pages/Alunos.jsx";
import Empresas from "./pages/Empresas.jsx";

const ABAS = [
  { id: "alunos", rotulo: "Alunos", Pagina: Alunos },
  { id: "empresas", rotulo: "Empresas parceiras", Pagina: Empresas },
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
