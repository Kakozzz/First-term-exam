from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, Field
from typing import List, Dict, Any, Optional
import random

class Usuario(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre_usuario: str
    contrasena: str
    email: Optional[str] = None
    is_active: bool = Field(default=True)

class UsuarioLogin(SQLModel):
    nombre_usuario: str
    contrasena: str

class CrearUsuario(SQLModel):
    nombre_usuario: str
    contrasena: str
    email: Optional[str] = None

usuarios_db: List[Dict[str, Any]] = [
    {"id": random.randint(10000, 99999), "nombre_usuario": "user1", "contrasena": "a1c", "email": "user1@example.com", "is_active": True}
]

def generar_id_usuario() -> int:
    while True:
        nuevo_id = random.randint(10000, 99999)
        if not any(u["id"] == nuevo_id for u in usuarios_db):
            return nuevo_id

app = FastAPI(
    title="API de Gestión de Usuarios",
    description="API by kakozz."
)

@app.get("/")
async def leer_raiz():
    return {"mensaje": "Bienvenido al API de Gestión de Usuarios"}

@app.post("/login")
async def iniciar_sesion(usuario: UsuarioLogin):
    for u in usuarios_db:
        if usuario.nombre_usuario == u["nombre_usuario"] and usuario.contrasena == u["contrasena"]:
            return {"mensaje": "Login correcto", "usuario": u["nombre_usuario"]}
    raise HTTPException(status_code=401, detail="Credenciales inválidas")

@app.post("/users", response_model=Usuario)
async def crear_usuario(usuario_data: CrearUsuario):
    if any(u['nombre_usuario'] == usuario_data.nombre_usuario for u in usuarios_db):
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso")
    
    nuevo_usuario_dict = {
        "id": generar_id_usuario(),
        "nombre_usuario": usuario_data.nombre_usuario,
        "contrasena": usuario_data.contrasena,
        "email": usuario_data.email,
        "is_active": True
    }
    
    usuarios_db.append(nuevo_usuario_dict)
    return nuevo_usuario_dict

@app.get("/users", response_model=List[Usuario])
async def listar_usuarios():
    return usuarios_db

@app.get("/users/{usuario_id}", response_model=Usuario)
async def obtener_usuario(usuario_id: int):
    for u in usuarios_db:
        if u.get("id") == usuario_id:
            return u
    raise HTTPException(status_code=404, detail=f"Usuario con id {usuario_id} no encontrado")

@app.put("/users/{usuario_id}", response_model=Usuario)
async def actualizar_usuario(usuario_id: int, datos: dict):
    for u in usuarios_db:
        if u.get("id") == usuario_id:
            for key, value in datos.items():
                if key not in ["id", "contrasena"]:
                    u[key] = value
            return u
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

@app.delete("/users/{usuario_id}")
async def eliminar_usuario(usuario_id: int):
    for index, u in enumerate(usuarios_db):
        if u.get("id") == usuario_id:
            usuarios_db.pop(index)
            return {"mensaje": "Usuario eliminado"}
    raise HTTPException(status_code=404, detail="Usuario no encontrado")
