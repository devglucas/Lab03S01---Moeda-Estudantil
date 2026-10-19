import { useEffect, useState } from "react";

import { alunosApi, instituicoesApi } from "../api.js";
import Aviso from "../components/Aviso.jsx";
import Campo from "../components/Campo.jsx";
import { formatarCpf } from "../formatacao.js";

const VAZIO = {
  nome: "",
  email: "",
  cpf: "",
  rg: "",
  endereco: "",
  curso: "",
  instituicaoId: "",
  login: "",
  senha: "",
};

export default function Alunos() {
  const [alunos, setAlunos] = useState([]);
  const [instituicoes, setInstituicoes] = useState([]);
  const [form, setForm] = useState(VAZIO);
  const [editandoId, setEditandoId] = useState(null);
  const [erros, setErros] = useState({});
  const [aviso, setAviso] = useState(null);
  const [salvando, setSalvando] = useState(false);

  async function carregar() {
    try {
      const [listaAlunos, listaInstituicoes] = await Promise.all([
        alunosApi.listar(),
        instituicoesApi.listar(),
      ]);
      setAlunos(listaAlunos);
      setInstituicoes(listaInstituicoes);
    } catch (erro) {
      setAviso({ tipo: "erro", texto: erro.message });
    }
  }

  useEffect(() => {
    carregar();
  }, []);

  function alterar(evento) {
    const { name, value } = evento.target;
    setForm((atual) => ({ ...atual, [name]: value }));
  }

  function limpar() {
    setForm(VAZIO);
    setEditandoId(null);
    setErros({});
  }

  function editar(aluno) {
    setForm({
      nome: aluno.nome,
      email: aluno.email,
      cpf: formatarCpf(aluno.cpf),
      rg: aluno.rg,
      endereco: aluno.endereco,
      curso: aluno.curso,
      instituicaoId: String(aluno.instituicaoId),
      login: aluno.login,
      senha: "",
    });
    setEditandoId(aluno.id);
    setErros({});
    setAviso(null);
  }

  async function salvar(evento) {
    evento.preventDefault();
    setSalvando(true);
    setAviso(null);

    const dados = { ...form, instituicaoId: Number(form.instituicaoId) || null };

    try {
      if (editandoId) {
        await alunosApi.atualizar(editandoId, dados);
        setAviso({ tipo: "sucesso", texto: "Aluno atualizado com sucesso." });
      } else {
        await alunosApi.criar(dados);
        setAviso({ tipo: "sucesso", texto: "Aluno cadastrado com sucesso." });
      }
      limpar();
      await carregar();
    } catch (erro) {
      setErros(erro.campos ?? {});
      setAviso({ tipo: "erro", texto: erro.message });
    } finally {
      setSalvando(false);
    }
  }

  async function remover(aluno) {
    if (!window.confirm(`Remover o aluno ${aluno.nome}?`)) return;

    try {
      await alunosApi.remover(aluno.id);
      if (editandoId === aluno.id) limpar();
      setAviso({ tipo: "sucesso", texto: "Aluno removido." });
      await carregar();
    } catch (erro) {
      setAviso({ tipo: "erro", texto: erro.message });
    }
  }

  return (
    <section className="pagina">
      <form className="cartao" onSubmit={salvar} noValidate>
        <h2>{editandoId ? "Editar aluno" : "Cadastrar aluno"}</h2>
        <Aviso aviso={aviso} />

        <div className="grade">
          <Campo rotulo="Nome" nome="nome" value={form.nome} onChange={alterar} erro={erros.nome} />
          <Campo rotulo="E-mail" nome="email" type="email" value={form.email} onChange={alterar} erro={erros.email} />
          <Campo rotulo="CPF" nome="cpf" placeholder="000.000.000-00" value={form.cpf} onChange={alterar} erro={erros.cpf} />
          <Campo rotulo="RG" nome="rg" value={form.rg} onChange={alterar} erro={erros.rg} />
          <Campo rotulo="Endereço" nome="endereco" value={form.endereco} onChange={alterar} erro={erros.endereco} />
          <Campo rotulo="Curso" nome="curso" value={form.curso} onChange={alterar} erro={erros.curso} />
          <Campo rotulo="Instituição de ensino" erro={erros.instituicaoId}>
            <select name="instituicaoId" value={form.instituicaoId} onChange={alterar}>
              <option value="">Selecione</option>
              {instituicoes.map((instituicao) => (
                <option key={instituicao.id} value={instituicao.id}>
                  {instituicao.nome}
                </option>
              ))}
            </select>
          </Campo>
          <Campo
            rotulo="Login"
            nome="login"
            value={form.login}
            onChange={alterar}
            erro={erros.login}
            disabled={Boolean(editandoId)}
          />
          <Campo
            rotulo={editandoId ? "Nova senha (opcional)" : "Senha"}
            nome="senha"
            type="password"
            value={form.senha}
            onChange={alterar}
            erro={erros.senha}
          />
        </div>

        <div className="acoes">
          {editandoId && (
            <button type="button" className="secundario" onClick={limpar}>
              Cancelar
            </button>
          )}
          <button type="submit" disabled={salvando}>
            {editandoId ? "Salvar alterações" : "Cadastrar"}
          </button>
        </div>
      </form>

      <div className="cartao">
        <h2>Alunos cadastrados</h2>
        {alunos.length === 0 ? (
          <p className="vazio">Nenhum aluno cadastrado.</p>
        ) : (
          <div className="tabela-rolagem">
            <table>
              <thead>
                <tr>
                  <th>Nome</th>
                  <th>E-mail</th>
                  <th>CPF</th>
                  <th>Curso</th>
                  <th>Instituição</th>
                  <th className="numero">Saldo</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {alunos.map((aluno) => (
                  <tr key={aluno.id}>
                    <td>{aluno.nome}</td>
                    <td>{aluno.email}</td>
                    <td>{formatarCpf(aluno.cpf)}</td>
                    <td>{aluno.curso}</td>
                    <td>{aluno.instituicaoNome}</td>
                    <td className="numero">{aluno.saldo}</td>
                    <td className="linha-acoes">
                      <button type="button" className="secundario" onClick={() => editar(aluno)}>
                        Editar
                      </button>
                      <button type="button" className="perigo" onClick={() => remover(aluno)}>
                        Excluir
                      </button>
                    </td>
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
