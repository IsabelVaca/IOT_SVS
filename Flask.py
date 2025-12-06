from flask import Flask, request
import mysql.connector

app = Flask(__name__)

# Conexión a MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="reto_db"
)

@app.route('/data', methods=['POST'])
def recibir_datos():
    temperatura = request.form.get('temperatura')
    humedad = request.form.get('humedad')
    vibracion = request.form.get('vibracion')
    corriente = request.form.get('corriente')

    cursor = db.cursor()

    sql = """
    INSERT INTO mediciones (temperatura, humedad, corriente, vibracion)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(sql, (float(temperatura), float(humedad), float(corriente), vibracion))
    db.commit()
    cursor.close()

    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)