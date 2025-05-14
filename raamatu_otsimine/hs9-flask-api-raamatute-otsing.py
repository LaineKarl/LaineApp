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

@app.route('/raamatu_otsing/<int:raamatu_id>', methods = ['POST'])
def raamatust_sone_otsimine(raamatu_id):

    try:

        input = json.loads(request.data)
        sone = input.get('sone')

        fail = blob_alla_laadimine(f"{raamatu_id}.txt")

        sone_arv = 0

        for line in fail.splitlines():
            sona = line.split()
            for i in sona:
                if i.strip().lower() == sone:
                    sone_arv += 1

        return {"raamatu_id": raamatu_id,
        "sone": sone,
        "leitud": sone_arv}, 200

    except Exception as e:
        return {}, 404

@app.route('/raamatu_otsing/', methods=['POST'])
def raamatute_sone_otsimine():
    try:
        input_data = json.loads(request.data)
        sone = input_data.get('sone')

        info = []

        for raamatu_id in blob_raamatute_nimekiri():
            fail = blob_alla_laadimine(raamatu_id)

            sone_arv = 0
            for line in fail.splitlines():
                sona = line.split()
                for i in sona:
                    if i.strip().lower() == sone:
                        sone_arv += 1

            info.append({
                "raamatu_id": raamatu_id.split(".")[0],
                "leitud": sone_arv
            })

        return {
            "sone": sone,
            "tulemused": info
        }, 200

    except Exception as e:
        print(e)
        # Võib lisada logimise vm siia
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

blob_connection_string = os.getenv('AZURE_BLOB_CONN_STRING')
blob_service_client = BlobServiceClient.from_connection_string(blob_connection_string)
blob_container_name = "laine"
blob_konteineri_loomine(blob_container_name)

# Peameetod, mis paneb käima Flask rakenduse
if __name__ == '__main__':
    # Aktiveerime DEBUG moodi, et näha lisainfot programmi töö kohta väljundis.
    app.run(debug=True)
