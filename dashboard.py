import streamlit as st
from PIL import Image
import pandas as pd
import mysql.connector
import time


def obtener_datos():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="iot_db"
    )
    df = pd.read_sql(
        "SELECT * FROM temperaturas ORDER BY fecha DESC LIMIT 50",
        conn
    )
    conn.close()
    return df


def main():
    

    st.set_page_config(layout="wide")
    img = Image.open("logo.png")
    st.image(img, width=200)
    st.title("SVS")
    st.subheader("Monitoreo de licuadora")

    with st.container(border=True):
        st.write("This is inside the container")
        cols = st.columns(3)
        titles = ["Temperatura", "Vibración", "Corriente"]
        for col, title in zip(cols, titles):
            with col:
                # aquí cada columna tendrá su título distinto
                st.title(title)
                # … puedes añadir más widgets dentro de cada columna …
                st.write("Aquí va el valor del sensor de", title.lower())

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