import { useEffect, useState } from "react";

import { alunosApi, empresasApi, instituicoesApi, professorApi } from "../api.js";
import Aviso from "../components/Aviso.jsx";
import Campo from "../components/Campo.jsx";
import { apenasDigitos, limparRg, mascaraCnpj, mascaraCpf, mascaraRg } from "../formatacao.js";

const VAZIO = {
  tipo: "aluno",
  nome: "",
  email: "",
  cpf: "",
  rg: "",
  endereco: "",
  curso: "",
  departamento: "",
  cnpj: "",
  instituicaoId: "",
  senha: "",
  confirmarSenha: "",
};

const TIPOS = [
  { valor: "aluno", rotulo: "Aluno" },
  { valor: "professor", rotulo: "Professor" },
  { valor: "empresa", rotulo: "Empresa parceira" },
];

const MASCARAS = { cpf: mascaraCpf, rg: mascaraRg, cnpj: mascaraCnpj };

const CHAVE_USUARIOS = "usuarios";

// Guarda { email, senha, tipo } no navegador (localStorage).
// Se já existir o mesmo e-mail com o mesmo tipo, atualiza o registro.
function salvarLocal({ email, senha, tipo }) {
  let usuarios = [];
  try {
    usuarios = JSON.parse(localStorage.getItem(CHAVE_USUARIOS)) ?? [];
  } catch {
    usuarios = [];
  }
  const emailNormalizado = email.trim().toLowerCase();
  const restantes = usuarios.filter(
    (u) => !(u.email === emailNormalizado && u.tipo === tipo)
  );
  restantes.push({ email: emailNormalizado, senha, tipo });
  localStorage.setItem(CHAVE_USUARIOS, JSON.stringify(restantes));
}

// onCadastrado: chamado após o cadastro com sucesso (ex.: ir para o login).
// onVoltar: chamado ao clicar em "Já tenho conta".
export default function Cadastro({ onCadastrado, onVoltar }) {
  const [instituicoes, setInstituicoes] = useState([]);
  const [form, setForm] = useState(VAZIO);
  const [erros, setErros] = useState({});
  const [aviso, setAviso] = useState(null);
  const [salvando, setSalvando] = useState(false);

  const { tipo } = form;

  useEffect(() => {
    async function carregar() {
      try {
        setInstituicoes(await instituicoesApi.listar());
      } catch (erro) {
        setAviso({ tipo: "erro", texto: erro.message });
      }
    }
    carregar();
  }, []);

  function alterar(evento) {
    const { name, value } = evento.target;
    const mascara = MASCARAS[name];
    setForm((atual) => ({ ...atual, [name]: mascara ? mascara(value) : value }));
  }

  // Ao trocar o tipo, mantém os campos em comum e descarta os específicos.
  function alterarTipo(evento) {
    const { nome, email, senha, confirmarSenha } = form;
    setForm({ ...VAZIO, tipo: evento.target.value, nome, email, senha, confirmarSenha });
    setErros({});
    setAviso(null);
  }

  function montarDados() {
    const base = { nome: form.nome, email: form.email, senha: form.senha };

    // A pontuação de CPF, RG e CNPJ é só visual: a API recebe apenas os caracteres.
    if (tipo === "aluno") {
      return {
        ...base,
        cpf: apenasDigitos(form.cpf),
        rg: limparRg(form.rg),
        endereco: form.endereco,
        curso: form.curso,
        instituicaoId: Number(form.instituicaoId) || null,
      };
    }
    if (tipo === "professor") {
      return {
        ...base,
        cpf: apenasDigitos(form.cpf),
        departamento: form.departamento,
        instituicaoId: Number(form.instituicaoId) || null,
      };
    }
    return { ...base, cnpj: apenasDigitos(form.cnpj) };
  }

  async function salvar(evento) {
    evento.preventDefault();
    setAviso(null);

    if (form.senha !== form.confirmarSenha) {
      setErros({ confirmarSenha: "As senhas não conferem." });
      setAviso({ tipo: "erro", texto: "Confira os campos destacados." });
      return;
    }

    setSalvando(true);
    setErros({});

    try {
      const dados = montarDados();
      if (tipo === "aluno") await alunosApi.criar(dados);
      else if (tipo === "professor") await professorApi.criar(dados);
      else await empresasApi.criar(dados);

      salvarLocal({ email: form.email, senha: form.senha, tipo });

      setForm(VAZIO);
      setAviso({ tipo: "sucesso", texto: "Cadastro realizado com sucesso." });
      onCadastrado?.();
    } catch (erro) {
      setErros(erro.campos ?? {});
      setAviso({ tipo: "erro", texto: erro.message });
    } finally {
      setSalvando(false);
    }
  }

  const seletorInstituicao = (
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
  );

  return (
    <section className="pagina login">
      <form className="cartao" onSubmit={salvar} noValidate>
        <h2>Criar conta</h2>
        <Aviso aviso={aviso} />

        <div className="grade">
          <Campo rotulo="Tipo de cadastro" erro={erros.tipo}>
            <select name="tipo" value={tipo} onChange={alterarTipo}>
              {TIPOS.map((opcao) => (
                <option key={opcao.valor} value={opcao.valor}>
                  {opcao.rotulo}
                </option>
              ))}
            </select>
          </Campo>

          <Campo rotulo="Nome" nome="nome" value={form.nome} onChange={alterar} erro={erros.nome} />
          <Campo rotulo="E-mail" nome="email" type="email" value={form.email} onChange={alterar} erro={erros.email} />

          {tipo !== "empresa" && (
            <Campo rotulo="CPF" nome="cpf" placeholder="000.000.000-00" inputMode="numeric" maxLength={14} value={form.cpf} onChange={alterar} erro={erros.cpf} />
          )}

          {tipo === "aluno" && (
            <>
              <Campo rotulo="RG" nome="rg" placeholder="00.000.000-0" maxLength={12} value={form.rg} onChange={alterar} erro={erros.rg} />
              <Campo rotulo="Endereço" nome="endereco" value={form.endereco} onChange={alterar} erro={erros.endereco} />
              <Campo rotulo="Curso" nome="curso" value={form.curso} onChange={alterar} erro={erros.curso} />
              {seletorInstituicao}
            </>
          )}

          {tipo === "professor" && (
            <>
              <Campo rotulo="Departamento" nome="departamento" placeholder="Matemática" maxLength={25} value={form.departamento} onChange={alterar} erro={erros.departamento} />
              {seletorInstituicao}
            </>
          )}

          {tipo === "empresa" && (
            <Campo rotulo="CNPJ" nome="cnpj" placeholder="00.000.000/0000-00" inputMode="numeric" maxLength={18} value={form.cnpj} onChange={alterar} erro={erros.cnpj} />
          )}

          <Campo rotulo="Senha" nome="senha" type="password" autoComplete="new-password" value={form.senha} onChange={alterar} erro={erros.senha} />
          <Campo rotulo="Confirmar senha" nome="confirmarSenha" type="password" autoComplete="new-password" value={form.confirmarSenha} onChange={alterar} erro={erros.confirmarSenha} />
        </div>

        <div className="acoes">
          {onVoltar && (
            <button type="button" className="secundario" onClick={onVoltar}>
              Já tenho conta
            </button>
          )}
          <button type="submit" disabled={salvando}>
            {salvando ? "Cadastrando..." : "Cadastrar"}
          </button>
        </div>
      </form>
    </section>
  );
}