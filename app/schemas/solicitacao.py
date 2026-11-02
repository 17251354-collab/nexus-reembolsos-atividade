from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
from typing import Optional, List
from app.db.models import SituacaoEnum

class SolicitacaoCreate(BaseModel):
    categoria: str
    valor: float = Field(..., gt=0, description="O valor deve ser maior que zero (RN04)")
    data_despesa: date
    justificativa: str
    referencia_comprovante: str

    @field_validator("data_despesa")
    @classmethod
    def validar_data(cls, v: date):
        if v > date.today():
            raise ValueError("Despesas com datas futuras não podem ser registradas (RN06)")
        return v

class SolicitacaoUpdate(BaseModel):
    categoria: Optional[str] = None
    valor: Optional[float] = Field(None, gt=0)
    data_despesa: Optional[date] = None
    justificativa: Optional[str] = None
    referencia_comprovante: Optional[str] = None

    @field_validator("data_despesa")
    @classmethod
    def validar_data(cls, v: Optional[date]):
        if v and v > date.today():
            raise ValueError("Despesas com datas futuras não podem ser registradas (RN06)")
        return v

class HistoricoResponse(BaseModel):
    id: int
    etapa: str
    decisao: str
    data_decisao: datetime
    observacao: Optional[str]
    responsavel_id: int

    class Config:
        from_attributes = True

class SolicitacaoResponse(BaseModel):
    id: int
    solicitante_id: int
    categoria: str
    valor: float
    data_despesa: date
    justificativa: str
    referencia_comprovante: str
    situacao: SituacaoEnum
    criado_em: datetime

    class Config:
        from_attributes = True

class SolicitacaoDetalheResponse(SolicitacaoResponse):
    historicos: List[HistoricoResponse] = []