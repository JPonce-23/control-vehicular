from docx import Document
from datetime import datetime
import os


def generar_resguardo_word(salida, regreso, vehiculo, persona):
    carpeta_resguardos = "archivos/resguardos"
    os.makedirs(carpeta_resguardos, exist_ok=True)

    nombre_archivo = f"resguardo_salida_{salida.id}.docx"
    ruta_archivo = os.path.join(carpeta_resguardos, nombre_archivo)

    documento = Document()

    documento.add_heading("CONTROL DE ENTREGAS Y DEVOLUCIONES DE PARQUE VEHICULAR", level=1)

    documento.add_paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y')}")

    documento.add_heading("I. Datos del vehículo", level=2)
    documento.add_paragraph(f"Marca: {vehiculo.marca}")
    documento.add_paragraph(f"Tipo: {vehiculo.tipo}")
    documento.add_paragraph(f"Modelo: {vehiculo.modelo_anio}")
    documento.add_paragraph(f"Placas: {vehiculo.placa}")
    documento.add_paragraph(f"No. Serie: {vehiculo.num_serie}")
    documento.add_paragraph(f"Color: {vehiculo.color}")
    documento.add_paragraph(f"Kilometraje actual: {vehiculo.km_acumulado}")

    documento.add_heading("II. Datos del asignatario", level=2)
    documento.add_paragraph(f"Nombre: {persona.nombre} {persona.apellido_paterno}")
    documento.add_paragraph(f"No. Licencia: {persona.num_licencia}")
    documento.add_paragraph(f"Vigencia licencia: {persona.vigencia_licencia}")
    documento.add_paragraph(f"Tipo licencia: {persona.tipo_licencia}")

    documento.add_heading("III. Datos de salida", level=2)
    documento.add_paragraph(f"Fecha salida: {salida.fecha_salida}")
    documento.add_paragraph(f"Finalidad de uso: {salida.finalidad_uso}")
    documento.add_paragraph(f"Kilometraje salida: {salida.km_odometro_salida}")
    documento.add_paragraph(f"Nivel gasolina salida: {salida.nivel_gasolina_salida}")
    documento.add_paragraph(f"Estado llantas salida: {salida.estado_llantas_salida}")

    documento.add_heading("IV. Datos de regreso", level=2)

    if regreso:
        documento.add_paragraph(f"Fecha regreso: {regreso.fecha_regreso}")
        documento.add_paragraph(f"Kilometraje regreso: {regreso.km_odometro_regreso}")
        documento.add_paragraph(f"Nivel gasolina regreso: {regreso.nivel_gasolina_regreso}")
        documento.add_paragraph(f"Estado llantas regreso: {regreso.estado_llantas_regreso}")
        documento.add_paragraph(f"Estado vehículo regreso: {regreso.estado_vehiculo_regreso}")
        documento.add_paragraph(f"Finalidad devolución: {regreso.finalidad_devolucion}")
    else:
        documento.add_paragraph("Sin regreso registrado.")

    documento.add_heading("V. Firmas", level=2)
    documento.add_paragraph("\n\n__________________________________")
    documento.add_paragraph("Persona que recibe")

    documento.add_paragraph("\n\n__________________________________")
    documento.add_paragraph("Persona que entrega")

    documento.save(ruta_archivo)

    return nombre_archivo, ruta_archivo