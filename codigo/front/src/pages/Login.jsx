import { useState } from "react";

import { authApi } from "../api.js";
import Aviso from "../components/Aviso.jsx";
import Campo from "../components/Campo.jsx";

const VAZIO = { email: "", senha: "" };

// O e-mail é o login e é único entre alunos, professores e empresas, então o
// próprio back-end descobre o perfil. onLogin recebe { token, usuario }.
export default function Login({ onLogin, aviso: avisoInicial }) {
  const [form, setForm] = useState(VAZIO);
  const [erros, setErros] = useState({});
  const [aviso, setAviso] = useState(avisoInicial);
  const [entrando, setEntrando] = useState(false);

  function alterar(evento) {
    const { name, value } = evento.target;
    setForm((atual) => ({ ...atual, [name]: value }));
  }

  async function entrar(evento) {
    evento.preventDefault();
    setEntrando(true);
    setAviso(null);
    setErros({});

    try {
      onLogin(await authApi.entrar({ email: form.email.trim(), senha: form.senha }));
    } catch (erro) {
      setErros(erro.campos ?? {});
      setAviso({ tipo: "erro", texto: erro.message });
      setEntrando(false);
    }
  }

  return (
    <section className="pagina login">
      <form className="cartao" onSubmit={entrar} noValidate>
        <h2>Entrar</h2>
        <Aviso aviso={aviso} />

        <Campo
          rotulo="E-mail"
          nome="email"
          type="email"
          autoComplete="username"
          value={form.email}
          onChange={alterar}
          erro={erros.email}
        />
        <Campo
          rotulo="Senha"
          nome="senha"
          type="password"
          autoComplete="current-password"
          value={form.senha}
          onChange={alterar}
          erro={erros.senha}
        />

        <div className="acoes">
          <button type="submit" disabled={entrando}>
            {entrando ? "Entrando..." : "Entrar"}
          </button>
        </div>
      </form>
    </section>
  );
}
