import streamlit as st
from PIL import Image
import pandas as pd
import mysql.connector
import time
import plotly.graph_objects as go


def obtener_datos():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="reto_db"
    )
    df = pd.read_sql(
        "SELECT temperatura, corriente, vibracion, fecha FROM mediciones ORDER BY fecha DESC LIMIT 50", conn
    )
    conn.close()
    df['fecha'] = pd.to_datetime(df['fecha'])
    return df

def mostrar_gauge_1(temp, min_val=0, max_val=100):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=temp,
        title={'text': "Temperatura (°C)"},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': "#3B8FF3"},
            'steps': [
                {'range': [min_val, (min_val+max_val)/2], 'color': "#34B1AA"},
                {'range': [(min_val+max_val)/2, max_val], 'color': "#E0B50F"},
                {'range': [min_val + (max_val - min_val)*0.6, max_val], 'color': "#F29F67"},
            ],
            'threshold': {
                'line': {'color': "#FF3333", 'width': 15},
                'thickness': 0.85,
                'value': max_val  
            }
        }
    ))

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
            'bar': {'color': "#34B1AA"},  # Verde (tu paleta)
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
    

    st.set_page_config(layout="wide")
    img = Image.open("logo.png")
    st.image(img, width=100)
    st.title("SVS")
    st.subheader("Monitoreo de licuadora")
    df = obtener_datos()

    #inicializar botones
    if "show_temp" not in st.session_state:
        st.session_state.show_temp = False
    if "show_vib" not in st.session_state:
        st.session_state.show_vib = False
    if "show_corr" not in st.session_state:
        st.session_state.show_corr = False
    
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




    placeholder = st.empty()
    df = obtener_datos()

    with placeholder.container():
        st.subheader("Últimas mediciones")
        st.dataframe(df)

        # Asegúrate de que 'fecha' y 'valor' existan en tu tabla
        chart_df = df.set_index("fecha")[["valor"]]
        st.line_chart(chart_df)

    # Espera 5 segundos y vuelve a ejecutar todo
    time.sleep(5)
    st.experimental_rerun()

    

if __name__ == '__main__':
    main()