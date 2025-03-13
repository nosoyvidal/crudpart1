from flask import Flask
from flask_cors import CORS
from flask import jsonify, request
import pymysql

app = Flask(__name__)
# Nos permite acceder desde una API externa
CORS(app)

# Función para conectarnos a la base de datos de MySQL
def conectar(host, user, vpass, vdb):
    conn = pymysql.connect(host='localhost', user='root', passwd='root', db='gestor_contra', charset='utf8mb4')
    return conn

# Ruta para consulta general del baúl de contraseñas
@app.route("/")
def consulta_general():
    try:
        conn = conectar('localhost', 'root', 'root', 'gestor_contra')
        cur = conn.cursor()
        cur.execute("SELECT * FROM baul")
        datos = cur.fetchall()
        data = []
        for row in datos:
            dato = {'id_baul': row[0], 'Plataforma': row[1], 'usuario': row[2], 'clave': row[3]}
            data.append(dato)
        cur.close()
        conn.close()
        return jsonify({'baul': data, 'mensaje': 'Baúl de contraseñas'})
    except Exception as ex:
        return jsonify({'mensaje': 'Error'})

@app.route("/consulta_individual/<codigo>", methods=['GET'])
def consulta_individual(codigo):
    try:
        conn = conectar('localhost', 'root', 'root', 'gestor_contra')
        cur = conn.cursor()
        cur.execute("SELECT * FROM baul where id_baul='{0}'".format(codigo))
        datos = cur.fetchone()
        cur.close()
        conn.close()
        
        if datos is not None:
            dato = {'id_baul': datos[0], 'Plataforma': datos[1], 'usuario': datos[2], 'clave': datos[3]}
            return jsonify({'baul': dato, 'mensaje': 'Registro encontrado'})
        else:
            return jsonify({'mensaje': 'Registro no encontrado'})
    except Exception as ex:
        return jsonify({'mensaje': 'Error'})

@app.route("/registro/", methods=['POST'])
def registrar():
    try:
        conn = conectar('localhost', 'root', 'root', 'gestor_contra')
        cur = conn.cursor()
        cur.execute("""INSERT INTO baul (plataforma, usuario, clave) VALUES ('{0}', '{1}', '{2}')""".format(
            request.json['plataforma'], request.json['usuario'], request.json['clave']
        ))
        conn.commit()  # Para confirmar la inserción de la información
        cur.close()
        conn.close()
        return jsonify({'mensaje': 'Registro agregado'})
    except Exception as ex:
        print(ex)
        return jsonify({'mensaje': 'Error'})

@app.route("/eliminar/<codigo>", methods=['DELETE'])
def eliminar(codigo):
    try:
        conn = conectar('localhost', 'root', 'root', 'gestor_contra')
        cur = conn.cursor()
        cur.execute("""DELETE FROM baul WHERE id_baul='{0}'""".format(codigo))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'mensaje': 'Eliminado'})
    except Exception as ex:
        print(ex)
        return jsonify({'mensaje': 'Error'})

@app.route("/actualizar/<codigo>", methods=['PUT'])
def actualizar(codigo):
    try:
        conn = conectar('localhost', 'root', 'root', 'gestor_contra')
        cur = conn.cursor()
        cur.execute("""UPDATE baul SET plataforma='{0}', usuario='{1}', clave='{2}' WHERE id_baul={3}""".format(
            request.json['plataforma'], request.json['usuario'], request.json['clave'], codigo
        ))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'mensaje': 'Registro Actualizado'})
    except Exception as ex:
        print(ex)
        return jsonify({'mensaje': 'Error'})

if __name__ == "__main__":
    app.run(debug=True)
