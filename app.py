import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv


load_dotenv()
SHEET_ID = os.getenv("SHEET_ID")
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")

if not SHEET_ID:
    raise ValueError(" Falta la variable SHEET_ID en el archivo .env")


scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1  


app = Flask(__name__)
CORS(app)

@app.route("/productos", methods=["GET"])
def get_productos():
    data = sheet.get_all_records()
    return jsonify(data)

@app.route("/productos", methods=["POST"])
def add_producto():
    nuevo = request.json
    sheet.append_row([nuevo["id"], nuevo["nombre"], nuevo["precio"]])
    return jsonify({"message": "Producto agregado correctamente"}), 201


@app.route("/productos/<id>", methods=["PUT"])
def update_producto(id):
    data = sheet.get_all_records()
    for idx, row in enumerate(data, start=2): 
        if str(row["id"]) == str(id):
            nuevo = request.json
            sheet.update(f"A{idx}:C{idx}", [[nuevo["id"], nuevo["nombre"], nuevo["precio"]]])
            return jsonify({"message": "Producto actualizado correctamente"})
    return jsonify({"error": "Producto no encontrado"}), 404


@app.route("/productos/<id>", methods=["DELETE"])
def delete_producto(id):
    data = sheet.get_all_records()
    for idx, row in enumerate(data, start=2):
        if str(row["id"]) == str(id):
            sheet.delete_rows(idx)
            return jsonify({"message": "Producto eliminado correctamente"})
    return jsonify({"error": "Producto no encontrado"}), 404


if __name__ == "__main__":
    app.run(port=3000, debug=True)
