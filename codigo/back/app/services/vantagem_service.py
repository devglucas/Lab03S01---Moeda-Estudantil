"""Regras de negócio das vantagens: cadastro pela empresa e catálogo do aluno."""
import os
import re
import uuid

from flask import current_app

from app.models.vantagem import Vantagem
from app.repositories import ErroIntegridade, VantagemRepository
from app.services.erros import Conflito, DadosInvalidos, NaoEncontrado
from app.validacao import texto

EXTENSOES_FOTO = {"png", "jpg", "jpeg", "webp"}
TAMANHO_MAXIMO_NOME = 120
TAMANHO_MAXIMO_DESCRICAO = 500


class VantagemService:
    def __init__(self, vantagens=None):
        self.vantagens = vantagens or VantagemRepository()

    def listar_todas(self):
        return self.vantagens.listar_todas()

    def listar_da_empresa(self, empresa):
        return self.vantagens.listar_por_empresa(empresa.id)

    def criar(self, empresa, dados, foto):
        """``empresa`` é o usuário logado; ``foto`` é opcional."""
        vantagem = Vantagem(empresa=empresa, **self._validar(dados, foto))
        vantagem.foto = self._guardar_foto(foto)
        self._salvar(vantagem, vantagem.foto)
        return vantagem

    def atualizar(self, empresa, vantagem_id, dados, foto):
        """Sem uma foto nova, a vantagem mantém a atual."""
        vantagem = self._buscar_da_empresa(empresa, vantagem_id)
        for campo, valor in self._validar(dados, foto).items():
            setattr(vantagem, campo, valor)

        foto_antiga = vantagem.foto
        foto_nova = self._guardar_foto(foto)
        if foto_nova:
            vantagem.foto = foto_nova
        self._salvar(vantagem, foto_nova)

        if foto_nova:
            self._apagar_foto(foto_antiga)
        return vantagem

    def remover(self, empresa, vantagem_id):
        vantagem = self._buscar_da_empresa(empresa, vantagem_id)
        foto = vantagem.foto
        try:
            self.vantagens.remover(vantagem)
        except ErroIntegridade:
            raise Conflito("Não foi possível remover a vantagem.")
        self._apagar_foto(foto)

    def _buscar_da_empresa(self, empresa, vantagem_id):
        """A empresa só enxerga as próprias vantagens; as das outras são 404."""
        vantagem = self.vantagens.buscar_por_id(vantagem_id)
        if vantagem is None or vantagem.empresa_id != empresa.id:
            raise NaoEncontrado("Vantagem não encontrada")
        return vantagem

    def _salvar(self, vantagem, foto_nova):
        try:
            self.vantagens.salvar(vantagem)
        except ErroIntegridade:
            # Sem o registro no banco, a foto recém-gravada ficaria órfã.
            self._apagar_foto(foto_nova)
            raise Conflito("Não foi possível salvar a vantagem.")

    def _validar(self, dados, foto):
        """Valida o formulário e devolve nome, descrição e custo já tratados."""
        campos = {}
        nome = texto(dados, "nome")
        descricao = texto(dados, "descricao")
        custo = texto(dados, "custo")

        if not nome:
            campos["nome"] = "Campo obrigatório"
        elif len(nome) > TAMANHO_MAXIMO_NOME:
            campos["nome"] = f"O nome deve ter até {TAMANHO_MAXIMO_NOME} caracteres"

        if not descricao:
            campos["descricao"] = "Campo obrigatório"
        elif len(descricao) > TAMANHO_MAXIMO_DESCRICAO:
            campos["descricao"] = f"A descrição deve ter até {TAMANHO_MAXIMO_DESCRICAO} caracteres"

        if not re.fullmatch(r"[0-9]+", custo) or int(custo) <= 0:
            campos["custo"] = "Informe um número inteiro de moedas maior que zero"

        if foto is not None and _extensao(foto.filename) not in EXTENSOES_FOTO:
            campos["foto"] = "Use uma imagem PNG, JPG ou WEBP"

        if campos:
            raise DadosInvalidos("Dados inválidos", campos)
        return {"nome": nome, "descricao": descricao, "custo": int(custo)}

    def _guardar_foto(self, foto):
        if foto is None:
            return None
        pasta = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(pasta, exist_ok=True)
        # Nome aleatório: evita colisões e não usa o nome enviado pelo usuário.
        nome = f"{uuid.uuid4().hex}.{_extensao(foto.filename)}"
        foto.save(os.path.join(pasta, nome))
        return nome

    def _apagar_foto(self, nome):
        if not nome:
            return
        try:
            os.remove(os.path.join(current_app.config["UPLOAD_FOLDER"], nome))
        except FileNotFoundError:
            pass


def _extensao(nome_arquivo):
    _, _, extensao = (nome_arquivo or "").rpartition(".")
    return extensao.lower()
