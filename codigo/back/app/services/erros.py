"""Erros de negócio lançados pelos services.

Cada erro já sabe o status HTTP correspondente; o handler registrado em
``create_app`` os converte para ``{"erro": ..., "campos": ...}``.
"""


class ErroDeNegocio(Exception):
    status = 400

    def __init__(self, mensagem, campos=None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.campos = campos

    def to_dict(self):
        corpo = {"erro": self.mensagem}
        if self.campos:
            corpo["campos"] = self.campos
        return corpo


class DadosInvalidos(ErroDeNegocio):
    status = 400


class NaoEncontrado(ErroDeNegocio):
    status = 404


class Conflito(ErroDeNegocio):
    status = 409


def exigir_json(dados):
    if not isinstance(dados, dict):
        raise DadosInvalidos("Envie os dados em JSON.")
    return dados
