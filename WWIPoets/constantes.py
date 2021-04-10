from warnings import warn

POETES_PAR_PAGE = 20
# Variable qui définit le nombre de résultats par page (utilisée pour les index d'individus et de production)
API_ROUTE = "/api"

SECRET_KEY = "JE SUIS UN SECRET !"
#Variable utilisée comme clé cryptographique
if SECRET_KEY == "JE SUIS UN SECRET !":
    warn("Le secret par défaut n'a pas été changé, vous devriez le faire", Warning)

"""
class _TEST:
    SECRET_KEY = SECRET_KEY
    # On configure la base de données
    SQLALCHEMY_DATABASE_URI = 'sqlite:///WWIPoets.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
"""

class _PRODUCTION:
    SECRET_KEY = SECRET_KEY
    # configuration du secret
    SQLALCHEMY_DATABASE_URI = 'sqlite:///WWIPoets.db'
    # configuration de la base de données production
    # Chemin relatif vers la base de données en mode production
    SQLALCHEMY_TRACK_MODIFICATIONS = False

CONFIG = {
    #"test": _TEST,
    "production": _PRODUCTION
    # Les deux classes sont regroupées dans un dictionnaire afin de pouvoir les appeler facilement. Nous désactivons le mode test pour travailler d'abord en production.
}