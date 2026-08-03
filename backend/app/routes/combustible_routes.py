from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from app.database import get_db
from app.models.presupuesto_gasolina_model import PresupuestoGasolina
from app.models.gasto_gasolina_model import GastoGasolina
from app.schemas.combustible_schema import (
    PresupuestoCrear, PresupuestoRespuesta,
    GastoCrear, GastoRespuesta,
    ResumenMes, ReporteCombustible, ReporteMes,
    ViajeRespuesta
)
from app.services.auth_service import requerir_rol, obtener_usuario_actual
from datetime import date
from app.models.vehiculo_model import Vehiculo

router = APIRouter(tags=["Combustible"])


# ─── 1. Crear presupuesto anual ─────────────────────────────

@router.post("/vehiculos/{vehiculo_id}/presupuesto-gasolina", response_model=PresupuestoRespuesta, status_code=201)
def crear_presupuesto(
    vehiculo_id: int,
    datos: PresupuestoCrear,
    db: Session = Depends(get_db),
    usuario_actual = Depends(requerir_rol(["administrador"]))
):
    
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    anio_actual = date.today().year
    anios_permitidos = [anio_actual, anio_actual + 1]

    if datos.anio not in anios_permitidos:
        raise HTTPException(
            status_code=400,
            detail="Solo se puede crear presupuesto para el año actual o el año siguiente"
    )

    if datos.mes_inicio > datos.mes_fin:
        raise HTTPException(status_code=400, detail="El mes de inicio no puede ser mayor al mes de fin")

    if vehiculo.estado == "fuera_de_servicio":
        raise HTTPException(
            status_code=400,
            detail="El vehículo puede consultarse en el resumen, pero no recibir un presupuesto nuevo mientras esté fuera de servicio"
        )

    existente = db.query (PresupuestoGasolina).filter(
        PresupuestoGasolina.vehiculo_id == vehiculo_id,
        PresupuestoGasolina.anio == datos.anio
    ).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe un presupuesto para este vehículo y año")

    meses_activos = datos.mes_fin - datos.mes_inicio + 1
    monto_por_mes = datos.monto_autorizado_total / meses_activos

    nuevo = PresupuestoGasolina(
        vehiculo_id=vehiculo_id,
        monto_autorizado_total=datos.monto_autorizado_total,
        monto_por_mes=monto_por_mes,
        monto_utilizado=0,
        saldo_acumulado=datos.monto_autorizado_total,
        anio=datos.anio,
        mes_inicio=datos.mes_inicio,
        mes_fin=datos.mes_fin
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    monto_restante = nuevo.monto_autorizado_total - nuevo.monto_utilizado
    porcentaje_restante = float((monto_restante / nuevo.monto_autorizado_total) * 100) if nuevo.monto_autorizado_total > 0 else 0.0

    return PresupuestoRespuesta(
        presupuesto_id=nuevo.id,
        vehiculo_id=nuevo.vehiculo_id,
        anio=nuevo.anio,
        mes_inicio=nuevo.mes_inicio,
        mes_fin=nuevo.mes_fin,
        monto_autorizado_total=nuevo.monto_autorizado_total,
        monto_por_mes=nuevo.monto_por_mes,
        monto_utilizado=nuevo.monto_utilizado,
        monto_restante=monto_restante,
        porcentaje_restante=round(porcentaje_restante, 2)
    )
    
# ─── 2. Consultar presupuesto anual ─────────────────────────

@router.get("/vehiculos/{vehiculo_id}/presupuesto-gasolina", response_model=PresupuestoRespuesta)
def consultar_presupuesto(
    vehiculo_id: int,
    anio: int,
    db: Session = Depends(get_db),
    usuario_actual = Depends(obtener_usuario_actual)
):
    presupuesto = db.query(PresupuestoGasolina).filter(
        PresupuestoGasolina.vehiculo_id == vehiculo_id,
        PresupuestoGasolina.anio == anio
    ).first()

    if not presupuesto:
        raise HTTPException(status_code=404, detail="No existe presupuesto para este vehículo y año")

    monto_restante = presupuesto.monto_autorizado_total - presupuesto.monto_utilizado
    porcentaje_restante = float((monto_restante / presupuesto.monto_autorizado_total) * 100) if presupuesto.monto_autorizado_total > 0 else 0.0

    return PresupuestoRespuesta(
        presupuesto_id=presupuesto.id,
        vehiculo_id=presupuesto.vehiculo_id,
        anio=presupuesto.anio,
        mes_inicio=presupuesto.mes_inicio,
        mes_fin=presupuesto.mes_fin,
        monto_autorizado_total=presupuesto.monto_autorizado_total,
        monto_por_mes=presupuesto.monto_por_mes,
        monto_utilizado=presupuesto.monto_utilizado,
        monto_restante=monto_restante,
        porcentaje_restante=round(porcentaje_restante, 2)
    )
    
    
    
# ─── 3. Registrar gasto de gasolina ─────────────────────────

@router.post("/vehiculos/{vehiculo_id}/gastos-gasolina", response_model=GastoRespuesta, status_code=201)
def registrar_gasto(
    vehiculo_id: int,
    datos: GastoCrear,
    db: Session = Depends(get_db),
    usuario_actual = Depends(requerir_rol(["administrador", "capturista"]))
):
    from app.models.vehiculo_model import Vehiculo
    from app.models.salida_model import Salida

    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    if datos.nivel_tanque is not None and datos.nivel_tanque not in {"vacio", "cuarto", "medio", "tres_cuartos", "lleno"}:
        raise HTTPException(status_code=400, detail="Nivel de tanque no válido")
    if datos.km_odometro is not None and datos.km_odometro < 0:
        raise HTTPException(status_code=400, detail="El kilometraje no puede ser negativo")

    # Validar que la salida exista y pertenezca a este vehículo
    salida = db.query(Salida).filter(
        Salida.id == datos.salida_id,
        Salida.vehiculo_id == vehiculo_id
    ).first()
    if not salida:
        raise HTTPException(status_code=400, detail="La salida indicada no existe o no pertenece a este vehículo")

    # Buscar presupuesto por vehículo y año del gasto
    anio_gasto = datos.fecha_gasto.year
    presupuesto = db.query(PresupuestoGasolina).filter(
        PresupuestoGasolina.vehiculo_id == vehiculo_id,
        PresupuestoGasolina.anio == anio_gasto
    ).first()
    if not presupuesto:
        raise HTTPException(status_code=404, detail=f"No existe presupuesto para este vehículo en el año {anio_gasto}")

    if not (presupuesto.mes_inicio <= datos.fecha_gasto.month <= presupuesto.mes_fin):
        raise HTTPException(
            status_code=400,
            detail="La fecha del gasto está fuera del rango de meses autorizado"
        )

    utilizado_actual = db.query(func.sum(GastoGasolina.monto)).filter(
        GastoGasolina.presupuesto_id == presupuesto.id
    ).scalar() or 0
    if utilizado_actual + datos.monto > presupuesto.monto_autorizado_total:
        raise HTTPException(
            status_code=400,
            detail="El gasto excede el monto disponible del presupuesto"
        )

    # Insertar el gasto
    nuevo_gasto = GastoGasolina(
        vehiculo_id=vehiculo_id,
        salida_id=datos.salida_id,
        presupuesto_id=presupuesto.id,
        fecha_gasto=datos.fecha_gasto,
        monto=datos.monto,
        nivel_tanque=datos.nivel_tanque,
        km_odometro=datos.km_odometro,
        nota=datos.nota,
        capturado_por=usuario_actual.id
    )
    db.add(nuevo_gasto)

    # Recalcular monto utilizado incluyendo el gasto aún no confirmado.
    total_utilizado = utilizado_actual + datos.monto

    presupuesto.monto_utilizado = total_utilizado
    presupuesto.saldo_acumulado = presupuesto.monto_autorizado_total - total_utilizado

    # Actualizar km_acumulado del vehículo si corresponde
    if datos.km_odometro and datos.km_odometro > (vehiculo.km_acumulado or 0):
        vehiculo.km_acumulado = datos.km_odometro

    db.commit()
    db.refresh(nuevo_gasto)

    return GastoRespuesta(
        id=nuevo_gasto.id,
        vehiculo_id=nuevo_gasto.vehiculo_id,
        salida_id=nuevo_gasto.salida_id,
        presupuesto_id=nuevo_gasto.presupuesto_id,
        fecha_gasto=nuevo_gasto.fecha_gasto,
        monto=nuevo_gasto.monto,
        nivel_tanque=nuevo_gasto.nivel_tanque.value if nuevo_gasto.nivel_tanque else None,
        km_odometro=nuevo_gasto.km_odometro,
        nota=nuevo_gasto.nota,
        capturado_por=nuevo_gasto.capturado_por,
        fecha_registro=nuevo_gasto.fecha_registro
    )
    
    
    
    
# ─── 4. Listar gastos de gasolina ───────────────────────────

@router.get("/vehiculos/{vehiculo_id}/gastos-gasolina", response_model=list[GastoRespuesta])
def listar_gastos(
    vehiculo_id: int,
    anio: int,
    db: Session = Depends(get_db),
    usuario_actual = Depends(obtener_usuario_actual)
):
    from app.models.vehiculo_model import Vehiculo

    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    gastos = db.query(GastoGasolina).filter(
        GastoGasolina.vehiculo_id == vehiculo_id,
        extract("year", GastoGasolina.fecha_gasto) == anio
    ).order_by(GastoGasolina.fecha_gasto.desc()).all()

    return [
        GastoRespuesta(
            id=g.id,
            vehiculo_id=g.vehiculo_id,
            salida_id=g.salida_id,
            presupuesto_id=g.presupuesto_id,
            fecha_gasto=g.fecha_gasto,
            monto=g.monto,
            nivel_tanque=g.nivel_tanque.value if g.nivel_tanque else None,
            km_odometro=g.km_odometro,
            nota=g.nota,
            capturado_por=g.capturado_por,
            fecha_registro=g.fecha_registro
        )
        for g in gastos
    ]
    
# ─── 5. Resumen del vehículo y presupuesto ──────────────────

@router.get("/vehiculos/{vehiculo_id}/gastos-gasolina/resumen")
def resumen_gasolina(
    vehiculo_id: int,
    anio: int,
    db: Session = Depends(get_db),
    usuario_actual = Depends(obtener_usuario_actual)
):
    from app.models.vehiculo_model import Vehiculo

    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    presupuesto = db.query(PresupuestoGasolina).filter(
        PresupuestoGasolina.vehiculo_id == vehiculo_id,
        PresupuestoGasolina.anio == anio
    ).first()
    if not presupuesto:
        raise HTTPException(status_code=404, detail=f"No existe presupuesto para este vehículo en el año {anio}")

    monto_restante = presupuesto.monto_autorizado_total - presupuesto.monto_utilizado
    porcentaje_restante = float((monto_restante / presupuesto.monto_autorizado_total) * 100) if presupuesto.monto_autorizado_total > 0 else 0.0

    ultimo_gasto = db.query(GastoGasolina).filter(
        GastoGasolina.vehiculo_id == vehiculo_id
    ).order_by(GastoGasolina.fecha_gasto.desc()).first()

    return {
        "vehiculo": {
            "id": vehiculo.id,
            "num_economico": vehiculo.num_economico,
            "placa": vehiculo.placa,
            "marca": vehiculo.marca,
            "tipo": vehiculo.tipo,
            "num_serie": vehiculo.num_serie,
            "num_tarjeta_gasolina": vehiculo.num_tarjeta_gasolina,
            "km_acumulado": float(vehiculo.km_acumulado) if vehiculo.km_acumulado else None
        },
        "presupuesto": {
            "id": presupuesto.id,
            "anio": presupuesto.anio,
            "monto_autorizado_total": float(presupuesto.monto_autorizado_total),
            "monto_por_mes": float(presupuesto.monto_por_mes),
            "monto_utilizado": float(presupuesto.monto_utilizado),
            "monto_restante": float(monto_restante),
            "porcentaje_restante": round(porcentaje_restante, 2)
        },
        "ultimo_gasto": {
            "fecha_gasto": ultimo_gasto.fecha_gasto if ultimo_gasto else None,
            "monto": float(ultimo_gasto.monto) if ultimo_gasto else None,
            "nivel_tanque": ultimo_gasto.nivel_tanque.value if ultimo_gasto and ultimo_gasto.nivel_tanque else None,
            "km_odometro": float(ultimo_gasto.km_odometro) if ultimo_gasto and ultimo_gasto.km_odometro else None
        }
    }
    
    
# ─── 6. Reporte mensual para gráficas ───────────────────────

@router.get("/vehiculos/{vehiculo_id}/reporte-combustible", response_model=ReporteCombustible)
def reporte_combustible(
    vehiculo_id: int,
    anio: int,
    db: Session = Depends(get_db),
    usuario_actual = Depends(obtener_usuario_actual)
):
    from app.models.vehiculo_model import Vehiculo

    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    presupuesto = db.query(PresupuestoGasolina).filter(
        PresupuestoGasolina.vehiculo_id == vehiculo_id,
        PresupuestoGasolina.anio == anio
    ).first()
    if not presupuesto:
        raise HTTPException(status_code=404, detail=f"No existe presupuesto para este vehículo en el año {anio}")

    # Agrupar gastos por mes solo dentro del rango del presupuesto
    gastos_por_mes = db.query(
        extract("month", GastoGasolina.fecha_gasto).label("mes_numero"),
        func.sum(GastoGasolina.monto).label("total_mes")
    ).filter(
        GastoGasolina.vehiculo_id == vehiculo_id,
        extract("year", GastoGasolina.fecha_gasto) == anio,
        extract("month", GastoGasolina.fecha_gasto) >= presupuesto.mes_inicio,
        extract("month", GastoGasolina.fecha_gasto) <= presupuesto.mes_fin
    ).group_by(
        extract("month", GastoGasolina.fecha_gasto)
    ).all()

    gastos_dict = {int(row.mes_numero): float(row.total_mes) for row in gastos_por_mes}

    nombres_meses = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]

    reporte = []
    gasto_acumulado = 0.0
    monto_total = float(presupuesto.monto_autorizado_total)
    meses_activos = presupuesto.mes_fin - presupuesto.mes_inicio + 1
    monto_por_mes = monto_total / meses_activos

    for mes_num in range(presupuesto.mes_inicio, presupuesto.mes_fin + 1):
        gasto_mes = gastos_dict.get(mes_num, 0.0)
        gasto_acumulado += gasto_mes
        monto_restante_mes = monto_por_mes - gasto_mes
        monto_restante_total = monto_total - gasto_acumulado

        reporte.append(ReporteMes(
            mes_numero=mes_num,
            mes=nombres_meses[mes_num - 1],
            monto_autorizado_mes=round(monto_por_mes, 2),
            gasto_mes=gasto_mes,
            monto_restante_mes=round(monto_restante_mes, 2),
            gasto_acumulado=round(gasto_acumulado, 2),
            monto_restante_total=round(monto_restante_total, 2)
        ))

    return ReporteCombustible(
        vehiculo_id=vehiculo_id,
        anio=anio,
        reporte=reporte
    )
    
    
    
    
    
# ─── 7. Viajes por vehículo ──────────────────────────────────

@router.get("/vehiculos/{vehiculo_id}/viajes", response_model=list[ViajeRespuesta])
def listar_viajes(
    vehiculo_id: int,
    anio: int = None,
    db: Session = Depends(get_db),
    usuario_actual = Depends(obtener_usuario_actual)
):
    from app.models.vehiculo_model import Vehiculo
    from app.models.salida_model import Salida
    from app.models.regreso_model import Regreso
    from app.models.persona_model import PersonaAutorizada

    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    query = db.query(Salida).filter(Salida.vehiculo_id == vehiculo_id)

    if anio:
        query = query.filter(extract("year", Salida.fecha_salida) == anio)

    salidas = query.order_by(Salida.fecha_salida.desc()).all()

    resultado = []
    for salida in salidas:
        regreso = db.query(Regreso).filter(Regreso.salida_id == salida.id).first()
        persona = db.query(PersonaAutorizada).filter(PersonaAutorizada.id == salida.persona_id).first()

        km_salida = float(salida.km_odometro_salida) if salida.km_odometro_salida else None
        km_regreso = float(regreso.km_odometro_regreso) if regreso and regreso.km_odometro_regreso else None
        kilometros_recorridos = None
        if km_salida is not None and km_regreso is not None:
            kilometros_recorridos = round(km_regreso - km_salida, 2)

        resultado.append(ViajeRespuesta(
            salida_id=salida.id,
            vehiculo_id=salida.vehiculo_id,
            persona=f"{persona.nombre} {persona.apellido_paterno}" if persona else "Sin persona asignada",
            fecha_salida=salida.fecha_salida,
            fecha_regreso=regreso.fecha_regreso if regreso else None,
            km_salida=km_salida,
            km_regreso=km_regreso,
            kilometros_recorridos=kilometros_recorridos,
            finalidad_uso=salida.finalidad_uso if hasattr(salida, "finalidad_uso") else None,
            finalidad_devolucion=regreso.finalidad_devolucion if regreso and hasattr(regreso, "finalidad_devolucion") else None
        ))

    return resultado