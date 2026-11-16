import { useEffect, useState } from "react";

import { extratoApi } from "../api.js";
import Aviso from "../components/Aviso.jsx";

// Como cada transação aparece no extrato de cada perfil. O sinal do valor
// depende do perfil: o mesmo envio é saída para o professor e entrada para o aluno.
function descrever(transacao, perfil) {
  if (transacao.tipo === "troca") {
    return { descricao: "Troca por vantagem", detalhe: `Cupom ${transacao.codigo}`, sinal: "-" };
  }
  if (perfil === "professor") {
    return { descricao: `Envio para ${transacao.alunoNome}`, detalhe: transacao.mensagem, sinal: "-" };
  }
  return { descricao: `Recebido de ${transacao.professorNome}`, detalhe: transacao.mensagem, sinal: "+" };
}

export default function Extrato({ usuario }) {
  const [extrato, setExtrato] = useState(null);
  const [aviso, setAviso] = useState(null);

  useEffect(() => {
    extratoApi
      .meu()
      .then(setExtrato)
      .catch((erro) => setAviso({ tipo: "erro", texto: erro.message }));
  }, []);

  const perfil = usuario.tipo;

  return (
    <section className="pagina">
      <Aviso aviso={aviso} />

      {extrato && (
        <div className="cartao">
          <h2>Meu extrato</h2>
          <p className="saldo">Saldo atual: {extrato.saldo} moeda(s)</p>

          {extrato.transacoes.length === 0 ? (
            <p className="vazio">Nenhuma transação encontrada.</p>
          ) : (
            <div className="tabela-rolagem">
              <table>
                <thead>
                  <tr>
                    <th>Data</th>
                    <th>Descrição</th>
                    <th>Motivo</th>
                    <th className="numero">Valor</th>
                  </tr>
                </thead>
                <tbody>
                  {extrato.transacoes.map((transacao) => {
                    const { descricao, detalhe, sinal } = descrever(transacao, perfil);
                    return (
                      <tr key={transacao.id}>
                        <td>{new Date(transacao.data).toLocaleString("pt-BR")}</td>
                        <td>{descricao}</td>
                        <td>{detalhe}</td>
                        <td className="numero">
                          {sinal}
                          {transacao.valor}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
