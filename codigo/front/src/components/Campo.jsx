import { cloneElement, useId } from "react";

// Campo de formulário com rótulo e mensagem de erro vinda da API.
// O erro fica fora do <label> e é ligado ao campo por aria-describedby.
export default function Campo({ rotulo, nome, erro, children, ...props }) {
  const id = useId();
  const idErro = `${id}-erro`;
  const acessibilidade = {
    id,
    "aria-invalid": Boolean(erro),
    "aria-describedby": erro ? idErro : undefined,
  };

  return (
    <div className="campo">
      <label htmlFor={id}>{rotulo}</label>
      {children
        ? cloneElement(children, acessibilidade)
        : <input name={nome} {...props} {...acessibilidade} />}
      {erro && <small id={idErro} className="campo-erro">{erro}</small>}
    </div>
  );
}
