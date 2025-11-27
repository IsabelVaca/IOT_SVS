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

def mostrar_gauge(temp, min_val=0, max_val=100):
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

    st.plotly_chart(fig, use_container_width=True)

def main():
    

    st.set_page_config(layout="wide")
    img = Image.open("logo.png")
    st.image(img, width=100)
    st.title("SVS")
    st.subheader("Monitoreo de licuadora")
    df = obtener_datos()
    
    with st.container(border=True):
        st.write("This is inside the container")
        col1, col2, col3 = st.columns(3)
        titles = ["Temperatura", "Vibración", "Corriente"]
        
        with col1:
            with st.container(border = True):
                st.title(titles[0])
                                            
                if 'temperatura' in df.columns and not df.empty:
                    promedio_temp = df['temperatura'].mean()
                    mostrar_gauge(promedio_temp, min_val=0, max_val=100)
                else:
                    st.write("No hay datos de temperatura aún.")
        with col2:
            with st.container(border = True):
                st.title(titles[1])

        with col3:
            with st.container(border = True):
                st.title(titles[2])

    # (Opcional) gráfica de la serie histórica
    df = df.set_index('fecha')
    st.line_chart(df['temperatura'])

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