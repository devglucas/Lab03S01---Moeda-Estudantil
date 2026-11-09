import { useEffect, useState } from "react";

import { alunosApi, extratoApi, professorApi } from "../api.js";
import Aviso from "../components/Aviso.jsx";
import Campo from "../components/Campo.jsx";

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

export default function Extrato() {
  const [professores, setProfessores] = useState([]);
  const [alunos, setAlunos] = useState([]);
  const [perfil, setPerfil] = useState("aluno");
  const [usuarioId, setUsuarioId] = useState("");
  const [extrato, setExtrato] = useState(null);
  const [aviso, setAviso] = useState(null);

  useEffect(() => {
    async function carregarUsuarios() {
      try {
        const [listaProfessores, listaAlunos] = await Promise.all([
          professorApi.listar(),
          alunosApi.listar(),
        ]);
        setProfessores(listaProfessores);
        setAlunos(listaAlunos);
      } catch (erro) {
        setAviso({ tipo: "erro", texto: erro.message });
      }
    }
    carregarUsuarios();
  }, []);

  useEffect(() => {
    if (!usuarioId) return undefined;

    // Evita que uma resposta atrasada sobrescreva a do usuário escolhido depois.
    let ignorar = false;
    extratoApi[perfil](usuarioId)
      .then((dados) => {
        if (!ignorar) setExtrato(dados);
      })
      .catch((erro) => {
        if (!ignorar) setAviso({ tipo: "erro", texto: erro.message });
      });
    return () => {
      ignorar = true;
    };
  }, [perfil, usuarioId]);

  function escolherPerfil(evento) {
    setPerfil(evento.target.value);
    setUsuarioId("");
    setExtrato(null);
    setAviso(null);
  }

  function escolherUsuario(evento) {
    setUsuarioId(evento.target.value);
    setExtrato(null);
    setAviso(null);
  }

  const usuarios = perfil === "professor" ? professores : alunos;

  return (
    <section className="pagina">
      <div className="cartao">
        <h2>Consultar extrato</h2>
        <Aviso aviso={aviso} />

        <div className="grade">
          <Campo rotulo="Perfil">
            <select name="perfil" value={perfil} onChange={escolherPerfil}>
              <option value="aluno">Aluno</option>
              <option value="professor">Professor</option>
            </select>
          </Campo>

          <Campo rotulo={perfil === "professor" ? "Professor" : "Aluno"}>
            <select name="usuarioId" value={usuarioId} onChange={escolherUsuario}>
              <option value="">Selecione</option>
              {usuarios.map((usuario) => (
                <option key={usuario.id} value={usuario.id}>
                  {usuario.nome}
                </option>
              ))}
            </select>
          </Campo>
        </div>
      </div>

      {extrato && (
        <div className="cartao">
          <h2>Extrato</h2>
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
