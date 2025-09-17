import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import io
from datetime import datetime
from Calculo import comision, descuento_comision, comision_tramite
from reportlab.pdfbase.pdfmetrics import stringWidth

# --- Configuración de la página ---
st.set_page_config(page_title="Calculadora Credilight Mejoravit",
                   page_icon="🏠",
                   layout="centered")

# --- CSS personalizado ---
st.markdown("""
<style>
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
st.write("Ingresa los datos del cliente para calcular el crédito.")

# --- Entradas ---
col1, col2 = st.columns(2)
with col1:
    persona = st.text_input("Nombre del cliente:")
    prestamo = st.number_input("Monto del crédito ($):", min_value=0.0, step=100.0, format="%.2f")
with col2:
    descuento_mensual = st.number_input("Descuento mensual ($):", min_value=0.0, step=100.0, format="%.2f")

# --- Función para generar PDF ---
def generar_pdf(persona, prestamo, descuento_uno, subtotal, total, descuento_semanal, fecha):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Bordes tipo factura
    c.setLineWidth(2)
    c.rect(40, 350, 520, 400)

    # Logo a la derecha
    try:
        c.drawImage('logo.jpg', 450, 700, width=100, height=100)
    except:
        pass

    # Título centrado
    c.setFont('Helvetica-Bold',18)
    c.setFillColor(colors.HexColor('#D32F2F'))
    c.drawCentredString(300, 770, "Reporte Credilight Mejoravit")
    c.setFillColor(colors.black)

    # Nombre del cliente
    c.setFont('Helvetica-Bold',14)
    c.drawString(50, 700, f"Cliente: {persona}")

    # Empresa y fecha
    c.setFont('Helvetica',12)
    c.drawString(50, 680, "Empresa: Credilight Mejoravit")
    c.drawString(50, 660, f"Fecha del reporte: {fecha}")

    # Tabla de desglose
    data = [
        ["Concepto", "Monto ($)"],
        ["Monto del crédito", f"{prestamo:.2f}"],
        ["Descuento comisión", f"-{descuento_uno:.2f}"],
        ["Sub Total", f"{subtotal:.2f}"],
        ["Costo de trámites", "-6000.00"],
        ["Total", f"{total:.2f}"],           # <-- Fila a poner en negrita
        ["Descuento semanal", f"{descuento_semanal:.2f}"]
    ]

    table = Table(data, colWidths=[300,150])
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#D32F2F')),  # Header rojo
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 12),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f5f5f5')),
        ('FONTNAME', (0,5), (-1,5), 'Helvetica-Bold'),  # <-- Total en negrita
    ])
    table.setStyle(style)
    table.wrapOn(c, 50, 400)
    table.drawOn(c, 50, 450)

    # Línea separadora debajo tabla
    c.setLineWidth(1)
    c.line(50, 440, 550, 440)

    # Aviso legal pie dentro del marco
    aviso = ("Este documento es un resumen de crédito personal y no constituye una oferta de financiamiento. "
             "Los términos finales del crédito Mejoravit están sujetos a aprobación de la institución financiera. "
             "Los cálculos mostrados son referenciales y pueden variar según condiciones reales del crédito.")

    c.setFont('Helvetica',9)
    max_width = 500  # Ancho dentro del rectángulo
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
        c.drawString(x_start, y_start - i*12, l)

    c.save()
    buffer.seek(0)
    return buffer

# --- Botón Calcular ---
if st.button("🧮 Calcular"):
    if persona and prestamo > 0 and descuento_mensual > 0:
        # --- Cálculos ---
        descuento_uno = comision(prestamo)
        subtotal = descuento_comision(prestamo, descuento_uno)
        total = comision_tramite(subtotal)
        descuento_semanal = descuento_mensual / 4
        fecha_reporte = datetime.now().strftime("%d/%m/%Y")

        # --- Mostrar resultados ---
        st.metric("Descuento comisión", f"-${descuento_uno:.2f}")
        st.metric("Sub Total", f"${subtotal:.2f}")
        st.metric("Costo de trámites", "-$6000.00")
        st.metric("Total", f"${total:.2f}")
        st.metric("Descuento semanal", f"${descuento_semanal:.2f}")

        # --- Guardar PDF en sesión para descarga ---
        pdf_buffer = generar_pdf(persona, prestamo, descuento_uno, subtotal, total, descuento_semanal, fecha_reporte)
        st.session_state['pdf_buffer'] = pdf_buffer

# --- Botón para descargar PDF ---
if 'pdf_buffer' in st.session_state:
    st.download_button("📥 Descargar PDF", st.session_state['pdf_buffer'],
                       file_name="desglose_factura_cliente.pdf",
                       mime="application/pdf")