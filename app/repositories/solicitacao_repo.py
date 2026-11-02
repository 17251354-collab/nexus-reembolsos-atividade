from sqlalchemy.orm import Session
from app.db.models import SolicitacaoReembolso, SituacaoEnum, HistoricoAnalise, Usuario
from app.schemas.solicitacao import SolicitacaoCreate, SolicitacaoUpdate
from fastapi import HTTPException

def criar_solicitacao(db: Session, solicitante_id: int, dados: SolicitacaoCreate):
    duplicada = db.query(SolicitacaoReembolso).filter(
        SolicitacaoReembolso.solicitante_id == solicitante_id,
        SolicitacaoReembolso.referencia_comprovante == dados.referencia_comprovante
    ).first()
    if duplicada:
        raise HTTPException(status_code=400, detail="Já existe uma solicitação com esta referência (RN05)")

    nova = SolicitacaoReembolso(
        solicitante_id=solicitante_id, categoria=dados.categoria, valor=dados.valor,
        data_despesa=dados.data_despesa, justificativa=dados.justificativa,
        referencia_comprovante=dados.referencia_comprovante, situacao=SituacaoEnum.RASCUNHO
    )
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova

def listar_minhas_solicitacoes(db: Session, solicitante_id: int):
    return db.query(SolicitacaoReembolso).filter(SolicitacaoReembolso.solicitante_id == solicitante_id).all()

def obter_solicitacao(db: Session, solicitacao_id: int, solicitante_id: int):
    solicitacao = db.query(SolicitacaoReembolso).filter(
        SolicitacaoReembolso.id == solicitacao_id,
        SolicitacaoReembolso.solicitante_id == solicitante_id
    ).first()
    if not solicitacao:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")
    return solicitacao

def atualizar_solicitacao(db: Session, solicitacao_id: int, solicitante_id: int, dados: SolicitacaoUpdate):
    solicitacao = obter_solicitacao(db, solicitacao_id, solicitante_id)
    if solicitacao.situacao != SituacaoEnum.RASCUNHO:
        raise HTTPException(status_code=400, detail="Apenas rascunhos podem ser modificados (RN07)")
    
    for key, value in dados.model_dump(exclude_unset=True).items():
        setattr(solicitacao, key, value)
    db.commit()
    db.refresh(solicitacao)
    return solicitacao

def deletar_solicitacao(db: Session, solicitacao_id: int, solicitante_id: int):
    solicitacao = obter_solicitacao(db, solicitacao_id, solicitante_id)
    if solicitacao.situacao != SituacaoEnum.RASCUNHO:
        raise HTTPException(status_code=400, detail="Apenas rascunhos podem ser excluídos")
    db.delete(solicitacao)
    db.commit()

def enviar_para_gestor(db: Session, solicitacao_id: int, solicitante_id: int):
    solicitacao = obter_solicitacao(db, solicitacao_id, solicitante_id)
    if solicitacao.situacao != SituacaoEnum.RASCUNHO:
        raise HTTPException(status_code=400, detail="Apenas rascunhos podem ser enviados (RN07)")
    solicitacao.situacao = SituacaoEnum.AGUARDANDO_GESTOR
    db.commit()
    db.refresh(solicitacao)
    return solicitacao

def listar_solicitacoes_departamento(db: Session, departamento_id: int):
    return db.query(SolicitacaoReembolso).join(SolicitacaoReembolso.solicitante).filter(
        Usuario.departamento_id == departamento_id,
        SolicitacaoReembolso.situacao == SituacaoEnum.AGUARDANDO_GESTOR
    ).all()

def analisar_solicitacao_gestor(db: Session, solicitacao_id: int, gestor: Usuario, aprovado: bool, observacao: str = None):
    solicitacao = db.query(SolicitacaoReembolso).filter(SolicitacaoReembolso.id == solicitacao_id).first()
    if not solicitacao:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")
    if solicitacao.situacao != SituacaoEnum.AGUARDANDO_GESTOR:
        raise HTTPException(status_code=400, detail="Esta solicitação não está aguardando o gestor (RN08)")
    if solicitacao.solicitante.departamento_id != gestor.departamento_id:
        raise HTTPException(status_code=403, detail="Você só pode analisar solicitações do seu departamento (RN03)")
    if solicitacao.solicitante_id == gestor.id:
        raise HTTPException(status_code=403, detail="Você não pode aprovar sua própria solicitação (RN09)")
    if not aprovado and not observacao:
        raise HTTPException(status_code=400, detail="Para recusar, é obrigatório informar uma observação (RN11)")

    solicitacao.situacao = SituacaoEnum.AGUARDANDO_FINANCEIRO if aprovado else SituacaoEnum.RECUSADA
    historico = HistoricoAnalise(
        solicitacao_id=solicitacao.id, responsavel_id=gestor.id, etapa="GESTOR",
        decisao="APROVADO" if aprovado else "RECUSADO", observacao=observacao
    )
    db.add(historico)
    db.commit()
    db.refresh(solicitacao)
    return solicitacao

def listar_solicitacoes_financeiro(db: Session):
    return db.query(SolicitacaoReembolso).filter(
        SolicitacaoReembolso.situacao.in_([SituacaoEnum.AGUARDANDO_FINANCEIRO, SituacaoEnum.APROVADA])
    ).all()

def analisar_solicitacao_financeiro(db: Session, solicitacao_id: int, financeiro: Usuario, aprovado: bool, observacao: str = None):
    solicitacao = db.query(SolicitacaoReembolso).filter(SolicitacaoReembolso.id == solicitacao_id).first()
    if not solicitacao:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")
    if solicitacao.situacao != SituacaoEnum.AGUARDANDO_FINANCEIRO:
        raise HTTPException(status_code=400, detail="Esta solicitação não está aguardando o financeiro (RN08)")
    if solicitacao.solicitante_id == financeiro.id:
        raise HTTPException(status_code=403, detail="Você não pode aprovar sua própria solicitação (RN09)")
    if not aprovado and not observacao:
        raise HTTPException(status_code=400, detail="Para recusar, é obrigatório informar uma observação (RN11)")

    solicitacao.situacao = SituacaoEnum.APROVADA if aprovado else SituacaoEnum.RECUSADA
    historico = HistoricoAnalise(
        solicitacao_id=solicitacao.id, responsavel_id=financeiro.id, etapa="FINANCEIRO",
        decisao="APROVADO" if aprovado else "RECUSADO", observacao=observacao
    )
    db.add(historico)
    db.commit()
    db.refresh(solicitacao)
    return solicitacao

def registrar_pagamento(db: Session, solicitacao_id: int, financeiro: Usuario, observacao: str = None):
    solicitacao = db.query(SolicitacaoReembolso).filter(SolicitacaoReembolso.id == solicitacao_id).first()
    if not solicitacao:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")
    if solicitacao.situacao != SituacaoEnum.APROVADA:
        raise HTTPException(status_code=400, detail="Apenas solicitações APROVADAS podem ser pagas (RN10)")
        
    solicitacao.situacao = SituacaoEnum.PAGA
    historico = HistoricoAnalise(
        solicitacao_id=solicitacao.id, responsavel_id=financeiro.id, etapa="PAGAMENTO",
        decisao="PAGO", observacao=observacao
    )
    db.add(historico)
    db.commit()
    db.refresh(solicitacao)
    return solicitacao