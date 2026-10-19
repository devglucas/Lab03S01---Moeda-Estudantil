import { useEffect, useState } from "react";

import { empresasApi } from "../api.js";
import Aviso from "../components/Aviso.jsx";
import Campo from "../components/Campo.jsx";
import { formatarCnpj } from "../formatacao.js";

const VAZIO = { nome: "", email: "", cnpj: "", login: "", senha: "" };

export default function Empresas() {
  const [empresas, setEmpresas] = useState([]);
  const [form, setForm] = useState(VAZIO);
  const [editandoId, setEditandoId] = useState(null);
  const [erros, setErros] = useState({});
  const [aviso, setAviso] = useState(null);
  const [salvando, setSalvando] = useState(false);

  async function carregar() {
    try {
      setEmpresas(await empresasApi.listar());
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

  function editar(empresa) {
    setForm({
      nome: empresa.nome,
      email: empresa.email,
      cnpj: formatarCnpj(empresa.cnpj),
      login: empresa.login,
      senha: "",
    });
    setEditandoId(empresa.id);
    setErros({});
    setAviso(null);
  }

  async function salvar(evento) {
    evento.preventDefault();
    setSalvando(true);
    setAviso(null);

    try {
      if (editandoId) {
        await empresasApi.atualizar(editandoId, form);
        setAviso({ tipo: "sucesso", texto: "Empresa atualizada com sucesso." });
      } else {
        await empresasApi.criar(form);
        setAviso({ tipo: "sucesso", texto: "Empresa cadastrada com sucesso." });
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

  async function remover(empresa) {
    if (!window.confirm(`Remover a empresa ${empresa.nome}?`)) return;

    try {
      await empresasApi.remover(empresa.id);
      if (editandoId === empresa.id) limpar();
      setAviso({ tipo: "sucesso", texto: "Empresa removida." });
      await carregar();
    } catch (erro) {
      setAviso({ tipo: "erro", texto: erro.message });
    }
  }

  return (
    <section className="pagina">
      <form className="cartao" onSubmit={salvar} noValidate>
        <h2>{editandoId ? "Editar empresa parceira" : "Cadastrar empresa parceira"}</h2>
        <Aviso aviso={aviso} />

        <div className="grade">
          <Campo rotulo="Nome" nome="nome" value={form.nome} onChange={alterar} erro={erros.nome} />
          <Campo rotulo="E-mail" nome="email" type="email" value={form.email} onChange={alterar} erro={erros.email} />
          <Campo rotulo="CNPJ" nome="cnpj" placeholder="00.000.000/0000-00" value={form.cnpj} onChange={alterar} erro={erros.cnpj} />
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
        <h2>Empresas parceiras cadastradas</h2>
        {empresas.length === 0 ? (
          <p className="vazio">Nenhuma empresa cadastrada.</p>
        ) : (
          <div className="tabela-rolagem">
            <table>
              <thead>
                <tr>
                  <th>Nome</th>
                  <th>E-mail</th>
                  <th>CNPJ</th>
                  <th>Login</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {empresas.map((empresa) => (
                  <tr key={empresa.id}>
                    <td>{empresa.nome}</td>
                    <td>{empresa.email}</td>
                    <td>{formatarCnpj(empresa.cnpj)}</td>
                    <td>{empresa.login}</td>
                    <td className="linha-acoes">
                      <button type="button" className="secundario" onClick={() => editar(empresa)}>
                        Editar
                      </button>
                      <button type="button" className="perigo" onClick={() => remover(empresa)}>
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
