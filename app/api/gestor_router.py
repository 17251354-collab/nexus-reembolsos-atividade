from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.db.database import get_db
from app.api.deps import require_role
from app.db.models import Usuario, PerfilEnum
from app.schemas.solicitacao import SolicitacaoResponse
from app.repositories import solicitacao_repo

router = APIRouter(prefix="/gestor", tags=["Gestor"])

class AnaliseRequest(BaseModel):
    observacao: str | None = None

@router.get("/solicitacoes", response_model=List[SolicitacaoResponse])
def listar_pendentes(
    db: Session = Depends(get_db), 
    usuario: Usuario = Depends(require_role([PerfilEnum.GESTOR]))
):
    return solicitacao_repo.listar_solicitacoes_departamento(db, usuario.departamento_id)

@router.post("/solicitacoes/{id}/aprovar", response_model=SolicitacaoResponse)
def aprovar(
    id: int,
    dados: AnaliseRequest,
    db: Session = Depends(get_db), 
    usuario: Usuario = Depends(require_role([PerfilEnum.GESTOR]))
):
    return solicitacao_repo.analisar_solicitacao_gestor(db, id, usuario, aprovado=True, observacao=dados.observacao)

@router.post("/solicitacoes/{id}/recusar", response_model=SolicitacaoResponse)
def recusar(
    id: int,
    dados: AnaliseRequest,
    db: Session = Depends(get_db), 
    usuario: Usuario = Depends(require_role([PerfilEnum.GESTOR]))
):
    return solicitacao_repo.analisar_solicitacao_gestor(db, id, usuario, aprovado=False, observacao=dados.observacao)