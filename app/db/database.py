from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Cria a conexão com o banco de dados SQLite
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False} # Necessário para SQLite
)

# Cria a fábrica de sessões (para interagir com o banco)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os nossos modelos (tabelas)
Base = declarative_base()

# Função para obter a sessão do banco e fechar depois de usar
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()