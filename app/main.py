
from fastapi import FastAPI

from app.planes import router


app = FastAPI(
    title="API de Gimnasio",
    version="1.0.0"
)

app.include_router(router)

