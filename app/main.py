from fastapi import FastAPI
from app.api.auth_router import router as auth_router
from app.api.colaborador_router import router as colaborador_router
from app.api.gestor_router import router as gestor_router
from app.api.financeiro_router import router as financeiro_router

app = FastAPI(
    title="API NexusCorp - Gestão de Reembolsos",
    description="API para centralizar a gestão de reembolsos e estabelecer regras de acesso.",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(colaborador_router)
app.include_router(gestor_router)
app.include_router(financeiro_router)

@app.get("/", tags=["Status"])
def health_check():
    return {"status": "ok", "mensagem": "API da NexusCorp está rodando!"}