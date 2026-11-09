from app.extensions import db
from app.models.transacao import Transacao


class TransacaoRepository:
    def registrar(self, transacao, *entidades_alteradas):
        db.session.add(transacao)
        for entidade in entidades_alteradas:
            db.session.add(entidade)
        db.session.commit()
        return transacao

    def listar_por_professor(self, professor_id):
        return (
            Transacao.query.filter_by(professor_id=professor_id)
            .order_by(Transacao.data.desc())
            .all()
        )

    def listar_por_aluno(self, aluno_id):
        return (
            Transacao.query.filter_by(aluno_id=aluno_id)
            .order_by(Transacao.data.desc())
            .all()
        )
    
    def listar_todas(self):
        return Transacao.query.order_by(Transacao.data.desc()).all()