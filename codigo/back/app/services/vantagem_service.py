from app.extensions import db
from app.models.vantagem import Vantagem
from app.models.empresa import EmpresaParceira
from app.repositories.vantagem_repository import VantagemRepository
from app.services.email_service import EmailService
# from app.services.professor_service import NaoEncontradoError, ValidacaoError
from app.services.erros import Conflito, DadosInvalidos, NaoEncontrado, exigir_json
import os, uuid
from app.extensions import db
from app.services.erros import ErroDeNegocio


class VantagemService:

    PASTA_FOTOS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
    EXTENSOES = {"png", "jpg", "jpeg", "webp"}

    def __init__(self, repository=None):
        self.repository = repository or VantagemRepository()

    def salvar_foto(self, arquivo):
        if arquivo is None or arquivo.filename == "":
            return None # Foto é opcional

        ext = arquivo.filename.rsplit(".", 1)[-1].lower() if "." in arquivo.filename else ""
        if ext not in self.EXTENSOES:
            raise ErroDeNegocio("Formato inválido.", {"foto": "Use PNG, JPG ou WEBP."}, 400)

        os.makedirs(self.PASTA_FOTOS, exist_ok=True)
        nome = f"{uuid.uuid4().hex}.{ext}"
        arquivo.save(os.path.join(self.PASTA_FOTOS, nome))
        return nome

    def criar(self, dados, files):
        # Se 'dados' vier como None (caso o front mande multipart/form-data sem JSON puro, 
        # os dados de texto costumam vir em request.form, dependendo de como o controller chama).
        # Vamos garantir que 'dados' seja um dicionário seguro:
        dados = dados or {}

        print(dados)
        empresa_id = dados.get("empresaId")
        nome = dados.get("nome")
        descricao = dados.get("descricao")
        custo = dados.get("custo")

        arquivoFoto = files.get("foto") if files else None

        if not empresa_id or not nome or not custo:
            raise DadosInvalidos("Empresa, nome e custo são obrigatórios")

        empresa = db.session.get(EmpresaParceira, empresa_id)
        if not empresa:
            raise NaoEncontrado("Empresa não encontrada")

        nome_foto = self.salvar_foto(arquivoFoto)

        # 1. CRIAR A INSTÂNCIA DA CLASSE (Isso transforma o dict em um objeto do SQLAlchemy)
        vantagem = Vantagem(
            nome=nome,
            descricao=descricao,
            custo=int(custo) if custo else 0,
            foto=nome_foto,
            empresa_id=empresa_id
        )

        # 2. Passar o objeto instanciado para o repositório
        self.repository.criar(vantagem)
        return vantagem


    def salvar_foto(self, arquivo):
        if arquivo is None or arquivo.filename == "":
            raise ErroDeNegocio(
                "Envie uma imagem.",
                {"foto": "Arquivo obrigatório."},
                400
            )

        ext = arquivo.filename.rsplit(".", 1)[-1].lower() if "." in arquivo.filename else ""

        if ext not in self.EXTENSOES:
            raise ErroDeNegocio(
                "Formato inválido.",
                {"foto": "Use PNG, JPG ou WEBP."},
                400
            )

        os.makedirs(self.PASTA_FOTOS, exist_ok=True)

        nome = f"{uuid.uuid4().hex}.{ext}"
        caminho = os.path.join(self.PASTA_FOTOS, nome)

        arquivo.save(caminho)

        return nome

    def listar_todas(self):
        return self.repository.listar_todas()