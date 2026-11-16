import { useEffect, useState } from "react";

import { urlDaFoto, vantagemApi } from "../api.js";
import Aviso from "../components/Aviso.jsx";
import Campo from "../components/Campo.jsx";

const VAZIO = { nome: "", descricao: "", custo: "", foto: null };

// A empresa logada cadastra, edita e remove as próprias vantagens.
export default function Vantagem() {
  const [vantagens, setVantagens] = useState([]);
  const [form, setForm] = useState(VAZIO);
  const [editando, setEditando] = useState(null);
  const [erros, setErros] = useState({});
  const [aviso, setAviso] = useState(null);
  const [salvando, setSalvando] = useState(false);
  // O <input type="file"> não é controlado; trocar a key o esvazia.
  const [chaveFoto, setChaveFoto] = useState(0);

  async function carregar() {
    try {
      setVantagens(await vantagemApi.minhas());
    } catch (erro) {
      setAviso({ tipo: "erro", texto: erro.message });
    }
  }

  useEffect(() => {
    carregar();
  }, []);

  function alterar(evento) {
    const { name, value, files } = evento.target;
    setForm((atual) => ({ ...atual, [name]: files ? files[0] ?? null : value }));
  }

  function limpar() {
    setForm(VAZIO);
    setEditando(null);
    setErros({});
    setChaveFoto((chave) => chave + 1);
  }

  function editar(vantagem) {
    setForm({
      nome: vantagem.nome,
      descricao: vantagem.descricao,
      custo: String(vantagem.custo),
      foto: null,
    });
    setEditando(vantagem);
    setErros({});
    setAviso(null);
    setChaveFoto((chave) => chave + 1);
  }

  async function salvar(evento) {
    evento.preventDefault();
    setSalvando(true);
    setAviso(null);

    const formulario = new FormData();
    formulario.append("nome", form.nome);
    formulario.append("descricao", form.descricao);
    formulario.append("custo", form.custo);
    if (form.foto) formulario.append("foto", form.foto);

    try {
      if (editando) {
        await vantagemApi.atualizar(editando.id, formulario);
        setAviso({ tipo: "sucesso", texto: "Vantagem atualizada com sucesso." });
      } else {
        await vantagemApi.criar(formulario);
        setAviso({ tipo: "sucesso", texto: "Vantagem cadastrada com sucesso." });
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

  async function remover(vantagem) {
    if (!window.confirm(`Remover a vantagem ${vantagem.nome}?`)) return;

    try {
      await vantagemApi.remover(vantagem.id);
      if (editando?.id === vantagem.id) limpar();
      setAviso({ tipo: "sucesso", texto: "Vantagem removida." });
      await carregar();
    } catch (erro) {
      setAviso({ tipo: "erro", texto: erro.message });
    }
  }

  return (
    <section className="pagina">
      <form className="cartao" onSubmit={salvar} noValidate>
        <h2>{editando ? "Editar vantagem" : "Cadastrar vantagem"}</h2>
        <Aviso aviso={aviso} />

        <div className="grade">
          <Campo
            rotulo="Nome da vantagem"
            nome="nome"
            maxLength={120}
            value={form.nome}
            onChange={alterar}
            erro={erros.nome}
          />

          <Campo
            rotulo="Custo (moedas)"
            nome="custo"
            type="number"
            min={1}
            step={1}
            value={form.custo}
            onChange={alterar}
            erro={erros.custo}
          />

          <Campo
            rotulo={editando?.foto ? "Nova foto (opcional)" : "Foto do produto (opcional)"}
            erro={erros.foto}
          >
            <input
              key={chaveFoto}
              type="file"
              name="foto"
              accept="image/png, image/jpeg, image/webp"
              onChange={alterar}
            />
          </Campo>

          <Campo rotulo="Descrição" erro={erros.descricao}>
            <textarea
              name="descricao"
              rows={3}
              maxLength={500}
              placeholder="Ex.: 10% de desconto em qualquer livro da loja"
              value={form.descricao}
              onChange={alterar}
            />
          </Campo>
        </div>

        <div className="acoes">
          {editando && (
            <button type="button" className="secundario" onClick={limpar}>
              Cancelar
            </button>
          )}
          <button type="submit" disabled={salvando}>
            {editando ? "Salvar alterações" : "Cadastrar"}
          </button>
        </div>
      </form>

      <div className="cartao">
        <h2>Minhas vantagens</h2>
        {vantagens.length === 0 ? (
          <p className="vazio">Nenhuma vantagem cadastrada.</p>
        ) : (
          <div className="tabela-rolagem">
            <table>
              <thead>
                <tr>
                  <th>Foto</th>
                  <th>Nome</th>
                  <th>Descrição</th>
                  <th className="numero">Custo</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {vantagens.map((vantagem) => (
                  <tr key={vantagem.id}>
                    <td>
                      {vantagem.foto ? (
                        <img className="miniatura" src={urlDaFoto(vantagem.foto)} alt="" />
                      ) : (
                        <span className="miniatura sem-foto">—</span>
                      )}
                    </td>
                    <td>{vantagem.nome}</td>
                    <td className="texto-longo">{vantagem.descricao}</td>
                    <td className="numero">{vantagem.custo}</td>
                    <td className="linha-acoes">
                      <button type="button" className="secundario" onClick={() => editar(vantagem)}>
                        Editar
                      </button>
                      <button type="button" className="perigo" onClick={() => remover(vantagem)}>
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
