from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.db.database import get_db
from app.api.deps import require_role
from app.db.models import Usuario, PerfilEnum
from app.schemas.solicitacao import SolicitacaoResponse
from app.repositories import solicitacao_repo

router = APIRouter(prefix="/financeiro", tags=["Financeiro"])

class AnaliseRequest(BaseModel):
    observacao: str | None = None

@router.get("/solicitacoes", response_model=List[SolicitacaoResponse])
def listar_pendentes(db: Session = Depends(get_db), usuario: Usuario = Depends(require_role([PerfilEnum.FINANCEIRO]))):
    return solicitacao_repo.listar_solicitacoes_financeiro(db)

@router.post("/solicitacoes/{id}/aprovar", response_model=SolicitacaoResponse)
def aprovar(id: int, dados: AnaliseRequest, db: Session = Depends(get_db), usuario: Usuario = Depends(require_role([PerfilEnum.FINANCEIRO]))):
    return solicitacao_repo.analisar_solicitacao_financeiro(db, id, usuario, aprovado=True, observacao=dados.observacao)

@router.post("/solicitacoes/{id}/recusar", response_model=SolicitacaoResponse)
def recusar(id: int, dados: AnaliseRequest, db: Session = Depends(get_db), usuario: Usuario = Depends(require_role([PerfilEnum.FINANCEIRO]))):
    return solicitacao_repo.analisar_solicitacao_financeiro(db, id, usuario, aprovado=False, observacao=dados.observacao)

@router.post("/solicitacoes/{id}/pagar", response_model=SolicitacaoResponse)
def pagar(id: int, dados: AnaliseRequest, db: Session = Depends(get_db), usuario: Usuario = Depends(require_role([PerfilEnum.FINANCEIRO]))):
    return solicitacao_repo.registrar_pagamento(db, id, usuario, observacao=dados.observacao)