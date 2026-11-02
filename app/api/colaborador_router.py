from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.api.deps import get_current_user
from app.db.models import Usuario
from app.schemas.solicitacao import SolicitacaoCreate, SolicitacaoUpdate, SolicitacaoResponse, SolicitacaoDetalheResponse
from app.repositories import solicitacao_repo

router = APIRouter(prefix="/colaborador", tags=["Colaborador"])

@router.post("/solicitacoes", response_model=SolicitacaoResponse, status_code=201)
def registrar_despesa(dados: SolicitacaoCreate, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return solicitacao_repo.criar_solicitacao(db, usuario.id, dados)

@router.get("/solicitacoes", response_model=List[SolicitacaoResponse])
def listar_despesas(db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return solicitacao_repo.listar_minhas_solicitacoes(db, usuario.id)

@router.get("/solicitacoes/{id}", response_model=SolicitacaoDetalheResponse)
def detalhar_despesa(id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return solicitacao_repo.obter_solicitacao(db, id, usuario.id)

@router.patch("/solicitacoes/{id}", response_model=SolicitacaoResponse)
def editar_despesa(id: int, dados: SolicitacaoUpdate, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return solicitacao_repo.atualizar_solicitacao(db, id, usuario.id, dados)

@router.delete("/solicitacoes/{id}", status_code=204)
def excluir_despesa(id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    solicitacao_repo.deletar_solicitacao(db, id, usuario.id)

@router.post("/solicitacoes/{id}/enviar", response_model=SolicitacaoResponse)
def enviar_despesa(id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return solicitacao_repo.enviar_para_gestor(db, id, usuario.id)