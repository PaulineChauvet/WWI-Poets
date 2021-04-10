from flask import render_template, request, url_for, jsonify
from urllib.parse import urlencode
from ..app import app
from ..constantes import POETES_PAR_PAGE, API_ROUTE
from ..modeles.donnees import Poet, Publication, Military_status


def Json_404():
    response = jsonify({"erreur": "Unable to perform the query"})
    response.status_code = 404
    return response

@app.route(API_ROUTE+"/poets/<poet_id>")
def api_poets_single(poet_id):
    try:
        query = Poet.query.get(poet_id)
        return jsonify(query.poete_to_json())
    except:
        return Json_404()


