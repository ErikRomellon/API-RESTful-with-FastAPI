#uvicorn main:app --host 0.0.0.0 --port 8080

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI()

# Entidades

#Entidad alumno
class Alumno(BaseModel):
    id: int
    nombres: str = Field(..., min_length=1)
    apellidos: str = Field(..., min_length=1)
    matricula: str = Field(..., min_length=1)
    promedio: float

#Entidad profesor
from pydantic import Field

class Profesor(BaseModel):
    id: int = Field(..., ge=1)
    nombres: str = Field(..., min_length=1)
    apellidos: str = Field(..., min_length=1)
    numeroEmpleado: int = Field(..., ge=1)
    horasClase: int = Field(..., ge=1)


# Almacenamiento en memoria
alumnos_db: List[Alumno] = []
profesores_db: List[Profesor] = []

# Rutas para Alumnos
@app.get("/alumnos", response_model=List[Alumno])
async def obtener_alumnos():
    return alumnos_db

@app.get("/alumnos/{id}", response_model=Alumno)
async def obtener_alumno(id: int):
    alumno = next((al for al in alumnos_db if al.id == id), None)
    if alumno is None:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    return alumno

@app.post("/alumnos", response_model=Alumno, status_code=201)
async def crear_alumno(alumno: Alumno):
    alumnos_db.append(alumno)
    return alumno

@app.put("/alumnos/{id}", response_model=Alumno)
async def actualizar_alumno(id: int, alumno: Alumno):
    for index, al in enumerate(alumnos_db):
        if al.id == id:
            alumnos_db[index] = alumno
            return alumno
    raise HTTPException(status_code=404, detail="Alumno no encontrado")

@app.delete("/alumnos/{id}", status_code=200)
async def eliminar_alumno(id: int):
    global alumnos_db
    alumno = next((al for al in alumnos_db if al.id == id), None)
    if alumno is None:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    alumnos_db = [al for al in alumnos_db if al.id != id]
    return {"detail": "Alumno eliminado"}

# Rutas para Profesores
@app.get("/profesores", response_model=List[Profesor])
async def obtener_profesores():
    return profesores_db

@app.get("/profesores/{id}", response_model=Profesor)
async def obtener_profesor(id: int):
    profesor = next((prof for prof in profesores_db if prof.id == id), None)
    if profesor is None:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    return profesor

@app.post("/profesores", response_model=Profesor, status_code=201)
async def crear_profesor(profesor: Profesor):
    try:
        profesores_db.append(profesor)
        return profesor
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@app.put("/profesores/{id}", response_model=Profesor)
async def actualizar_profesor(id: int, profesor: Profesor):
    for index, prof in enumerate(profesores_db):
        if prof.id == id:
            profesores_db[index] = profesor
            return profesor
    raise HTTPException(status_code=404, detail="Profesor no encontrado")

@app.delete("/profesores/{id}", status_code=200)
async def eliminar_profesor(id: int):
    global profesores_db
    profesor = next((al for al in profesores_db if al.id == id), None)
    if profesor is None:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    profesores_db = [prof for prof in profesores_db if prof.id != id]
    return {"detail": "Profesor eliminado"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [{"loc": err["loc"], "msg": err["msg"]} for err in exc.errors()]
    return JSONResponse(
        status_code=400,
        content={"detail": "Campos incorrectos o inválidos", "errors": errors},
    )
