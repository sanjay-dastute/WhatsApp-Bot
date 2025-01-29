from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes.whatsapp import router as whatsapp_router
from app.routes.admin import router as admin_router
from app.routes.auth import router as auth_router
from app.models.base import Base, engine
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import os

app = FastAPI(title="WhatsApp Bot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(whatsapp_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(admin_router, prefix="/api/v1/admin")

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
