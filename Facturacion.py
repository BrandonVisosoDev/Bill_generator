import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib.pagesizes import letter

@st.cache(allow_output_mutation=True)
def obtener_productos():
    return []

def ingresar_producto():
    st.header("Ingresar Producto")
    
    articulo = st.text_input("Nombre del artículo a facturar:")
    cantidad = st.number_input("Cantidad a facturar:", min_value=0)
    precio = st.number_input("Precio del producto:", min_value=0.0)

    return articulo, cantidad, precio

def mostrar_tabla(productos):
    st.header("Productos Registrados")
    
    if not productos:
        st.info("Aún no hay productos registrados.")
    else:
        df = pd.DataFrame(productos, columns=["Artículo", "Cantidad", "Precio"])
        st.dataframe(df)

def calcular_factura(productos):
    st.header("Resumen de Factura")

    subtotal = sum(prod[1] * prod[2] for prod in productos)
    impuesto = st.number_input("Ingrese la cantidad de impuesto (%):", min_value=0.0, max_value=100.0)
    descuento = st.number_input("Ingrese la cantidad de descuento (%):", min_value=0.0, max_value=100.0)

    total = subtotal + (subtotal * (impuesto / 100)) - (subtotal * (descuento / 100))

    st.write(f"Subtotal: {subtotal}")
    st.write(f"Impuesto ({impuesto}%): {round(subtotal * (impuesto / 100), 2)}")

    # Formatear descuento y total con dos decimales
    descuento = round(subtotal * (descuento / 100), 2)
    st.write(f"Descuento: {descuento}")

    total = round(total, 2)
    st.write(f"Total: {total}")

    return {
        'subtotal': subtotal,
        'impuesto': impuesto,
        'impuesto_total': round(subtotal * (impuesto / 100), 2),
        'descuento': descuento,
        'total': total
    }

def generar_pdf(datos_factura, productos, de, cobrar_a, enviar_a, fecha_vencimiento, condicion_pago):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)

    # Configuración del PDF
    pdf.setFont("Helvetica", 12)

    # Encabezado
    pdf.drawCentredString(300, 750, "FACTURA")

    # Detalles de la factura
    pdf.drawString(100, 730, f"Factura: {datos_factura['numero_factura']}")
    pdf.drawString(100, 710, f"Fecha: {datos_factura['fecha_actual']}")
    pdf.drawString(100, 690, f"Fecha de Vencimiento: {fecha_vencimiento.strftime('%Y-%m-%d')}")
    pdf.drawString(100, 670, f"Condición de Pago: {condicion_pago}")

    # Detalles del cliente
    pdf.drawString(100, 640, f"De: {de}")
    pdf.drawString(100, 620, f"Cobrar a: {cobrar_a}")
    pdf.drawString(100, 600, f"Enviar a: {enviar_a}")

    # Separador
    pdf.line(100, 580, 500, 580)

    # Agregar detalles de productos
    pdf.drawString(100, 550, "Detalles de Productos:")
    y_position = 530
    for producto in productos:
        pdf.drawString(120, y_position, f"{producto[0]} - Cantidad: {producto[1]} - Precio: {producto[2]}")
        y_position -= 20

    # Agregar resumen de la factura
    pdf.drawString(100, y_position - 20, "Resumen de Factura:")
    pdf.drawString(120, y_position - 40, f"Subtotal: {datos_factura['subtotal']}")
    pdf.drawString(120, y_position - 60, f"Impuesto ({datos_factura['impuesto']}%): {datos_factura['impuesto_total']}")
    pdf.drawString(120, y_position - 80, f"Descuento: {datos_factura['descuento']}")
    pdf.drawString(120, y_position - 100, f"Total: {datos_factura['total']}")

    pdf.save()

    buffer.seek(0)
    return buffer

def main():
    st.image('LG.jpg', width=100)

    col1, col2 = st.columns(2)

    with col1:
        st.header("")
        de = st.text_input("De (Quien se factura):")
        cobrar_a = st.text_input("Cobrar a:")
        enviar_a = st.text_input("Enviar a:")

    with col2:
        st.header("Factura")
        num_factura = st.text_input("Número de Factura:")
        fecha_actual = st.date_input("Fecha Actual:")
        fecha_vencimiento = st.date_input("Fecha de Vencimiento:")
        condicion_pago = st.text_input("Condición de Pago:")

    productos = obtener_productos()

    articulo, cantidad, precio = ingresar_producto()

    if st.button("Agregar Producto"):
        productos.append([articulo, cantidad, precio])

    mostrar_tabla(productos)

    # Calcular la factura y mostrar el resumen
    datos_factura = calcular_factura(productos)
    datos_factura['numero_factura'] = num_factura
    datos_factura['fecha_actual'] = fecha_actual.strftime("%Y-%m-%d")

    # Botón para descargar PDF
    if st.button("Generar"):
        pdf_buffer = generar_pdf(datos_factura, productos, de, cobrar_a, enviar_a, fecha_vencimiento, condicion_pago)
        st.download_button(
            label="Descargar PDF",
            data=pdf_buffer,
            file_name="factura.pdf",
            key="pdf_download_button"
        )

if __name__ == "__main__":
    main()
