from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.security import decodificar_token
from app.db.models import Usuario, PerfilEnum

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    credenciais_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou expiradas (RN01, RN14)",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decodificar_token(token)
    if not payload:
        raise credenciais_invalidas
    
    user_id = payload.get("sub")
    if user_id is None:
        raise credenciais_invalidas
        
    usuario = db.query(Usuario).filter(Usuario.id == int(user_id)).first()
    if usuario is None:
        raise credenciais_invalidas
        
    return usuario

def require_role(roles_permitidos: list[PerfilEnum]):
    def role_checker(usuario: Usuario = Depends(get_current_user)):
        if usuario.perfil not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para acessar este recurso."
            )
        return usuario
    return role_checker