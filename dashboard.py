import streamlit as st
from PIL import Image
import pandas as pd
import mysql.connector
import time
import plotly.graph_objects as go
import base64
from streamlit_autorefresh import st_autorefresh
from streamlit_echarts import st_echarts
from streamlit_extras.stylable_container import stylable_container
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import plotly.express as px


#auto refresh cada 12 segundos
st_autorefresh(interval=12 * 1000, key="data_refresh")
#obtener datos desde MySQL
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
#mostrar tabla de datos
def mostrar_tabla_mysql():
    st.subheader(" Datos desde MySQL")
    df = obtener_datos()
    st.dataframe(df, use_container_width=True)

#Graficas de temperatura
def grafica_area_temperatura(df):
    fechas = df["fecha"].dt.strftime("%H:%M:%S").tolist()
    valores = df["temperatura"].tolist()

    options = {
        "xAxis": {"type": "category", "data": fechas},
        "yAxis": {"type": "value"},
        "series": [
            {"data": valores, "type": "line", "areaStyle": {}}
        ]
    }
    
    st_echarts(options=options, height="400px")


def grafica_area_corr(df):
    fechas = df["fecha"].dt.strftime("%H:%M:%S").tolist()
    valores = df["temperatura"].tolist()

    options = {
        "xAxis": {"type": "category", "data": fechas},
        "yAxis": {"type": "value"},
        "series": [
            {"data": valores, "type": "line", "areaStyle": {}}
        ]
    }
    
    st_echarts(options=options, height="400px")

def grafica_area_vib(df):
    fechas = df["fecha"].dt.strftime("%H:%M:%S").tolist()
    valores = df["temperatura"].tolist()

    options = {
        "xAxis": {"type": "category", "data": fechas},
        "yAxis": {"type": "value"},
        "series": [
            {"data": valores, "type": "line", "areaStyle": {}}
        ]
    }
    
    st_echarts(options=options, height="400px")

#Calculos de estado de cada variable
def calc_temp_state(temperatura):
    if temperatura >= 70:
        state = "critical"
        return state
    else:
        state = "normal"
        return state
    
def calc_corr_state(corriente):
    if corriente >= 13:
        state = "critical"
        return state
    else:
        state = "normal"
        return state
    
def calc_vib_state(vibracion):
    if vibracion >= 3:
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

#Cálculo y renderizado del estado general
def calc_general_state(temp_state, corr_state, vib_state):
    if ((temp_state == "normal" and corr_state == "normal" and vib_state == "normal") or 
    (temp_state == "critical" and corr_state == "normal" and vib_state == "normal" ) 
          or
          (temp_state == "normal" and vib_state == "critical" and corr_state == "normal") or
          (corr_state == "critical" and vib_state == "normal" and temp_state == "normal")):
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

    elif ((temp_state == "critical" and corr_state == "critical" and vib_state == "normal" ) 
          or
          (temp_state == "critical" and vib_state == "critical" and corr_state == "normal") or
          (corr_state == "critical" and vib_state == "critical" and temp_state == "normal")):
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

#Gráficas de gauge
def mostrar_gauge(valor, tipo):
    # Definir rangos y límites según tipo
    if tipo == 'temperatura':
        title_text = "Temperatura (°C)"
        min_val, max_val = 0, 100
        green_min, green_max = 40, 60
        yellow_min, yellow_max = 50, 70
        red_min = 70

    elif tipo == 'corriente':
        title_text = "Corriente (A)"
        min_val, max_val = 0, 20
        green_min, green_max = 0, 12
        yellow_min, yellow_max = 12, 12.9 
        red_min = 13

    else:
        title_text = str(tipo)
        # valores genéricos
        min_val, max_val = 0, 5
        green_min, green_max = min_val, min_val + (max_val - min_val) * 0.5
        yellow_min, yellow_max = 0, 3
        red_min = 3

    # construir grafico
    steps = []
    steps.append({'range': [min_val, green_max], 'color': "#34B1AA"})
    if yellow_min is not None and yellow_max is not None:
        steps.append({'range': [green_max, yellow_max], 'color': "#E0B50F"})
    steps.append({'range': [red_min, max_val], 'color': "#F29F67"})

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=valor,
        title={'text': title_text},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': "#D6E1FF"},
            'steps': steps,
            'threshold': {
                'line': {'color': "#FF3333", 'width': 4},
                'thickness': 0.75,
                'value': red_min
            }
        }
    ))
    # Estilo de fondo transparente
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(fig, use_container_width=True)

#Predicción de fallas usando regresión lineal
def predecir_falla(df, limite_temp, limite_vib, limite_corr):

    df = df.copy()

    # Convertimos fecha a número de segundos desde el inicio
    df["t_num"] = (df["fecha"] - df["fecha"].min()).dt.total_seconds()

    X = df[["t_num"]]

    variables = ["temperatura", "vibracion", "corriente"]
    limites = [limite_temp, limite_vib, limite_corr]
    tiempos_falla = []

    for var, limite in zip(variables, limites):

        y = df[var]

        model = LinearRegression()
        model.fit(X, y)

        m = model.coef_[0]
        b = model.intercept_

        # Solo si la tendencia es ascendente
        if m > 0:
            t_falla = (limite - b) / m
            if t_falla > df["t_num"].max():
                tiempos_falla.append(t_falla)

    if len(tiempos_falla) == 0:
        return None

    t_falla_real = min(tiempos_falla)

    fecha_falla = df["fecha"].min() + pd.to_timedelta(t_falla_real, unit="s")

    return fecha_falla



# GRAFICAR PREDICCIÓN
def graficar_prediccion(df, fecha_falla):
    fig, ax = plt.subplots()

    ax.plot(df["fecha"], df["temperatura"], label="Temperatura")
    ax.plot(df["fecha"], df["vibracion"], label="Vibración")
    ax.plot(df["fecha"], df["corriente"], label="Corriente")

    if fecha_falla is not None:
        ax.axvline(fecha_falla, linestyle="--", color="red",
                   label=f"Posible falla: {fecha_falla.date()}")

    ax.set_xlabel("Tiempo")
    ax.set_ylabel("Valores de sensores")
    ax.set_title("Predicción de fecha de falla del dispositivo")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    st.pyplot(fig)

    


def main():
    
    #encabezado y configuración de página
    st.set_page_config(layout="wide")
    with stylable_container(
                key="header", 
                 css_styles="""
                 {
                 background-color: #3C81EB;
                 border-radius: 8px;
                 padding: 20px;
                }
                 """
            ):
        co1,co2 = st.columns([3,0.2])
        with co1:
            st.title("SVS — Monitoreo de licuadora")
        with co2:
            img = Image.open("logo.png")
            st.image(img, width=150)

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
            with stylable_container(
                key="card_temp", 
                 css_styles="""
                 {
                 background-color: #272B4A;
                 border-radius: 8px;
                 padding: 20px;
                }
                 """
            ):
            
                st.markdown("<h3 style='text-align: center;'>Temperatura</h3>", unsafe_allow_html=True)
                                            
                if 'temperatura' in df.columns and not df.empty:
                    promedio_temp = df['temperatura'].mean()
                    mostrar_gauge(promedio_temp, "temperatura")
                else:
                    st.write("No hay datos de temperatura aún.")
                if left.button("Ver gráfico histórico", key="btn_temp", width="stretch", type="primary"):
                    st.session_state.show_temp = not st.session_state.show_temp
                    if st.session_state.show_temp:
                        df_temp = df.copy()
                        df_temp = df_temp.set_index('fecha')
                        st.line_chart(df_temp['temperatura'])
                        df_sorted = df.sort_values('fecha')
                        
        with col2:
            with stylable_container(
                key="card_vib", 
                 css_styles="""
                 {
                 background-color: #272B4A;
                 border-radius: 8px;
                 padding: 20px;
                }
                 """
            ):
                st.markdown(f"<h3 style='text-align: center;'>{titles[1]}</h3>", unsafe_allow_html=True)
                if 'vibracion' in df.columns and not df.empty:
                    promedio_vib = df['vibracion'].mean()
                    mostrar_gauge(promedio_vib, "vibración")
                else:
                    st.write("No hay datos de vibración aún.")
                
                if middle.button("Ver gráfico histórico",key="btn_vib", width="stretch", type="primary"):
                     st.session_state.show_vib = not st.session_state.show_vib
                     if st.session_state.show_vib:
                        df = df.set_index('fecha')
                        st.line_chart(df['vibracion'])

        with col3:
            with stylable_container(
                key="card_corr", 
                 css_styles="""
                 {
                 background-color: #272B4A;
                 border-radius: 8px;
                 padding: 20px;
                }
                 """
            ):
                st.markdown(f"<h3 style='text-align: center;'>{titles[2]}</h3>", unsafe_allow_html=True)
                if 'corriente' in df.columns and not df.empty:
                    promedio_corr = df['corriente'].mean()
                    mostrar_gauge(promedio_corr, "corriente")
                else:
                    st.write("No hay datos de corriente aún.")
                if right.button("Ver gráfico histórico", key="btn_corr", width="stretch", type="primary"):
                    st.session_state.show_corr = not st.session_state.show_corr
                    if st.session_state.show_corr:
                        df = df.set_index('fecha')
                        st.line_chart(df['corriente'])

    #Calculo de estados
    temp_state = calc_temp_state(promedio_temp)
    corr_state = calc_corr_state(promedio_corr)
    vib_state = calc_vib_state(promedio_vib)
    

    col_left, col_right = st.columns([1.5, 1.5])
    with col_left:
        with stylable_container(
                key="sys_state", 
                 css_styles="""
                 {
                 background-color: #272B4A;
                 border-radius: 8px;
                 padding: 20px;
                }
                 """
            ):
            #Mostrar estado general
            calc_general_state(temp_state, corr_state, vib_state)
            colu_espacio = st.columns(1)

            col1, col2, col3 = st.columns([1, 0.9, 1.1])


            if col2.button("Ver detalle de diagnóstico",  type="primary"):
                if ((temp_state == "normal" and corr_state == "normal" and vib_state == "normal") or 
    (temp_state == "critical" and corr_state == "normal" and vib_state == "normal" ) 
          or
          (temp_state == "normal" and vib_state == "critical" and corr_state == "normal") or
          (corr_state == "critical" and vib_state == "normal" and temp_state == "normal")):
                    col2.markdown("Todos los sistemas operan dentro de los parámetros normales. No se requieren acciones adicionales.")

                elif ((temp_state == "critical" and corr_state == "critical" and vib_state == "normal" ) 
          or
          (temp_state == "critical" and vib_state == "critical" and corr_state == "normal") or
          (corr_state == "critical" and vib_state == "critical" and temp_state == "normal")):
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

    with col_right:
        with stylable_container(
                key="prediction", 
                 css_styles="""
                 {
                 background-color: #272B4A;
                 border-radius: 8px;
                 padding: 20px;
                }
                 """
            ):
            st.subheader(" Predicción de Falla del Dispositivo")

            df_pred = obtener_datos()
            lim_temp = 70
            lim_vib = 9.0
            lim_corr = 15
            fecha_falla = predecir_falla(df_pred,
                                        lim_temp,
                                        lim_vib,
                                        lim_corr)

            if fecha_falla is not None:
                st.error(f"Posible falla estimada alrededor de: **{fecha_falla}**")
            else:
                st.success("El sistema no muestra tendencia de falla en el corto plazo.")
            
            graficar_prediccion(df_pred, fecha_falla)

            col_espacio1 = st.columns(1, )
                    
    
    col_espacio2 = st.columns(1)
    #botón para mostrar tabla de datos
    if st.button("Consultar historial de lecturas", type="primary",  width="stretch"):
        mostrar_tabla_mysql()
        df = obtener_datos()


  
    

if __name__ == '__main__':
    main()