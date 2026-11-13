import { useState } from "react";

// import { authApi } from "../api.js";
import Aviso from "../components/Aviso.jsx";
import Campo from "../components/Campo.jsx";

const VAZIO = { tipo: "aluno", email: "", senha: "" };

const TIPOS = [
  { valor: "aluno", rotulo: "Aluno" },
  { valor: "professor", rotulo: "Professor" },
  { valor: "empresa", rotulo: "Empresa parceira" },
];

// onLogin recebe o usuário autenticado (ex.: { id, nome, tipo, token }).
export default function Login({ onLogin }) {
  const [form, setForm] = useState(VAZIO);
  const [erros, setErros] = useState({});
  const [aviso, setAviso] = useState(null);
  const [salvando, setSalvando] = useState(false);

  function alterar(evento) {
    const { name, value } = evento.target;
    setForm((atual) => ({ ...atual, [name]: value }));
  }

  async function entrar(evento) {
    // evento.preventDefault();
    // setSalvando(true);
    // setAviso(null);
    // setErros({});

    // try {
    //   const usuario = await authApi.login({
    //     tipo: form.tipo,
    //     email: form.email.trim(),
    //     senha: form.senha,
    //   });
    //   onLogin?.(usuario);
    // } catch (erro) {
    //   setErros(erro.campos ?? {});
    //   setAviso({ tipo: "erro", texto: erro.message });
    // } finally {
    //   setSalvando(false);
    // }
  }

  return (
    <section className="pagina login">
      <form className="cartao" onSubmit={entrar} noValidate>
        <h2>Entrar</h2>
        <Aviso aviso={aviso} />

        <div className="grade">
          <Campo rotulo="Tipo de acesso" erro={erros.tipo}>
            <select name="tipo" value={form.tipo} onChange={alterar}>
              {TIPOS.map((tipo) => (
                <option key={tipo.valor} value={tipo.valor}>
                  {tipo.rotulo}
                </option>
              ))}
            </select>
          </Campo>
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
        </div>

        <div className="acoes">
          <button type="submit" disabled={salvando}>
            {salvando ? "Entrando..." : "Entrar"}
          </button>
        </div>
      </form>
    </section>
  );
}