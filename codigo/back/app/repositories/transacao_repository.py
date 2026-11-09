"""Repositório das transações (envios de moedas e trocas por vantagem)."""
from app.extensions import db
from app.models.transacao import EnvioMoeda, Transacao
from app.repositories.base_repository import BaseRepository


class TransacaoRepository(BaseRepository):
    model = Transacao

    def registrar(self, transacao, *entidades_alteradas):
        """Grava a transação e os saldos alterados em um único commit."""
        db.session.add(transacao)
        db.session.add_all(entidades_alteradas)
        self._confirmar()
        return transacao

    def listar_todas(self):
        return self._mais_recentes(Transacao.query).all()

    def listar_por_professor(self, professor_id):
        """Extrato do professor: os envios que ele realizou."""
        consulta = EnvioMoeda.query.filter_by(professor_id=professor_id)
        return self._mais_recentes(consulta).all()

    def listar_por_aluno(self, aluno_id):
        """Extrato do aluno: moedas recebidas e trocas por vantagem."""
        consulta = Transacao.query.filter_by(aluno_id=aluno_id)
        return self._mais_recentes(consulta).all()

    def existe_para_professor(self, professor_id):
        consulta = EnvioMoeda.query.filter_by(professor_id=professor_id)
        return db.session.query(consulta.exists()).scalar()

    def existe_para_aluno(self, aluno_id):
        return self._existe(Transacao.aluno_id, aluno_id)

    def _mais_recentes(self, consulta):
        return consulta.order_by(Transacao.data.desc(), Transacao.id.desc())
