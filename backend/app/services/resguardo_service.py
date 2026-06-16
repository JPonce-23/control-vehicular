from docxtpl import DocxTemplate
from datetime import datetime
import os


def check(valor_actual, valor_esperado):
    if valor_actual is None:
        return ""
    return "✓" if str(valor_actual).lower().strip() == valor_esperado else ""


def normalizar_gasolina(valor_actual):
    if valor_actual is None:
        return ""
    
    valor_actual = str(valor_actual).lower().strip()

    equivalencias = {
        "vacio": "0",
        "vacío": "0",
        "0": "0",
        "cuarto": "1/4",
        "1/4": "1/4",
        "medio": "1/2",
        "1/2": "1/2",
        "tres cuartos": "3/4",
        "tres_cuartos": "3/4",
        "3/4": "3/4",
        "lleno": "4/4",
        "4/4": "4/4"
    }

    return equivalencias.get(valor_actual, valor_actual)


def normalizar_llantas(valor_actual):
    return normalizar_gasolina(valor_actual)


def formatear_fecha(fecha):
    if fecha is None:
        return "N/A"
    return fecha.strftime("%d/%m/%Y")


def mes_en_letra(fecha):
    if fecha is None:
        return ""

    meses = {
        1: "enero",
        2: "febrero",
        3: "marzo",
        4: "abril",
        5: "mayo",
        6: "junio",
        7: "julio",
        8: "agosto",
        9: "septiembre",
        10: "octubre",
        11: "noviembre",
        12: "diciembre"
    }
        
    return meses[fecha.month]


def valor(campo, default=""):
    if campo is None:
        return default

    texto = str(campo).strip()

    if texto.lower() == "string":
        return default

    return texto


def normalizar_clave(texto):
    texto = str(texto).lower().strip()
    reemplazos = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ñ": "n"
    }

    for original, reemplazo in reemplazos.items():
        texto = texto.replace(original, reemplazo)

    texto = texto.replace(" ", "_")
    return texto


def generar_checks_condiciones(condiciones):
    checks = {}

    for revision, item in condiciones:
        clave = normalizar_clave(item.nombre)
        estado = str(revision.estado).lower().strip()

        checks[f"{clave}_b"] = "✓" if estado == "bueno" else ""
        checks[f"{clave}_r"] = "✓" if estado == "regular" else ""
        checks[f"{clave}_m"] = "✓" if estado == "malo" else ""

    return checks


def generar_checks_inventario(inventario):
    checks = {}

    for revision, item in inventario:
        clave = normalizar_clave(item.nombre)
        estado = str(revision.estado).lower().strip()

        if estado == "correcto":
            checks[clave] = "✓"
        elif estado == "na":
            checks[clave] = "N/A"
        else:
            checks[clave] = ""

    return checks


def generar_resguardo_word(salida, regreso, vehiculo, persona, condiciones=None, inventario=None):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    carpeta_resguardos = os.path.join(BASE_DIR, "archivos", "resguardos")
    ruta_template = os.path.join(BASE_DIR, "templates", "resguardo_template.docx")

    os.makedirs(carpeta_resguardos, exist_ok=True)

    nombre_archivo = f"resguardo_salida_{salida.id}.docx"
    ruta_archivo = os.path.join(carpeta_resguardos, nombre_archivo)

    documento = DocxTemplate(ruta_template)

    nombre_persona = (
        f"{valor(persona.nombre, '')} "
        f"{valor(persona.apellido_paterno, '')} "
        f"{valor(persona.apellido_materno, '')}"
    ).strip()

    contexto = {
        "dia": datetime.now().strftime("%d"),
        "mes": datetime.now().strftime("%m"),
        "anio": datetime.now().strftime("%Y"),

        "fecha_salida": salida.fecha_salida.strftime("%d") if salida.fecha_salida else "",
        "fecha_regreso": regreso.fecha_regreso.strftime("%d") if regreso and regreso.fecha_regreso else "",
        "mes_regreso": mes_en_letra(regreso.fecha_regreso) if regreso and regreso.fecha_regreso else "",
        "anio_regreso": regreso.fecha_regreso.strftime("%Y") if regreso and regreso.fecha_regreso else "",

        "marca": valor(vehiculo.marca),
        "tipo": valor(vehiculo.tipo),
        "modelo": valor(vehiculo.modelo_anio),
        "cilindros": valor(vehiculo.cilindros),
        "num_motor": valor(vehiculo.num_motor),
        "num_serie": valor(vehiculo.num_serie),
        "num_poliza": valor(vehiculo.num_poliza),
        "placa": valor(vehiculo.placa),
        "num_inventario": valor(vehiculo.num_inventario),
        "num_economico": valor(vehiculo.num_economico),
        "color": valor(vehiculo.color),

        "tipo_movimiento": valor(salida.tipo_movimiento),
        "forma_movimiento": valor(salida.forma_movimiento),
        "fecha_inicio": formatear_fecha(salida.fecha_salida),
        "fecha_fin": formatear_fecha(salida.fecha_fin_provisional),
        "finalidad_uso": valor(salida.finalidad_uso),
        "finalidad_devolucion": valor(regreso.finalidad_devolucion if regreso else None),

        "num_oficio": valor(salida.num_oficio),
        "nombre_persona": nombre_persona,
        "num_expediente": valor(salida.num_expediente),
        "num_licencia": valor(persona.num_licencia),
        "rfc": valor(persona.rfc),
        "area_adscripcion": valor(salida.area_en_viaje),
        "cargo": valor(persona.cargo),
        "vigencia_licencia": valor(persona.vigencia_licencia),
        "tipo_licencia": valor(persona.tipo_licencia),

        "estado_llantas": valor(salida.estado_llantas_salida),
        "nivel_gasolina": valor(salida.nivel_gasolina_salida),
        "km_odometro_salida": valor(salida.km_odometro_salida),

        "num_tarjeta_gasolina": valor(vehiculo.num_tarjeta_gasolina, ""),

        "gasolina_0": check(normalizar_gasolina(salida.nivel_gasolina_salida), "0"),
        "gasolina_14": check(normalizar_gasolina(salida.nivel_gasolina_salida), "1/4"),
        "gasolina_12": check(normalizar_gasolina(salida.nivel_gasolina_salida), "1/2"),
        "gasolina_34": check(normalizar_gasolina(salida.nivel_gasolina_salida), "3/4"),
        "gasolina_44": check(normalizar_gasolina(salida.nivel_gasolina_salida), "4/4"),

        "llantas_14": check(normalizar_llantas(salida.estado_llantas_salida), "1/4"),
        "llantas_12": check(normalizar_llantas(salida.estado_llantas_salida), "1/2"),
        "llantas_34": check(normalizar_llantas(salida.estado_llantas_salida), "3/4"),
        "llantas_44": check(normalizar_llantas(salida.estado_llantas_salida), "4/4"),
    }

    contexto.update(generar_checks_condiciones(condiciones or []))
    contexto.update(generar_checks_inventario(inventario or []))

    documento.render(contexto)
    documento.save(ruta_archivo)

    return nombre_archivo, ruta_archivo