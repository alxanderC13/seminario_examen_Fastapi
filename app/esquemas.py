from pydantic import BaseModel, Field


class PlanBase(BaseModel):
    nombre: str = Field(min_length=3, max_length=60)
    precio_mensual: int = Field(ge=10, le=500)
    nivel: int = Field(ge=1, le=5)
    incluye_entrenador: bool = False


class PlanCrear(PlanBase):
    codigo: str = Field(pattern=r"^[A-Z]{3}\d{3}$")


class PlanActualizar(BaseModel):
    nombre: str | None = Field(default=None, min_length=3, max_length=60)
    precio_mensual: int | None = Field(default=None, ge=10, le=500)
    nivel: int | None = Field(default=None, ge=1, le=5)
    incluye_entrenador: bool | None = None


class Plan(PlanCrear):
    pass