// Mensagem de sucesso ou erro exibida acima do formulário.
export default function Aviso({ aviso }) {
  if (!aviso) return null;
  return (
    <p className={`aviso aviso-${aviso.tipo}`} role="status">
      {aviso.texto}
    </p>
  );
}
