import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import io
from datetime import datetime
from Calculo import comision, descuento_comision, comision_tramite

# --- Configuración de página ---
st.set_page_config(page_title="Calculadora Credilight Mejoravit", page_icon="🏠", layout="centered")

# --- CSS personalizado ---
st.markdown("""
    <style>
    .main {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
    }
    .stButton button {
        background-color: #D32F2F;
        color: white;
        font-size: 18px;
        font-weight: bold;
        border-radius: 10px;
        padding: 10px 20px;
        border: none;
        cursor: pointer;
    }
    .stButton button:hover {
        background-color: #B71C1C;
    }
    .stNumberInput input, .stTextInput input {
        background-color: #f5f5f5;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Logo y título ---
st.image("logo.jpg", width=120)
st.markdown("<h1 style='text-align: center; color: #D32F2F;'>Calculadora Credilight Mejoravit</h1>", unsafe_allow_html=True)
st.write("Ingresa los datos del cliente para calcular el crédito y generar el desglose en PDF tipo factura.")

# --- Entradas ---
col1, col2 = st.columns(2)

with col1:
    persona = st.text_input("Nombre del cliente:")
    prestamo = st.number_input("Monto del crédito ($):", min_value=0.0, step=100.0, format="%.2f")

with col2:
    descuento_mensual = st.number_input("Descuento mensual ($):", min_value=0.0, step=100.0, format="%.2f")

# --- Cálculos ---
if persona and prestamo > 0 and descuento_mensual > 0:
    descuento_uno = comision(prestamo)
    subtotal = descuento_comision(prestamo, descuento_uno)
    total = comision_tramite(subtotal)
    descuento_semanal = descuento_mensual / 4
    fecha_reporte = datetime.now().strftime("%d/%m/%Y")

    # --- Resultados en tarjetas ---
    st.metric("Descuento comisión", f"-${descuento_uno:.2f}")
    st.metric("Sub Total", f"${subtotal:.2f}")
    st.metric("Costo de trámites", "-$6000.00")
    st.metric("Total", f"${total:.2f}")
    st.metric("Descuento semanal", f"-${descuento_semanal:.2f}")

    # --- Función para generar PDF tipo factura con aviso legal ---
    def generar_pdf(persona, prestamo, descuento_uno, subtotal, total, descuento_semanal, fecha):
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)

        # --- Bordes de factura ---
        c.setLineWidth(2)
        c.rect(40, 370, 520, 380)  # x, y, width, height

        # --- Logo a la derecha ---
        try:
            c.drawImage('logo.jpg', 450, 720, width=100, height=100)
        except:
            pass

        # --- Título centrado ---
        c.setFont('Helvetica-Bold',18)
        c.setFillColor(colors.HexColor('#D32F2F'))
        c.drawCentredString(300, 750, "Reporte Credilight Mejoravit")
        c.setFillColor(colors.black)

        # --- Nombre de la empresa y fecha ---
        c.setFont('Helvetica',12)
        c.drawString(50, 730, "Empresa: Credilight Mejoravit")
        c.drawString(50, 715, f"Fecha del reporte: {fecha}")

        # --- Tabla de desglose ---
        data = [
            ["Concepto", "Monto ($)"],
            ["Monto del crédito", f"{prestamo:.2f}"],
            ["Descuento comisión", f"-{descuento_uno:.2f}"],
            ["Sub Total", f"{subtotal:.2f}"],
            ["Costo de trámites", "-6000.00"],
            ["Total", f"{total:.2f}"],
            ["Descuento semanal", f"-{descuento_semanal:.2f}"]
        ]

        table = Table(data, colWidths=[300,150])
        style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#D32F2F')),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('GRID',(0,0),(-1,-1),1,colors.black),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 12),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f5f5f5'))
        ])
        table.setStyle(style)
        table.wrapOn(c, 50, 400)
        table.drawOn(c, 50, 450)

        # --- Línea separadora debajo de la tabla ---
        c.setLineWidth(1)
        c.line(50, 440, 550, 440)

        # --- Aviso legal pie de página ---
        c.setFont('Helvetica',9)
        aviso = ("Este documento es un resumen de crédito personal y no constituye una oferta de financiamiento. "
                 "Los términos finales del crédito Mejoravit están sujetos a aprobación de la institución financiera. "
                 "Los cálculos mostrados son referenciales y pueden variar según condiciones reales del crédito.")
        text = c.beginText(50, 420)
        text.setLeading(12)
        text.textLines(aviso)
        c.drawText(text)

        c.save()
        buffer.seek(0)
        return buffer

    # --- Botón para generar PDF ---
    if st.button("📄 Generar PDF"):
        pdf_buffer = generar_pdf(persona, prestamo, descuento_uno, subtotal, total, descuento_semanal, fecha_reporte)
        st.download_button("📥 Descargar PDF", pdf_buffer, file_name="desglose_factura_legal.pdf", mime="application/pdf")