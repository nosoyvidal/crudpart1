from flask import Flask, jsonify, request
from flask_cors import CORS
import pymysql
from cryptography.fernet import Fernet

# Clave secreta
clave_secreta = b'k0AUPtAyaeQRUsBG4vpxlLA4Dci0y6-T-hCSfMWJaGc='
f = Fernet(clave_secreta)

app = Flask(__name__)
CORS(app)

# Conexión a BD
def conectar():
    try:
        conn = pymysql.connect(host='localhost', user='root', passwd='root', db='gestor_contra', charset='utf8mb4')
        print("✅ Conexión a BD exitosa")
        return conn
    except Exception as e:
        print("❌ Error al conectar a la BD:", e)
        return None

# Consultar todos
@app.route("/")
def consulta_general():
    try:
        conn = conectar()
        if conn is None:
            return jsonify({'mensaje': 'Error de conexión a BD'})
        cur = conn.cursor()
        cur.execute("SELECT * FROM baul")
        datos = cur.fetchall()
        print(f"📄 Datos obtenidos: {datos}")
        data = []
        for row in datos:
            try:
                clave_desencriptada = f.decrypt(row[3].encode()).decode()
            except Exception as e:
                print(f"❌ Error desencriptando la clave de id {row[0]}:", e)
                clave_desencriptada = "Error al desencriptar"

            dato = {'id_baul': row[0], 'Plataforma': row[1], 'usuario': row[2], 'clave': clave_desencriptada}
            data.append(dato)
        cur.close()
        conn.close()
        return jsonify({'baul': data, 'mensaje': 'Baúl de contraseñas'})
    except Exception as ex:
        print("❌ Error en consulta_general:", ex)
        return jsonify({'mensaje': 'Error en consulta_general'})

# Consultar uno
@app.route("/consulta_individual/<codigo>", methods=['GET'])
def consulta_individual(codigo):
    try:
        conn = conectar()
        if conn is None:
            return jsonify({'mensaje': 'Error de conexión'})
        cur = conn.cursor()
        cur.execute("SELECT * FROM baul WHERE id_baul=%s", (codigo,))
        datos = cur.fetchone()
        cur.close()
        conn.close()
        if datos:
            try:
                clave_desencriptada = f.decrypt(datos[3].encode()).decode()
            except Exception as e:
                print(f"❌ Error desencriptando clave id {datos[0]}:", e)
                clave_desencriptada = "Error al desencriptar"
            dato = {'id_baul': datos[0], 'Plataforma': datos[1], 'usuario': datos[2], 'clave': clave_desencriptada}
            return jsonify({'baul': dato, 'mensaje': 'Registro encontrado'})
        else:
            return jsonify({'mensaje': 'Registro no encontrado'})
    except Exception as ex:
        print("❌ Error en consulta_individual:", ex)
        return jsonify({'mensaje': 'Error en consulta_individual'})

# Registrar
@app.route("/registro/", methods=['POST'])
def registrar():
    try:
        conn = conectar()
        if conn is None:
            return jsonify({'mensaje': 'Error de conexión'})
        cur = conn.cursor()
        plataforma = request.json['plataforma']
        usuario = request.json['usuario']
        clave_plana = request.json['clave']
        clave_encriptada = f.encrypt(clave_plana.encode()).decode()
        cur.execute("INSERT INTO baul (plataforma, usuario, clave) VALUES (%s, %s, %s)", 
                    (plataforma, usuario, clave_encriptada))
        conn.commit()
        cur.close()
        conn.close()
        print(f"✅ Registro agregado: {plataforma}, {usuario}")
        return jsonify({'mensaje': 'Registro agregado'})
    except Exception as ex:
        print("❌ Error en registrar:", ex)
        return jsonify({'mensaje': 'Error en registrar'})

# Eliminar
@app.route("/eliminar/<codigo>", methods=['DELETE'])
def eliminar(codigo):
    try:
        conn = conectar()
        if conn is None:
            return jsonify({'mensaje': 'Error de conexión'})
        cur = conn.cursor()
        cur.execute("DELETE FROM baul WHERE id_baul=%s", (codigo,))
        conn.commit()
        cur.close()
        conn.close()
        print(f"🗑️ Registro eliminado: {codigo}")
        return jsonify({'mensaje': 'Eliminado'})
    except Exception as ex:
        print("❌ Error en eliminar:", ex)
        return jsonify({'mensaje': 'Error en eliminar'})

# Actualizar
@app.route("/actualizar/<codigo>", methods=['PUT'])
def actualizar(codigo):
    try:
        conn = conectar()
        if conn is None:
            return jsonify({'mensaje': 'Error de conexión'})
        cur = conn.cursor()
        plataforma = request.json['plataforma']
        usuario = request.json['usuario']
        clave_plana = request.json['clave']
        clave_encriptada = f.encrypt(clave_plana.encode()).decode()
        cur.execute("UPDATE baul SET plataforma=%s, usuario=%s, clave=%s WHERE id_baul=%s",
                    (plataforma, usuario, clave_encriptada, codigo))
        conn.commit()
        cur.close()
        conn.close()
        print(f"✏️ Registro actualizado id {codigo}")
        return jsonify({'mensaje': 'Registro Actualizado'})
    except Exception as ex:
        print("❌ Error en actualizar:", ex)
        return jsonify({'mensaje': 'Error en actualizar'})

# Iniciar
if __name__ == "__main__":
    app.run(debug=True)
