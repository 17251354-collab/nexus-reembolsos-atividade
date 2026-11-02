from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Usuario
from app.core.security import verificar_senha, criar_token_acesso
from app.schemas.usuario import TokenResponse

router = APIRouter(prefix="/auth", tags=["Autenticação"])

@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Busca o usuário pelo e-mail (o Swagger usa 'username', vamos usar como email)
    usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()
    
    # Verifica se o usuário existe e se a senha está correta
    if not usuario or not verificar_senha(form_data.password, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos", # Não revela qual está errado (RN03)
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Cria o Token JWT
    token = criar_token_acesso(subject=str(usuario.id), perfil=usuario.perfil.value)
    
    return {"access_token": token, "token_type": "bearer"}