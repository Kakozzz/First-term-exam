from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Optional
from passlib.context import CryptContext

# --- Configuración Inicial ---
app = FastAPI(title="Laboratorio de Fuerza Bruta Controlada")
# Usamos Bcrypt para hashear contraseñas de forma segura
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Modelos Pydantic ---
class UserInDB(BaseModel):
    # Modelo para el usuario ALMACENADO (guarda el hash)
    id: int
    username: str
    password_hash: str 
    email: Optional[str] = None
    is_active: bool = True

class UserCreate(BaseModel):
    # Modelo para la creación (recibe texto plano)
    username: str
    password: str 
    email: Optional[str] = None

class LoginRequest(BaseModel):
    # Modelo para el login (recibe texto plano)
    username: str
    password: str

# --- Funciones de Seguridad (Hashing) ---
def hash_password(password: str) -> str:
    """Hashea la contraseña usando Bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña en texto plano contra el hash almacenado."""
    return pwd_context.verify(plain_password, hashed_password)

# --- "Base de Datos" en Memoria y Precarga ---
db: Dict[int, UserInDB] = {}
next_id = 1

def preload_test_user():
    """Carga un usuario de prueba (lab_user:123456) al inicio de la API."""
    global next_id
    
    TEST_USERNAME = "lab_user"
    TEST_PASSWORD = "123456" 
    TEST_EMAIL = "target_brute_force@lab.com"
    
    # El ataque necesita que el hash de esta contraseña esté en la base de datos
    hashed_password = hash_password(TEST_PASSWORD)
    
    user = UserInDB(
        id=next_id,
        username=TEST_USERNAME, 
        password_hash=hashed_password,
        email=TEST_EMAIL,
        is_active=True
    )
    db[next_id] = user
    next_id += 1
    print(f"--- [LAB] Usuario de prueba '{TEST_USERNAME}' cargado (Contraseña: {TEST_PASSWORD}) ---")

# Ejecutar la precarga al iniciar el módulo
preload_test_user()

# --- Endpoints ---

@app.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    """Crea un nuevo usuario (almacenando el hash de la contraseña)."""
    global next_id
    
    if any(user.username == user_data.username for user in db.values()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El nombre de usuario ya existe")
    
    hashed_password = hash_password(user_data.password)
    
    user = UserInDB(
        id=next_id,
        username=user_data.username,
        password_hash=hashed_password,
        email=user_data.email
    )
    db[next_id] = user
    next_id += 1
    
    return {"id": user.id, "username": user.username, "email": user.email, "message": "Usuario creado exitosamente"}

@app.get("/users")
async def list_users():
    """Lista todos los usuarios (sin mostrar el hash)."""
    return [{"id": u.id, "username": u.username, "email": u.email, "is_active": u.is_active} for u in db.values()]

# --- ENDPOINT DE AUTENTICACIÓN (Objetivo del Ataque) ---

@app.post("/login")
async def login_user(form_data: LoginRequest):
    """Endpoint de autenticación, objetivo del ataque de fuerza bruta."""
    user = next((u for u in db.values() if u.username == form_data.username), None)
    
    # Mensaje genérico para no dar pistas sobre si el usuario existe o no
    if not user:
        return {"message": "Login fallido"} 

    # Verificar la contraseña contra el hash almacenado
    if not verify_password(form_data.password, user.password_hash):
        return {"message": "Login fallido"} 

    # Éxito
    return {"message": "Login exitoso"}
