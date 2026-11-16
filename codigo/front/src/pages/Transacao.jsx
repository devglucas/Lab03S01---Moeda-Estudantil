import { useEffect, useState } from "react";

import { alunosApi, authApi, transacoesApi } from "../api.js";
import Aviso from "../components/Aviso.jsx";
import Campo from "../components/Campo.jsx";

const VAZIO = { alunoId: "", valor: "", mensagem: "" };

// O professor logado envia moedas em seu próprio nome, só para alunos da sua instituição.
export default function Transacao({ usuario }) {
  const [saldo, setSaldo] = useState(usuario.saldo);
  const [alunos, setAlunos] = useState([]);
  const [form, setForm] = useState(VAZIO);
  const [erros, setErros] = useState({});
  const [aviso, setAviso] = useState(null);
  const [salvando, setSalvando] = useState(false);

  async function atualizarSaldo() {
    setSaldo((await authApi.eu()).saldo);
  }

  useEffect(() => {
    async function carregar() {
      try {
        const [lista] = await Promise.all([alunosApi.listar(), atualizarSaldo()]);
        setAlunos(lista.filter((aluno) => aluno.instituicaoId === usuario.instituicaoId));
      } catch (erro) {
        setAviso({ tipo: "erro", texto: erro.message });
      }
    }
    carregar();
  }, [usuario.instituicaoId]);

  function alterar(evento) {
    const { name, value } = evento.target;
    setForm((atual) => ({ ...atual, [name]: value }));
  }

  function limpar() {
    setForm(VAZIO);
    setErros({});
  }

  async function salvar(evento) {
    evento.preventDefault();
    setSalvando(true);
    setAviso(null);
    setErros({});

    const dados = {
      alunoId: Number(form.alunoId) || null,
      valor: Number(form.valor),
      mensagem: form.mensagem,
    };

    try {
      await transacoesApi.enviar(dados);
      setAviso({ tipo: "sucesso", texto: "Moedas enviadas com sucesso." });
      limpar();
      await atualizarSaldo();
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
        <p className="saldo">Seu saldo: {saldo} moeda(s)</p>
        <Aviso aviso={aviso} />

        <div className="grade">
          <Campo rotulo={`Aluno (${usuario.instituicaoNome})`} erro={erros.alunoId}>
            <select name="alunoId" value={form.alunoId} onChange={alterar}>
              <option value="">Selecione</option>
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
    </section>
  );
}
