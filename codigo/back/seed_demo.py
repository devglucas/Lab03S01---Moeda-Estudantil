"""Preenche o banco com dados de demonstração: python seed_demo.py

Cria empresas, professores, alunos, vantagens, envios de moedas e uma troca,
passando pelos mesmos services da API (senhas com hash, 1.000 moedas por
professor, envios atômicos e código de cupom). Nenhum e-mail é enviado.
Todos os usuários usam a senha ``senha123``. Para recriar do zero, apague o
``moedas.db`` antes de rodar.
"""
from app import create_app
from app.repositories import InstituicaoRepository, UsuarioRepository
from app.services.aluno_service import AlunoService
from app.services.empresa_service import EmpresaService
from app.services.professor_service import ProfessorService
from app.services.transacao_service import TransacaoService
from app.services.troca_service import TrocaService
from app.services.vantagem_service import VantagemService

SENHA = "senha123"

EMPRESAS = [
    {"nome": "Livraria Central", "email": "livraria@demo.com", "cnpj": "11222333000181"},
    {"nome": "Cantina do Campus", "email": "cantina@demo.com", "cnpj": "44555666000172"},
]

PROFESSORES = [
    {"nome": "Carla Mendes", "email": "carla@demo.com", "cpf": "52998224725",
     "departamento": "Computação", "instituicao": "PUC Minas"},
    {"nome": "Rui Andrade", "email": "rui@demo.com", "cpf": "15350946056",
     "departamento": "Matemática", "instituicao": "UFMG"},
]

ALUNOS = [
    {"nome": "Ana Souza", "email": "ana@demo.com", "cpf": "11144477735", "rg": "MG1234567",
     "endereco": "Rua da Bahia, 100", "curso": "Engenharia de Software", "instituicao": "PUC Minas"},
    {"nome": "Bruno Lima", "email": "bruno@demo.com", "cpf": "39053344705", "rg": "MG7654321",
     "endereco": "Av. Afonso Pena, 200", "curso": "Ciência da Computação", "instituicao": "PUC Minas"},
    {"nome": "Clara Rocha", "email": "clara@demo.com", "cpf": "71428793860", "rg": "MG1122334",
     "endereco": "Rua Espírito Santo, 300", "curso": "Matemática", "instituicao": "UFMG"},
]

VANTAGENS = {
    "livraria@demo.com": [
        ("10% de desconto em livros", "Desconto em qualquer livro da loja.", 100),
        ("Livro técnico à escolha", "Um livro técnico de até R$ 150.", 800),
    ],
    "cantina@demo.com": [
        ("Café com pão de queijo", "Um café coado e um pão de queijo.", 30),
        ("Almoço completo", "Prato do dia com suco e sobremesa.", 120),
    ],
}

# (professor, aluno, valor, motivo)
ENVIOS = [
    ("carla@demo.com", "ana@demo.com", 200, "Monitoria de Algoritmos"),
    ("carla@demo.com", "bruno@demo.com", 50, "Ótima participação em aula"),
    ("rui@demo.com", "clara@demo.com", 150, "Melhor nota na prova de Cálculo"),
]

# (aluno, vantagem)
TROCAS = [("ana@demo.com", "Café com pão de queijo")]


class _SemNotificacao:
    """Os dados de demonstração não disparam e-mails."""

    def notificar_envio_moedas(self, _envio):
        pass

    def notificar_troca(self, _troca):
        pass


def semear():
    usuarios = UsuarioRepository()
    if usuarios.buscar_por_login(EMPRESAS[0]["email"]):
        print("Os dados de demonstração já existem. Apague o moedas.db para recriá-los.")
        return

    instituicoes = {i.nome: i.id for i in InstituicaoRepository().listar()}

    for dados in EMPRESAS:
        EmpresaService().criar({**dados, "senha": SENHA})
    for dados in PROFESSORES:
        ProfessorService().criar(_com_instituicao(dados, instituicoes))
    for dados in ALUNOS:
        AlunoService().criar(_com_instituicao(dados, instituicoes))

    vantagens = {}
    for email, lista in VANTAGENS.items():
        empresa = usuarios.buscar_por_login(email)
        for nome, descricao, custo in lista:
            dados = {"nome": nome, "descricao": descricao, "custo": str(custo)}
            vantagens[nome] = VantagemService().criar(empresa, dados, None)

    envios = TransacaoService(notificacoes=_SemNotificacao())
    for professor, aluno, valor, motivo in ENVIOS:
        dados = {"alunoId": usuarios.buscar_por_login(aluno).id, "valor": valor, "mensagem": motivo}
        envios.enviar_moedas(usuarios.buscar_por_login(professor), dados)

    trocas = TrocaService(notificacoes=_SemNotificacao())
    for aluno, vantagem in TROCAS:
        trocas.trocar(usuarios.buscar_por_login(aluno), {"vantagemId": vantagens[vantagem].id})

    _resumo(usuarios)


def _com_instituicao(dados, instituicoes):
    instituicao = dados["instituicao"]
    campos = {chave: valor for chave, valor in dados.items() if chave != "instituicao"}
    return {**campos, "instituicaoId": instituicoes[instituicao], "senha": SENHA}


def _resumo(usuarios):
    print(f"Dados de demonstração criados. Senha de todos os usuários: {SENHA}\n")
    for titulo, lista in (("Empresas", EMPRESAS), ("Professores", PROFESSORES), ("Alunos", ALUNOS)):
        print(titulo)
        for dados in lista:
            usuario = usuarios.buscar_por_login(dados["email"])
            saldo = f"  saldo {usuario.saldo}" if hasattr(usuario, "saldo") else ""
            print(f"  {dados['email']:<20} {dados['nome']}{saldo}")
        print()


if __name__ == "__main__":
    with create_app().app_context():
        semear()
