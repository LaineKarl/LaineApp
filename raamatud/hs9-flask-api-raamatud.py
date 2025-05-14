from azure.storage.blob import BlobServiceClient
from flask import Flask
from flask_cors import CORS
from flask import send_file
from flask import request
import os
import json
import requests

app = Flask(__name__)
cors = CORS(app, resources={r"/raamatud/*": {"origins": "*"}, r"/raamatu_otsing/*": {"origins": "*"}})


# Python meetodi definitsioon, mis implementeerib REST meetodi
# app.route(REST_ENDPOINT, methods) määrab ära milliseid REST/HTTP päringuid sellele meetodile edastatakse/suunatakse
# Siin näites on selleks: GET meetodi saatmine REST lõpp-punkti "/raamatud".
#      Ehk, Kui saadetakse GET päring aadressile "http://localhost:5000/raamatud", siis käivitatakse see meetod.
# Päringu vatusena saadetakse tagasi misiganes see meetod tagastab return operatsiooni tulemusena.
@app.route('/raamatud/', methods=['GET'])
def raamatu_nimekiri():
    try:
        uued_raamatud = {"raamatud": []}
        raamatud = blob_raamatute_nimekiri()
        for i in raamatud:
            if i.endswith(".txt"):
                uued_raamatud["raamatud"].append(i.split(".")[0])

        return uued_raamatud, 200

    except Exception as e:
        return {}, 404


@app.route('/raamatud/<book_id>', methods=['GET'])
def raamatu_allalaadimine(book_id):
    try:

        if not book_id.isnumeric():
            return {}, 404

        raamatu_sisu = blob_alla_laadimine(f"{book_id}.txt")

        return raamatu_sisu, 200, {'Content-Type': 'text/plain; charset=utf-8'}

    except Exception as e:
        return {}, 404


@app.route('/raamatud/<book_id>', methods = ['DELETE'])
def raamatu_kustutamine(book_id):

    try:

        if not book_id.isnumeric():
            return {}, 404

        blob_kustutamine(f"{book_id}.txt")

        return {}, 204

    except Exception as e:
        return {}, 404


@app.route('/raamatud/', methods = ['POST'])
def raamatu_lisamine():

    try:
        input = json.loads(request.data)
        book_id = input.get('raamatu_id')
        response = requests.get(f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt", verify=False)
        raamat_fail = f"{book_id}.txt"

        blob_ules_laadimine_sisu(raamat_fail,response.text)

        return {"tulemus": "Raamatu loomine õnnestus",
                "raamatu_id": book_id }, 201

    except Exception as e:
        return {}, 404


def blob_konteineri_loomine(konteineri_nimi):
    container_client = blob_service_client.get_container_client(container=konteineri_nimi)
    if not container_client.exists():
        blob_service_client.create_container(konteineri_nimi)
        print("Loodud")
    else:
        print("On olemas")

def blob_raamatute_nimekiri():
    container_client = blob_service_client.get_container_client(container=blob_container_name)
    lst = []
    for i in container_client.list_blobs():
        lst.append(i.name)
    return lst

def blob_alla_laadimine(faili_nimi):
    blob_client = blob_service_client.get_blob_client(container=blob_container_name, blob=faili_nimi)
    sisu = blob_client.download_blob().content_as_text()
    return sisu

def blob_ules_laadimine_sisu(faili_nimi, sisu):
    blob_client = blob_service_client.get_blob_client(container=blob_container_name, blob=faili_nimi)
    blob_client.upload_blob(sisu, overwrite=True)


def blob_kustutamine(faili_nimi):
    blob_client = blob_service_client.get_blob_client(container=blob_container_name, blob=faili_nimi)
    try:
        blob_client.delete_blob()
    except Exception as e:
        print(f"Viga: {e}")

blob_connection_string = os.getenv('APPSETTING_AzureWebJobsStorage')
blob_service_client = BlobServiceClient.from_connection_string(blob_connection_string)
blob_container_name = os.getenv('APPSETTING_blob_container_name')
blob_konteineri_loomine(blob_container_name)

# Peameetod, mis paneb käima Flask rakenduse
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 80))

    # Aktiveerime DEBUG moodi, et näha lisainfot programmi töö kohta väljundis.
    app.run(host="0.0.0.0", debug=True, port=port)
