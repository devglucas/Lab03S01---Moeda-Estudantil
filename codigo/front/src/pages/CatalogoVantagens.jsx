import { useEffect, useState } from "react";

import { authApi, trocasApi, urlDaFoto, vantagemApi } from "../api.js";
import Aviso from "../components/Aviso.jsx";

// Catálogo do aluno logado: as vantagens de todas as empresas parceiras, que
// podem ser trocadas pelas moedas do saldo.
export default function CatalogoVantagens({ usuario }) {
  const [vantagens, setVantagens] = useState(null);
  const [saldo, setSaldo] = useState(usuario.saldo);
  const [aviso, setAviso] = useState(null);
  const [cupom, setCupom] = useState(null);
  const [trocandoId, setTrocandoId] = useState(null);

  async function atualizarSaldo() {
    setSaldo((await authApi.eu()).saldo);
  }

  useEffect(() => {
    async function carregar() {
      try {
        const [lista] = await Promise.all([vantagemApi.catalogo(), atualizarSaldo()]);
        setVantagens(lista);
      } catch (erro) {
        setAviso({ tipo: "erro", texto: erro.message });
      }
    }
    carregar();
  }, []);

  async function trocar(vantagem) {
    if (!window.confirm(`Trocar ${vantagem.custo} moeda(s) por "${vantagem.nome}"?`)) return;

    setTrocandoId(vantagem.id);
    setAviso(null);
    setCupom(null);
    try {
      setCupom(await trocasApi.trocar(vantagem.id));
      await atualizarSaldo();
    } catch (erro) {
      setAviso({ tipo: "erro", texto: erro.message });
    } finally {
      setTrocandoId(null);
    }
  }

  return (
    <section className="pagina">
      <div className="cartao">
        <h2>Vantagens disponíveis</h2>
        <p className="saldo">Seu saldo: {saldo} moeda(s)</p>
        <Aviso aviso={aviso} />

        {cupom && (
          <div className="cupom" role="status">
            <span>
              Troca realizada! Apresente este código à {cupom.empresaNome} para
              retirar "{cupom.vantagemNome}":
            </span>
            <strong>{cupom.codigo}</strong>
            <small>O cupom também foi enviado para o seu e-mail.</small>
          </div>
        )}

        {vantagens?.length === 0 && <p className="vazio">Nenhuma vantagem cadastrada ainda.</p>}

        {vantagens?.length > 0 && (
          <ul className="catalogo">
            {vantagens.map((vantagem) => {
              const faltam = vantagem.custo - saldo;
              return (
                <li key={vantagem.id} className="vantagem">
                  {vantagem.foto ? (
                    <img src={urlDaFoto(vantagem.foto)} alt={vantagem.nome} />
                  ) : (
                    <div className="vantagem-sem-foto">Sem foto</div>
                  )}
                  <div className="vantagem-corpo">
                    <span className="vantagem-empresa">{vantagem.empresaNome}</span>
                    <h3>{vantagem.nome}</h3>
                    <p>{vantagem.descricao}</p>
                  </div>
                  <div className="vantagem-rodape">
                    <strong>{vantagem.custo} moeda(s)</strong>
                    {faltam > 0 ? (
                      <span className="falta">Faltam {faltam}</span>
                    ) : (
                      <button
                        type="button"
                        onClick={() => trocar(vantagem)}
                        disabled={trocandoId !== null}
                      >
                        {trocandoId === vantagem.id ? "Trocando..." : "Trocar"}
                      </button>
                    )}
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </section>
  );
}
