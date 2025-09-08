import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)
CORS(app)

# 🔹 Autenticación con Google Sheets usando variable de entorno
service_account_info = json.loads(os.environ["SERVICE_ACCOUNT_JSON"])
creds = Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
gc = gspread.authorize(creds)

# 🔹 Conectar con tu hoja de Google Sheets
SHEET_ID = os.environ["SHEET_ID"]
sheet = gc.open_by_key(SHEET_ID).sheet1

# =====================================================
# Rutas del CRUD
# =====================================================

# 📌 Obtener todos los productos
@app.route("/productos", methods=["GET"])
def get_productos():
    data = sheet.get_all_records()
    return jsonify(data), 200

# 📌 Agregar un nuevo producto
@app.route("/productos", methods=["POST"])
def add_producto():
    data = request.get_json()
    nombre = data.get("nombre")
    precio = data.get("precio")

    if not nombre or not precio:
        return jsonify({"error": "Faltan datos"}), 400

    sheet.append_row([nombre, precio])
    return jsonify({"message": "Producto agregado"}), 201

# 📌 Actualizar un producto por ID (fila en la hoja)
@app.route("/productos/<int:row_id>", methods=["PUT"])
def update_producto(row_id):
    data = request.get_json()
    nombre = data.get("nombre")
    precio = data.get("precio")

    if not nombre or not precio:
        return jsonify({"error": "Faltan datos"}), 400

    try:
        sheet.update_cell(row_id + 1, 1, nombre)  # columna 1 = nombre
        sheet.update_cell(row_id + 1, 2, precio)  # columna 2 = precio
        return jsonify({"message": "Producto actualizado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 📌 Eliminar un producto por ID (fila en la hoja)
@app.route("/productos/<int:row_id>", methods=["DELETE"])
def delete_producto(row_id):
    try:
        sheet.delete_rows(row_id + 1)
        return jsonify({"message": "Producto eliminado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =====================================================
# Inicio del servidor
# =====================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port, debug=True)
