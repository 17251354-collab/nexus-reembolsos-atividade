from pydantic import BaseModel, EmailStr
from typing import Optional
from app.db.models import PerfilEnum

class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr
    perfil: PerfilEnum
    departamento_id: int

class UsuarioCreate(UsuarioBase):
    senha: str

class UsuarioResponse(UsuarioBase):
    id: int

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: EmailStr
    senha: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"