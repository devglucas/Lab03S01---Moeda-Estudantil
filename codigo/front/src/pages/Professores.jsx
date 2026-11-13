import { useEffect, useState } from "react";

import { professorApi, instituicoesApi } from "../api.js";
import Aviso from "../components/Aviso.jsx";
import Campo from "../components/Campo.jsx";
import { apenasDigitos, mascaraCpf } from "../formatacao.js";

const VAZIO = {
  nome: "",
  email: "",
  cpf: "",
  departamento: "",
  instituicaoId: "",
  senha: "",
};

const MASCARAS = { cpf: mascaraCpf };

export default function Professores() {
  const [professores, setProfessores] = useState([]);
  const [instituicoes, setInstituicoes] = useState([]);
  const [form, setForm] = useState(VAZIO);
  const [editandoId, setEditandoId] = useState(null);
  const [erros, setErros] = useState({});
  const [aviso, setAviso] = useState(null);
  const [salvando, setSalvando] = useState(false);

  async function carregar() {
    try {
      const [listaProfessores, listaInstituicoes] = await Promise.all([
        professorApi.listar(),
        instituicoesApi.listar(),
      ]);
      setProfessores(listaProfessores);
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
    const mascara = MASCARAS[name];
    setForm((atual) => ({ ...atual, [name]: mascara ? mascara(value) : value }));
  }

  function limpar() {
    setForm(VAZIO);
    setEditandoId(null);
    setErros({});
  }

  function editar(professor) {
    setForm({
      nome: professor.nome,
      email: professor.email,
      cpf: mascaraCpf(professor.cpf),
      departamento: professor.departamento,
      instituicaoId: String(professor.instituicaoId),
      senha: "",
    });
    setEditandoId(professor.id);
    setErros({});
    setAviso(null);
  }

  async function salvar(evento) {
    evento.preventDefault();
    setSalvando(true);
    setAviso(null);

    // A pontuação do CPF é só visual: a API recebe apenas os dígitos.
    const dados = {
      ...form,
      cpf: apenasDigitos(form.cpf),
      instituicaoId: Number(form.instituicaoId) || null,
    };

    try {
      if (editandoId) {
        await professorApi.atualizar(editandoId, dados);
        setAviso({ tipo: "sucesso", texto: "Professor atualizado com sucesso." });
      } else {
        await professorApi.criar(dados);
        setAviso({ tipo: "sucesso", texto: "Professor cadastrado com sucesso." });
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

  async function remover(professor) {
    if (!window.confirm(`Remover o professor ${professor.nome}?`)) return;

    try {
      await professorApi.remover(professor.id);
      if (editandoId === professor.id) limpar();
      setAviso({ tipo: "sucesso", texto: "Professor removido." });
      await carregar();
    } catch (erro) {
      setAviso({ tipo: "erro", texto: erro.message });
    }
  }

  return (
    <section className="pagina">
      <form className="cartao" onSubmit={salvar} noValidate>
        <h2>{editandoId ? "Editar professor" : "Cadastrar professor"}</h2>
        <Aviso aviso={aviso} />

        <div className="grade">
          <Campo rotulo="Nome" nome="nome" value={form.nome} onChange={alterar} erro={erros.nome} />
          <Campo rotulo="E-mail" nome="email" type="email" value={form.email} onChange={alterar} erro={erros.email} />
          <Campo rotulo="CPF" nome="cpf" placeholder="000.000.000-00" inputMode="numeric" maxLength={14} value={form.cpf} onChange={alterar} erro={erros.cpf} />
          <Campo rotulo="Departamento" nome="departamento" placeholder="Matemática" maxLength={120} value={form.departamento} onChange={alterar} erro={erros.departamento} />
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
        <h2>Professores cadastrados</h2>
        {professores.length === 0 ? (
          <p className="vazio">Nenhum professor cadastrado.</p>
        ) : (
          <div className="tabela-rolagem">
            <table>
              <thead>
                <tr>
                  <th>Nome</th>
                  <th>E-mail</th>
                  <th>CPF</th>
                  <th>Departamento</th>
                  <th>Instituição</th>
                  <th className="numero">Saldo</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {professores.map((professor) => (
                  <tr key={professor.id}>
                    <td>{professor.nome}</td>
                    <td>{professor.email}</td>
                    <td>{mascaraCpf(professor.cpf)}</td>
                    <td>{professor.departamento}</td>
                    <td>{professor.instituicaoNome}</td>
                    <td className="numero">{professor.saldo}</td>
                    <td className="linha-acoes">
                      <button type="button" className="secundario" onClick={() => editar(professor)}>
                        Editar
                      </button>
                      <button type="button" className="perigo" onClick={() => remover(professor)}>
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
