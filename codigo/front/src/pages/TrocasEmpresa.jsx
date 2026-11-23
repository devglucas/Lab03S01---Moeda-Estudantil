import { useEffect, useState } from "react";

import { trocasApi } from "../api.js";
import Aviso from "../components/Aviso.jsx";
import Campo from "../components/Campo.jsx";

// Trocas das vantagens da empresa logada. O campo de busca serve para conferir
// o código do cupom que o aluno apresenta ao retirar o benefício.
export default function TrocasEmpresa() {
  const [trocas, setTrocas] = useState([]);
  const [busca, setBusca] = useState("");
  const [aviso, setAviso] = useState(null);

  useEffect(() => {
    trocasApi
      .daEmpresa()
      .then(setTrocas)
      .catch((erro) => setAviso({ tipo: "erro", texto: erro.message }));
  }, []);

  const termo = busca.trim().toUpperCase();
  const visiveis = termo ? trocas.filter((troca) => troca.codigo.includes(termo)) : trocas;

  return (
    <section className="pagina">
      <div className="cartao">
        <h2>Trocas das minhas vantagens</h2>
        <Aviso aviso={aviso} />

        <div className="grade">
          <Campo
            rotulo="Conferir código do cupom"
            nome="busca"
            placeholder="ABCD-2345"
            value={busca}
            onChange={(evento) => setBusca(evento.target.value)}
          />
        </div>

        {visiveis.length === 0 ? (
          <p className="vazio">
            {termo ? "Nenhuma troca com esse código." : "Nenhuma troca realizada ainda."}
          </p>
        ) : (
          <div className="tabela-rolagem">
            <table>
              <thead>
                <tr>
                  <th>Data</th>
                  <th>Código</th>
                  <th>Aluno</th>
                  <th>Vantagem</th>
                  <th className="numero">Valor</th>
                </tr>
              </thead>
              <tbody>
                {visiveis.map((troca) => (
                  <tr key={troca.id}>
                    <td>{new Date(troca.data).toLocaleString("pt-BR")}</td>
                    <td className="codigo">{troca.codigo}</td>
                    <td>{troca.alunoNome}</td>
                    <td>{troca.vantagemNome}</td>
                    <td className="numero">{troca.valor}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}
