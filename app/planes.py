
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.datos import PLANES
from app.esquemas import Plan, PlanActualizar, PlanCrear


router = APIRouter(prefix="/planes", tags=["planes"])


# Dependencia
def obtener_plan(codigo: str) -> dict:
    for plan in PLANES:
        if plan["codigo"] == codigo.upper():
            return plan

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No existe el plan '{codigo}'"
    )


PlanEncontrado = Annotated[dict, Depends(obtener_plan)]


# Pregunta 1 - Listar planes
@router.get("", response_model=list[Plan])
def listar_planes(
    nivel: Annotated[int | None, Query(ge=1, le=5)] = None,
    solo_con_entrenador: bool = False
) -> list[dict]:

    resultado = PLANES

    if nivel is not None:
        resultado = [
            p for p in resultado if p["nivel"] == nivel
        ]

    if solo_con_entrenador:
        resultado = [
            p for p in resultado if p["incluye_entrenador"]
        ]

    return resultado


# Pregunta 1 - Crear plan
@router.post(
    "",
    response_model=Plan,
    status_code=status.HTTP_201_CREATED
)
def crear_plan(nuevo: PlanCrear) -> dict:

    if any(p["codigo"] == nuevo.codigo for p in PLANES):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El plan '{nuevo.codigo}' ya existe"
        )

    PLANES.append(nuevo.model_dump())

    return PLANES[-1]


# Pregunta 2 - Facturacion
@router.get("/facturacion")
def facturacion(
    meses: Annotated[int, Query(ge=1, le=24)],
    nivel: Annotated[int | None, Query(ge=1, le=5)] = None
) -> dict:

    seleccion = [
        p for p in PLANES
        if nivel is None or p["nivel"] == nivel
    ]

    if not seleccion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay planes para la selección"
        )

    cantidad = len(seleccion)

    precios = sum(
        p["precio_mensual"] for p in seleccion
    )

    con_entrenador = sum(
        1 for p in seleccion if p["incluye_entrenador"]
    )

    base = precios * meses

    descuento = meses >= 12

    estimada = base * 0.85 if descuento else base

    return {
        "planes": cantidad,
        "meses": meses,
        "precio_promedio": round(precios / cantidad, 2),
        "facturacion_base": base,
        "descuento_aplicado": descuento,
        "facturacion_estimada": round(float(estimada), 2),
        "porcentaje_con_entrenador": round(
            con_entrenador * 100 / cantidad, 1
        )
    }


# Pregunta 3 - Planes contratados
@router.get("/contratados")
def planes_contratados(
    contratados: Annotated[list[str] | None, Query()] = None
) -> dict:

    codigos = {
        c.upper() for c in (contratados or [])
    }

    total = 0
    cantidad_contratados = 0
    disponibles = 0
    ingreso = 0

    mas_caro = None
    precio_mayor = 0

    for plan in PLANES:

        total += 1

        if plan["codigo"] in codigos:
            cantidad_contratados += 1

        else:
            disponibles += 1
            ingreso += plan["precio_mensual"]

            if plan["precio_mensual"] > precio_mayor:
                precio_mayor = plan["precio_mensual"]
                mas_caro = plan["codigo"]

    if total == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay planes registrados"
        )

    return {
        "total": total,
        "contratados": cantidad_contratados,
        "disponibles": disponibles,
        "porcentaje_contratacion": round(
            cantidad_contratados * 100 / total, 1
        ),
        "ingreso_potencial_disponibles": ingreso,
        "plan_disponible_mas_caro": mas_caro
    }


# Pregunta 1 - Consultar por codigo
@router.get("/{codigo}", response_model=Plan)
def ver_plan(plan: PlanEncontrado) -> dict:
    return plan


# Pregunta 1 - Actualizar
@router.put("/{codigo}", response_model=Plan)
def actualizar_plan(
    cambios: PlanActualizar,
    plan: PlanEncontrado
) -> dict:

    plan.update(
        cambios.model_dump(exclude_unset=True)
    )

    return plan


# Pregunta 1 - Eliminar
@router.delete(
    "/{codigo}",
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar_plan(plan: PlanEncontrado) -> None:
    PLANES.remove(plan)
