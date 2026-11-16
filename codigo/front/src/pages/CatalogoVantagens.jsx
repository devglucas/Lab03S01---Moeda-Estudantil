import { useEffect, useState } from "react";

import { authApi, urlDaFoto, vantagemApi } from "../api.js";
import Aviso from "../components/Aviso.jsx";

// Catálogo do aluno logado: as vantagens de todas as empresas parceiras.
export default function CatalogoVantagens({ usuario }) {
  const [vantagens, setVantagens] = useState(null);
  const [saldo, setSaldo] = useState(usuario.saldo);
  const [aviso, setAviso] = useState(null);

  useEffect(() => {
    async function carregar() {
      try {
        const [lista, perfil] = await Promise.all([vantagemApi.catalogo(), authApi.eu()]);
        setVantagens(lista);
        setSaldo(perfil.saldo);
      } catch (erro) {
        setAviso({ tipo: "erro", texto: erro.message });
      }
    }
    carregar();
  }, []);

  return (
    <section className="pagina">
      <div className="cartao">
        <h2>Vantagens disponíveis</h2>
        <p className="saldo">Seu saldo: {saldo} moeda(s)</p>
        <Aviso aviso={aviso} />

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
                    <span className={faltam > 0 ? "falta" : "disponivel"}>
                      {faltam > 0 ? `Faltam ${faltam}` : "Saldo suficiente"}
                    </span>
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
