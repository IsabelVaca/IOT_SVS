import streamlit as st
from PIL import Image
import pandas as pd
import mysql.connector
import time
import plotly.graph_objects as go
import base64
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=10 * 1000, key="data_refresh")

def obtener_datos():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="reto_db"
    )
    df = pd.read_sql(
        "SELECT temperatura, corriente, vibracion, fecha FROM mediciones ORDER BY fecha DESC ", conn
    )
    conn.close()
    df['fecha'] = pd.to_datetime(df['fecha'])
    return df

def mostrar_tabla_mysql():
    st.subheader(" Datos desde MySQL")
    df = obtener_datos()
    st.dataframe(df, use_container_width=True)


#Calculos de estado de cada variable
def calc_temp_state(temperatura):
    if temperatura > 100:
        state = "critical"
        return state
    else:
        state = "normal"
        return state
    
def calc_corr_state(corriente):
    if corriente > 100:
        state = "critical"
        return state
    else:
        state = "normal"
        return state
    
def calc_vib_state(vibracion):
    if vibracion > 100:
        state = "critical"
        return state
    else:
        state = "normal"
        return state
    
#Renderizado de SVG
#implementado con IA 
def render_svg(svg_str: str, width: int = None) -> None:
    """Renderiza un SVG pasado como string usando base64"""
    b64 = base64.b64encode(svg_str.encode("utf-8")).decode("utf-8")
    img_html = f'<img src="data:image/svg+xml;base64,{b64}"'
    if width is not None:
        img_html += f' width="{width}"'
    img_html += ' />'
    st.markdown(img_html, unsafe_allow_html=True)

def calc_general_state(temp_state, corr_state, vib_state):
    if temp_state == "normal" and corr_state == "normal" and vib_state == "normal":
        with st.container():
            with open("1.svg", "r", encoding="utf-8") as f:
                svg_content = f.read()
            render_svg(svg_content, width=500)

            # Texto desplazado a la derecha con HTML + margin-left
            st.markdown(
                """
                <div style="margin-left: 170px; margin-top: -40px;">
                    <span style="color: #16c378; font-size: 28px;">
                        Estado: Óptimo
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

    elif ((temp_state == "critical" and corr_state == "critical") or
          (temp_state == "critical" and vib_state == "critical") or
          (corr_state == "critical" and vib_state == "critical")):
        with st.container():
            with open("2.svg", "r", encoding="utf-8") as f:
                svg_content = f.read()
            render_svg(svg_content, width=500)

            st.markdown(
                """
                <div style="margin-left: 170px; margin-top: -40px;">
                    <span style="color: #e5a100; font-size: 28px;">
                        Estado: Atención
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

    elif temp_state == "critical" and corr_state == "critical" and vib_state == "critical":
        with st.container():
            with open("3.svg", "r", encoding="utf-8") as f:
                svg_content = f.read()
            render_svg(svg_content, width=500)

            st.markdown(
                """
                <div style="margin-left: 170px; margin-top: -40px;">
                    <span style="color: #e63946; font-size: 28px;">
                        Estado: Crítico
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )


#Grafica de gauge
def mostrar_gauge(valor, tipo, min_val=0, max_val=100):
        # Título según la variable
    if tipo == 'temperatura':
        title_text = "Temperatura (°C)"
    elif tipo == 'vibracion':
        title_text = "Vibración"
    elif tipo == 'corriente':
        title_text = "Corriente (A)"
    else:
        title_text = str(tipo)

        # Puntos intermedios
    mid1 = min_val + (max_val - min_val) * 0.5   # 50%
    mid2 = min_val + (max_val - min_val) * 0.8   # 80%

    fig = go.Figure(go.Indicator(
         mode="gauge+number",
        value=valor,
        title={'text': title_text},
         gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': "#D6E1FF"},  
            'steps': [
                {'range': [min_val, mid1], 'color': "#34B1AA"},  # verde
                {'range': [mid1, mid2], 'color': "#E0B50F"},     # amarillo
                {'range': [mid2, max_val], 'color': "#F29F67"},  # naranja
               ],
            'threshold': {
                'line': {'color': "#FF3333", 'width': 4},
                'thickness': 0.75,
                'value': max_val
             }
          }
      ))
    st.plotly_chart(fig, use_container_width=True)

    


def main():
    
    #encabezado y configuración de página
    st.set_page_config(layout="wide")
    img = Image.open("logo.png")
    st.image(img, width=100)
    st.title("SVS")
    st.subheader("Monitoreo de licuadora")

    #obtener datos
    df = obtener_datos()

    #inicializar botones
    if "show_temp" not in st.session_state:
        st.session_state.show_temp = False
    if "show_vib" not in st.session_state:
        st.session_state.show_vib = False
    if "show_corr" not in st.session_state:
        st.session_state.show_corr = False
    if "show_temp" not in st.session_state:
        st.session_state.show_temp = False
    
    # Contenedores para las gráficas de gauge
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        left, middle, right = st.columns(3)
        titles = ["Temperatura", "Vibración", "Corriente"]
        
        with col1:
            with st.container(border = True):
                st.markdown("<h3 style='text-align: center;'>Temperatura</h3>", unsafe_allow_html=True)
                                            
                if 'temperatura' in df.columns and not df.empty:
                    promedio_temp = df['temperatura'].mean()
                    mostrar_gauge(promedio_temp, "temperatura",  min_val=0, max_val=100)
                else:
                    st.write("No hay datos de temperatura aún.")
                if left.button("Ver gráfico histórico", key="btn_temp", width="stretch"):
                    st.session_state.show_temp = not st.session_state.show_temp
                    if st.session_state.show_temp:
                        df = df.set_index('fecha')
                        st.line_chart(df['temperatura'])
        with col2:
            with st.container(border = True):
                st.markdown(f"<h3 style='text-align: center;'>{titles[1]}</h3>", unsafe_allow_html=True)
                if 'vibracion' in df.columns and not df.empty:
                    promedio_vib = df['vibracion'].mean()
                    mostrar_gauge(promedio_vib, "vibracion",  min_val=0, max_val=100)
                else:
                    st.write("No hay datos de vibración aún.")
                
                if middle.button("Ver gráfico histórico",key="btn_vib", width="stretch"):
                     st.session_state.show_vib = not st.session_state.show_vib
                     if st.session_state.show_vib:
                        df = df.set_index('fecha')
                        st.line_chart(df['vibracion'])

        with col3:
            with st.container(border = True):
                st.markdown(f"<h3 style='text-align: center;'>{titles[2]}</h3>", unsafe_allow_html=True)
                if 'corriente' in df.columns and not df.empty:
                    promedio_corr = df['corriente'].mean()
                    mostrar_gauge(promedio_corr, "corriente",  min_val=0, max_val=100)
                else:
                    st.write("No hay datos de corriente aún.")
                if right.button("Ver gráfico histórico", key="btn_corr", width="stretch"):
                    st.session_state.show_corr = not st.session_state.show_corr
                    if st.session_state.show_corr:
                        df = df.set_index('fecha')
                        st.line_chart(df['corriente'])

    #Calculo de estados
    temp_state = calc_temp_state(promedio_temp)
    corr_state = calc_corr_state(promedio_corr)
    vib_state = calc_vib_state(promedio_vib)

    #Mostrar estado general
    calc_general_state(temp_state, corr_state, vib_state)
   
    

    col1, col2, col3 = st.columns([0.5, 0.9, 2.2])


    if col2.button("Ver detalle de diagnóstico"):
        if temp_state == "normal" and corr_state == "normal" and vib_state == "normal":
            col2.markdown("Todos los sistemas operan dentro de los parámetros normales. No se requieren acciones adicionales.")

        elif ((temp_state == "critical" and corr_state == "critical") or
          (temp_state == "critical" and vib_state == "critical") or
          (corr_state == "critical" and vib_state == "critical")):
            col2.markdown("Múltiples variables en estado crítico. Se recomienda una revisión  del sistema.")

            text = "Variables en estado crítico:\n"
            if temp_state == "critical":
                text += "\n- Temperatura"
            if corr_state == "critical":
                text += "\n- Corriente"
            if vib_state == "critical":
                text += "\n- Vibración"
            col2.text(text)

        elif temp_state == "critical" and corr_state == "critical" and vib_state == "critical":
            col2.markdown("Todas las variables están en estado crítico. Acción inmediata requerida para evitar fallos graves.")


    

    if st.button("Consultar historial de lecturas",  width="stretch"):
        mostrar_tabla_mysql()
        df = obtener_datos()


  
    

if __name__ == '__main__':
    main()