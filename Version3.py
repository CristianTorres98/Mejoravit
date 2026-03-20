import streamlit as st
import base64
import io
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.pdfbase.pdfmetrics import stringWidth

from Calculo import comision, descuento_comision, comision_tramite


# -------------------------------------------------
# CONFIGURACIÓN
# -------------------------------------------------
st.set_page_config(
    page_title="Calculadora Credilight Mejoravit",
    page_icon="🏠",
    layout="centered"
)


# -------------------------------------------------
# FONDO
# -------------------------------------------------
def set_background(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
    }}
    </style>
    """, unsafe_allow_html=True)

set_background("fondo.jpg")


# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.image("logo.jpg", width=120)
st.markdown("<h1 style='text-align:center; color:#D32F2F;'>Calculadora Credilight Mejoravit</h1>", unsafe_allow_html=True)
st.write("Ingresa los datos del cliente para calcular el crédito.")


# -------------------------------------------------
# PANTALLA BURÓ
# -------------------------------------------------
if "buro_confirmado" not in st.session_state:
    st.session_state["buro_confirmado"] = False

if not st.session_state["buro_confirmado"]:
    st.markdown("## ¿El cliente está en buró de crédito?")
    
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ No está en buró"):
            st.session_state["en_buro"] = False
            st.session_state["buro_confirmado"] = True
            st.rerun()

    with col2:
        if st.button("⚠️ Sí está en buró"):
            st.session_state["en_buro"] = True
            st.session_state["buro_confirmado"] = True
            st.rerun()

    st.stop()

if st.button("🔄 Cambiar respuesta de buró"):
    st.session_state["buro_confirmado"] = False
    st.rerun()


# -------------------------------------------------
# INPUTS
# -------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    persona = st.text_input("Nombre del cliente:")
    prestamo = st.number_input("Monto del crédito ($):", min_value=0.0, step=100.0, format="%.2f", value=None)

with col2:
    descuento_mensual = st.number_input("Descuento mensual ($):", min_value=0.0, step=100.0, format="%.2f", value=None)
    meses = st.number_input("Plazo (meses):", min_value=0, step=1)


# -------------------------------------------------
# PDF
# -------------------------------------------------
def generar_pdf(persona, prestamo, descuento_uno, subtotal, total,
                descuento_semanal, meses, fecha, en_buro):

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    c.setLineWidth(2)
    c.rect(40, 350, 520, 400)

    try:
        c.drawImage("logo.jpg", 450, 700, width=100, height=100)
    except:
        pass

    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.HexColor("#D32F2F"))
    c.drawCentredString(300, 770, "Reporte Credilight Mejoravit")
    c.setFillColor(colors.black)

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 700, f"Cliente: {persona}")

    c.setFont("Helvetica", 12)
    c.drawString(50, 680, "Empresa: Credilight Mejoravit")
    c.drawString(50, 660, f"Fecha del reporte: {fecha}")

    # TABLA
    data = [
        ["Concepto", "Monto ($)"],
        ["Monto del crédito", f"{prestamo:,.2f}"],
        ["Descuento comisión", f"-{descuento_uno:,.2f}"],
        ["Sub Total", f"{subtotal:,.2f}"],
        ["Costo de trámites", "-6,000.00"],
        ["Total", f"{total:,.2f}"],
        ["Descuento semanal", f"{descuento_semanal:,.2f}"],
        ["Plazo", f"{meses} meses"],
    ]

    table = Table(data, colWidths=[300, 150])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#D32F2F")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
    ]))

    table.wrapOn(c, 50, 400)
    table.drawOn(c, 50, 450)

    # -------------------------------------------------
    # LEYENDA ORIGINAL + EXTRA SI HAY BURÓ
    # -------------------------------------------------
    aviso = (
        "Este documento es un resumen de crédito personal y no constituye "
        "una oferta de financiamiento. Los términos finales del crédito "
        "Mejoravit están sujetos a aprobación de la institución financiera. "
        "Los cálculos mostrados son referenciales y pueden variar según "
        "condiciones reales del crédito."
    )

    if en_buro:
        aviso += " Nota: El cliente presenta historial en buró de crédito y se aplicó una reducción del 10%."

    c.setFont("Helvetica", 9)
    max_width = 500
    x_start = 50
    y_start = 420

    words = aviso.split(" ")
    line = ""
    lines = []

    for word in words:
        test_line = line + word + " "
        if stringWidth(test_line, "Helvetica", 9) <= max_width:
            line = test_line
        else:
            lines.append(line.strip())
            line = word + " "
    lines.append(line.strip())

    for i, l in enumerate(lines):
        c.drawString(x_start, y_start - i * 12, l)

    c.save()
    buffer.seek(0)
    return buffer


# -------------------------------------------------
# CALCULAR
# -------------------------------------------------
if st.button("🧮 Calcular"):

    if not persona or prestamo is None or descuento_mensual is None:
        st.warning("Completa los campos.")
        st.stop()

    en_buro = st.session_state.get("en_buro", False)

    if en_buro:
        prestamo = prestamo * 0.9
        st.warning("⚠️ Se aplicó reducción del 10% por buró.")

    descuento_uno = comision(prestamo)
    subtotal = descuento_comision(prestamo, descuento_uno)
    total = comision_tramite(subtotal)
    descuento_semanal = descuento_mensual / 4
    fecha = datetime.now().strftime("%d/%m/%Y")

    # 🔥 TABLA EN PANTALLA (REGRESÓ)
    conceptos = [
        "Monto del crédito",
        "Descuento comisión",
        "Sub Total",
        "Costo de trámites",
        "Total",
        "Descuento mensual",
        "Descuento semanal",
        "Plazo"
    ]

    montos = [
        f"${prestamo:,.2f}",
        f"-${descuento_uno:,.2f}",
        f"${subtotal:,.2f}",
        "-$6,000.00",
        f"${total:,.2f}",
        f"${descuento_mensual:,.2f}",
        f"${descuento_semanal:,.2f}",
        f"{meses} meses"
    ]

    tabla_html = "<table style='width:100%; border-collapse:collapse; background-color:white;'>"
    tabla_html += "<tr style='background-color:#D32F2F; color:white;'>"
    tabla_html += "<th>Concepto</th><th>Monto</th></tr>"

    for cpt, mnt in zip(conceptos, montos):
        tabla_html += f"<tr><td>{cpt}</td><td style='text-align:right;'>{mnt}</td></tr>"

    tabla_html += "</table>"

    st.markdown(tabla_html, unsafe_allow_html=True)

    st.session_state["pdf"] = generar_pdf(
        persona, prestamo, descuento_uno, subtotal,
        total, descuento_semanal, meses, fecha, en_buro
    )


# -------------------------------------------------
# DESCARGA
# -------------------------------------------------
if "pdf" in st.session_state:
    st.download_button(
        "📥 Descargar PDF",
        st.session_state["pdf"],
        file_name="credito.pdf"
    )