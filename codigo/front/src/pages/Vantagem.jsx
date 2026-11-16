import { useEffect, useState } from "react";

import { vantagemApi, empresasApi } from "../api.js";
import Aviso from "../components/Aviso.jsx";
import Campo from "../components/Campo.jsx";

const VAZIO = {
  nome: "",
  descricao: "",
  custo: "",
  empresaId: "",
  foto: null,
};

export default function Vantagens() {
  const [vantagens, setVantagens] = useState([]);
  const [empresas, setEmpresas] = useState([]);
  const [form, setForm] = useState(VAZIO);
  const [editandoId, setEditandoId] = useState(null);
  const [erros, setErros] = useState({});
  const [aviso, setAviso] = useState(null);
  const [salvando, setSalvando] = useState(false);

  async function carregar() {
    try {
      const [listaVantagens, listaEmpresas] = await Promise.all([
        vantagemApi.listar(),
        empresasApi.listar(),
      ]);
      console.log(listaVantagens)
      setVantagens(listaVantagens);
      setEmpresas(listaEmpresas);
    } catch (erro) {
      setAviso({ tipo: "erro", texto: erro.message });
    }
  }

  useEffect(() => {
    carregar();
  }, []);

  function alterar(evento) {
    const { name, value, type, files } = evento.target;
    if (type === "file") {
      setForm((atual) => ({ ...atual, [name]: files[0] ?? null }));
    } else {
      setForm((atual) => ({ ...atual, [name]: value }));
    }
  }

  function limpar() {
    setForm(VAZIO);
    setEditandoId(null);
    setErros({});
  }

  function editar(vantagem) {
    setForm({
      nome: vantagem.nome,
      descricao: vantagem.descricao,
      custo: String(vantagem.custo),
      empresaId: String(vantagem.empresaId),
      foto: null, // O arquivo anterior não é recarregado no input file por segurança do browser
    });
    setEditandoId(vantagem.id);
    setErros({});
    setAviso(null);
  }

  async function salvar(evento) {
    evento.preventDefault();
    setSalvando(true);
    setAviso(null);

    const formData = new FormData();

    formData.append("nome", form.nome);
    formData.append("descricao", form.descricao);
    formData.append("custo", form.custo);
    formData.append("empresaId", form.empresaId);

    // Adiciona a foto somente se existir
    if (form.foto) {
      formData.append("foto", form.foto);
    }


    console.log("FORM:", form);

    for (const [chave, valor] of formData.entries()) {
      console.log(chave, valor);
    }
    try {
      // Como o objeto API padrão utiliza application/json, 
      // passamos o fetch customizado ou ajustamos o body para aceitar FormData 
      // (o FormData remove automaticamente o Content-Type padrão para o browser setar o boundary correto).
      // if (editandoId) {
      //   await vantagemApi.atualizar(editandoId, formData);
      //   setAviso({ tipo: "sucesso", texto: "Vantagem atualizada com sucesso." });
      // } else {
      await vantagemApi.criar(formData);
      setAviso({ tipo: "sucesso", texto: "Vantagem cadastrada com sucesso." });
      // }
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
      if (editandoId === vantagem.id) limpar();
      setAviso({ tipo: "sucesso", texto: "Vantagem removida." });
      await carregar();
    } catch (erro) {
      setAviso({ tipo: "erro", texto: erro.message });
    }
  }

  return (
    <section className="pagina">
      <form className="cartao" onSubmit={salvar} noValidate>
        <h2>{editandoId ? "Editar vantagem" : "Cadastrar vantagem"}</h2>
        <Aviso aviso={aviso} />

        <div className="grade">
          <Campo rotulo="Nome da vantagem" nome="nome" value={form.nome} onChange={alterar} erro={erros.nome} />

          <Campo rotulo="Empresa parceira" erro={erros.empresaId}>
            <select name="empresaId" value={form.empresaId} onChange={alterar}>
              <option value="">Selecione</option>
              {empresas.map((empresa) => (
                <option key={empresa.id} value={empresa.id}>
                  {empresa.nome}
                </option>
              ))}
            </select>
          </Campo>

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

          <Campo rotulo="Foto da vantagem (opcional)" erro={erros.foto}>
            <input
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
              placeholder="Descreva os detalhes da vantagem..."
              value={form.descricao}
              onChange={alterar}
            />
          </Campo>
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
        <h2>Vantagens cadastradas</h2>
        {vantagens.length === 0 ? (
          <p className="vazio">Nenhuma vantagem cadastrada.</p>
        ) : (
          <div className="tabela-rolagem">
            <table>
              <thead>
                <tr>
                  <th>Nome</th>
                  <th>Empresa</th>
                  <th className="numero">Custo</th>
                  <th>Descrição</th>
                  <th>Foto</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {vantagens.map((vantagem) => (
                  <tr key={vantagem.id}>
                    <td>{vantagem.nome}</td>
                    <td>{vantagem.empresaNome || "—"}</td>
                    <td className="numero">{vantagem.custo}</td>
                    <td>{vantagem.descricao}</td>
                    <td><img src={vantagem.fotoUrl} alt="foto vantagem" /></td>
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