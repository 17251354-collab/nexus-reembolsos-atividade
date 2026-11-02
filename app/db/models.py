import enum
from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.database import Base

class PerfilEnum(str, enum.Enum):
    COLABORADOR = "COLABORADOR"
    GESTOR = "GESTOR"
    FINANCEIRO = "FINANCEIRO"

class SituacaoEnum(str, enum.Enum):
    RASCUNHO = "RASCUNHO"
    AGUARDANDO_GESTOR = "AGUARDANDO_GESTOR"
    AGUARDANDO_FINANCEIRO = "AGUARDANDO_FINANCEIRO"
    APROVADA = "APROVADA"
    PAGA = "PAGA"
    RECUSADA = "RECUSADA"

class Departamento(Base):
    __tablename__ = "departamentos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, index=True, nullable=False)

    usuarios = relationship("Usuario", back_populates="departamento")

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    perfil = Column(Enum(PerfilEnum), nullable=False)
    departamento_id = Column(Integer, ForeignKey("departamentos.id"), nullable=False)

    departamento = relationship("Departamento", back_populates="usuarios")
    solicitacoes = relationship("SolicitacaoReembolso", back_populates="solicitante")

class SolicitacaoReembolso(Base):
    __tablename__ = "solicitacoes_reembolso"

    id = Column(Integer, primary_key=True, index=True)
    solicitante_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    categoria = Column(String, nullable=False)
    valor = Column(Float, nullable=False)
    data_despesa = Column(Date, nullable=False)
    justificativa = Column(String, nullable=False)
    referencia_comprovante = Column(String, nullable=False)
    situacao = Column(Enum(SituacaoEnum), default=SituacaoEnum.RASCUNHO, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)

    solicitante = relationship("Usuario", back_populates="solicitacoes")
    historicos = relationship("HistoricoAnalise", back_populates="solicitacao")

class HistoricoAnalise(Base):
    __tablename__ = "historico_analises"

    id = Column(Integer, primary_key=True, index=True)
    solicitacao_id = Column(Integer, ForeignKey("solicitacoes_reembolso.id"), nullable=False)
    responsavel_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    etapa = Column(String, nullable=False) # Ex: GESTOR, FINANCEIRO
    decisao = Column(String, nullable=False) # Ex: APROVADO, RECUSADO
    data_decisao = Column(DateTime, default=datetime.utcnow)
    observacao = Column(String, nullable=True)

    solicitacao = relationship("SolicitacaoReembolso", back_populates="historicos")
    responsavel = relationship("Usuario")