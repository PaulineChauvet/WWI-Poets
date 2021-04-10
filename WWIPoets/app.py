from flask import Flask
#Importation de Flask depuis le module flask
from flask_sqlalchemy import SQLAlchemy
#Importation de l'ORM (Object Relational Mapper) SQLAlchemy depuis flask_sqlalchemy afin d'interagir avec des bases de données SQL.
from flask_login import LoginManager
#Importation de flask_login qui permet de gérer les sessions utilisateur.rice.s
import os
#Importation du module os qui permet d'interagir avec le système d'exploitation.
from .constantes import CONFIG
import sqlite3

#Stockage du chemin absolu du fichier qui contient le code.
chemin_actuel = os.path.dirname(os.path.abspath(__file__))
#Stockage du chemin vers les templates avec une jointure adaptée à l'OS
templates = os.path.join(chemin_actuel, "templates")
#Stockage du chemin vers les statics avec une jointure adaptée à l'OS
statics = os.path.join(chemin_actuel, "static")

# On initie l'extension
db = SQLAlchemy()

# On met en place la gestion d'utilisateur-rice-s
login = LoginManager()

#Instanciation de l'application
app = Flask(
    __name__,
    template_folder=templates,
    static_folder=statics
)

#Importation des routes depuis le dossier routes
from .routes import api, generic

def config_app(config_name="production"):
    """ Fonction de configuration de l'application """
    app.config.from_object(CONFIG[config_name])
    # Configuration de l'application en appelant la constante CONFIG qui définit s'il s'agit de l'app test ou de l'app de production.
    # Les configurations figurent dans le fichier constantes.py.
    # Set up extensions
    db.init_app(app)
    login.init_app(app)

    return app