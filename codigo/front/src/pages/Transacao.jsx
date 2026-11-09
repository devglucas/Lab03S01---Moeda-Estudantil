import { useEffect, useState } from "react";

import { alunosApi, professorApi, transacoesApi } from "../api.js";
import Aviso from "../components/Aviso.jsx";
import Campo from "../components/Campo.jsx";

const VAZIO = { professorId: "", alunoId: "", valor: "", mensagem: "" };

export default function Transacoes() {
  const [transacoes, setTransacoes] = useState([]);
  const [professores, setProfessores] = useState([]);
  const [alunos, setAlunos] = useState([]);
  const [form, setForm] = useState(VAZIO);
  const [erros, setErros] = useState({});
  const [aviso, setAviso] = useState(null);
  const [salvando, setSalvando] = useState(false);

  async function carregarTransacoes() {
    try {
      setTransacoes(await transacoesApi.listar());
    } catch (erro) {
      setAviso({ tipo: "erro", texto: erro.message });
    }
  }

  async function carregarProfessores() {
    try {
      setProfessores(await professorApi.listar());
    } catch (erro) {
      setAviso({ tipo: "erro", texto: erro.message });
    }
  }

  async function carregarAlunos(professorId) {
    const professor = professores.find((p) => String(p.id) === professorId);
    if (!professor) {
      setAlunos([]);
      return;
    }
    try {
      const lista = await alunosApi.listar();
      setAlunos(lista.filter((a) => a.instituicaoId === professor.instituicaoId));
    } catch (erro) {
      setAviso({ tipo: "erro", texto: erro.message });
    }
  }

  useEffect(() => {
    carregarTransacoes();
    carregarProfessores();
  }, []);

  function alterar(evento) {
    const { name, value } = evento.target;
    setForm((atual) => ({
      ...atual,
      [name]: value,
      ...(name === "professorId" ? { alunoId: "" } : {}),
    }));
    if (name === "professorId") carregarAlunos(value);
  }

  function limpar() {
    setForm(VAZIO);
    setAlunos([]);
    setErros({});
  }

  async function salvar(evento) {
    evento.preventDefault();
    setSalvando(true);
    setAviso(null);
    setErros({});

    const dados = {
      professorId: Number(form.professorId) || null,
      alunoId: Number(form.alunoId) || null,
      valor: Number(form.valor),
      mensagem: form.mensagem,
    };

    try {
      await transacoesApi.criar(dados);
      setAviso({ tipo: "sucesso", texto: "Moedas enviadas com sucesso." });
      limpar();
      await Promise.all([carregarTransacoes(), carregarProfessores()]); // tabela e saldos
    } catch (erro) {
      setErros(erro.campos ?? {});
      setAviso({ tipo: "erro", texto: erro.message });
    } finally {
      setSalvando(false);
    }
  }

  return (
    <section className="pagina">
      <form className="cartao" onSubmit={salvar} noValidate>
        <h2>Enviar moedas</h2>
        <Aviso aviso={aviso} />

        <div className="grade">
          <Campo rotulo="Professor" erro={erros.professorId}>
            <select name="professorId" value={form.professorId} onChange={alterar}>
              <option value="">Selecione</option>
              {professores.map((professor) => (
                <option key={professor.id} value={professor.id}>
                  {professor.nome} (saldo: {professor.saldo})
                </option>
              ))}
            </select>
          </Campo>

          <Campo rotulo="Aluno" erro={erros.alunoId}>
            <select
              name="alunoId"
              value={form.alunoId}
              onChange={alterar}
              disabled={!form.professorId}
            >
              <option value="">
                {form.professorId ? "Selecione" : "Escolha o professor primeiro"}
              </option>
              {alunos.map((aluno) => (
                <option key={aluno.id} value={aluno.id}>
                  {aluno.nome}
                </option>
              ))}
            </select>
          </Campo>

          <Campo
            rotulo="Valor (moedas)"
            nome="valor"
            type="number"
            min={1}
            step={1}
            value={form.valor}
            onChange={alterar}
            erro={erros.valor}
          />

          <Campo rotulo="Motivo do reconhecimento" erro={erros.mensagem}>
            <textarea
              name="mensagem"
              rows={3}
              maxLength={500}
              placeholder="Ex.: Ótima participação em aula"
              value={form.mensagem}
              onChange={alterar}
            />
          </Campo>
        </div>

        <div className="acoes">
          <button type="button" className="secundario" onClick={limpar}>
            Limpar
          </button>
          <button type="submit" disabled={salvando}>
            Enviar moedas
          </button>
        </div>
      </form>

      <div className="cartao">
        <h2>Transações realizadas</h2>
        {transacoes.length === 0 ? (
          <p className="vazio">Nenhuma transação realizada.</p>
        ) : (
          <div className="tabela-rolagem">
            <table>
              <thead>
                <tr>
                  <th>Data</th>
                  <th>Professor</th>
                  <th>Aluno</th>
                  <th className="numero">Valor</th>
                  <th>Mensagem</th>
                </tr>
              </thead>
              <tbody>
                {transacoes.map((transacao) => (
                  <tr key={transacao.id}>
                    <td>{new Date(transacao.data).toLocaleString("pt-BR")}</td>
                    <td>{transacao.professorNome}</td>
                    <td>{transacao.alunoNome}</td>
                    <td className="numero">{transacao.valor}</td>
                    <td>{transacao.mensagem}</td>
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