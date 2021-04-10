from flask import render_template, url_for, request, flash, redirect
#Importation de render_template (afin de joindre les routes aux templates), url_for (afin de construire des url vers les fonctions et les pages html),
#request (import de types d'objets via des requêtes HTTP), flash (permet l'envoi de messages automatiques) et redirect (renvoi vers l'url d'une autre route) depuis le module flask.
from sqlalchemy import or_
#Importation depuis SQLAlchemy de l'opérateur 'or' pour faire du requêtage multi-tables.
from ..app import app, db, login
#Importation de app, db et login pour gérer les utilisateurs
from ..modeles.donnees import Poet, Publication, Military_status
#Importation des classes Poet, Publication et Military_status, déclarées dans le fichier donnees.py
from ..modeles.utilisateurs import User
#Importation de la classe User, déclarée dans le fichier utilisateurs.py
from ..constantes import POETES_PAR_PAGE
#Importation de la variable POETES_PAR_PAGE, utilisée dans la fonction de recherche
from flask_login import login_user, current_user, logout_user, login_required
#Importation de current_user (utilisateur courant), login_user (connexion), logout_user (déconnexion) et login_required (identification obligatoire) pour gérer les sessions utilisateurs.

# PAGES GENERALES #

@app.route("/")
def accueil():
    """ Route permettant l'affichage d'une page accueil
    :returns: template 'accueil.html'
    :rtype: template
    """
    # Permet l'affichage des vingt derniers poètes enregistrés dans la base.
    #render_template a comme premier argument le chemin du template souhaité puis des arguments nommés, réutilisés comme variables à l'intérieur des templates.
    poets = Poet.query.order_by(Poet.poet_id.desc()).limit(20).all()
    return render_template("pages/accueil.html", nom="Poets of World War I", poetes=poets)

@app.route("/presentation")
def presentation():
    """
    Route permettant l'affichage des informations de présentation de l'application.
    :returns: template 'presentation_api.html'
    :rtype:template
    """
    return render_template("pages/presentation_api.html")

# PAGES DE CONSULTATION DE LA BASE #

@app.route("/recherche")
def recherche():
    """ Route permettant la recherche plein-texte.
    :returns: template 'recherche.html'
    :rtype: template
    """
    # On préfèrera l'utilisation de .get() ici qui permet d'éviter un if long (if "clef" in dictionnaire and dictonnaire["clef"])
    motclef = request.args.get("keyword", None)
    page = request.args.get("page", 1)

    if isinstance(page, str) and page.isdigit():
        page = int(page)
    else:
        page = 1
    # Si le numéro de la page est une chaîne de caractères composée uniquement de chiffres, on la recaste en integer
    # Sinon, le numéro de la page est égal à 1.

    # On crée une liste vide de résultat (qui restera vide par défaut si on n'a pas de mot clé)
    resultats = []

    # On fait de même pour le titre de la page.
    # Si un mot-clé est entré dans la barre de recherche, requête sur les tables Poet, Publication et Military_status de la base de données pour chercher des correspondances.
    #Le résultat est stocké dans la liste résultats = []
    titre = "Recherche"
    if motclef:
        resultats = Poet.query.filter(
            or_(Poet.poet_name.like("%{}%".format(motclef)),
            Poet.poet_firstname.like("%{}%".format(motclef)),
            Poet.poet_country.like("%{}%".format(motclef)),
            Poet.poet_birthplace.like("%{}%".format(motclef)),
            Poet.poet_deathplace.like("%{}%".format(motclef)),
            Poet.poet_birthdate.like("%{}%".format(motclef)),
            Poet.poet_deathdate.like("%{}%".format(motclef)),
            Poet.link_publication.any((Publication.publication_titre).like("%{}%".format(motclef))),
            Poet.link_publication.any((Publication.publication_genre_litteraire).like("%{}%".format(motclef))),
            Poet.link_military_status.any((Military_status.military_status_statut).like("%{}%".format(motclef))),
            Poet.link_military_status.any((Military_status.military_status_grade).like("%{}%".format(motclef))),
            Poet.link_military_status.any((Military_status.military_status_lieu_recrutement).like("%{}%".format(motclef))),
            Poet.link_military_status.any((Military_status.military_status_registre_matricule).like("%{}%".format(motclef)))
            )
            #Requête à la fois sur les tables Poet, Military_status et Publication grâce à la commande any.
          ).paginate(page=page, per_page=POETES_PAR_PAGE)
        #Pagination réalisée avec la méthode .paginate
        titre = "Résultat pour la recherche `" + motclef + " "
        return render_template("pages/recherche.html", resultats=resultats, titre=titre, keyword=motclef)


@app.route("/index_individus")
def index_individus():
    """ Route qui affiche la liste ordonnée alphabétiquement (par le nom de famille) des individus de la base.
    :returns: template 'index_individus.html'
    :rtype: template
    """
    titre = "Index des individus"
    # vérification que la base de données n'est pas vide :
    personnes = Poet.query.all()

    if len(personnes) == 0:
        return render_template("pages/index_individus.html", personnes=personnes, titre=titre)
    else:
        page = request.args.get("page", 1)
        if isinstance(page, str) and page.isdigit():
            page = int(page)
        else:
            page = 1

        # creation de la pagination avec la methode .paginate qui remplace le .all dans la requête sur la base
        personnes = Poet.query.order_by(Poet.poet_name).paginate(page=page)
        return render_template("pages/index_individus.html", personnes=personnes, titre=titre)

@app.route("/index_publications")
def index_publications():
    """
    Route qui affiche la liste ordonnée alphabétiquement (par le titre) des références bibliographiques contenues dans la base.
    :returns: template 'index_publications.html'
    :rtype: template
    """
    titre="Oeuvres poétiques de guerre"
    #Vérification que la base de données n'est pas vide.
    oeuvres=Publication.query.all()

    if len(oeuvres) == 0:
        return render_template("pages/index_publications.html", oeuvres=oeuvres, titre=titre)
    else:
        page = request.args.get("page", 1)
        if isinstance(page, str) and page.isdigit():
            page=int(page)
        else:
            page=1
        #Création de la pagination avec la méthode .paginate.
        oeuvres=Publication.query.order_by(Publication.publication_titre).paginate(page=page)
        return render_template("pages/index_publications.html", oeuvres=oeuvres, titre=titre)

@app.route("/poets/<int:poet_id>")
def notice(poet_id):
    """ Route permettant l'affichage d'une notice individuelle de poète (informations biographiques élémentaires + description en rapport avec la Première Guerre mondiale)

    :param poet_id: Identifiant numérique du/de la poétesse qui correspond à la valeur de la clé primaire dans la table Poet dans la BDD.
    :type poet_id: int
    :returns: template 'notice.html'
    :rtype: template
    """

    unique_poete = Poet.query.get(poet_id)
    #Si la requête par l'identifiant numérique ne trouve pas de correspondance, message d'information renvoyé à l'utilisateur sur l'absence de l'individu dans la base.
    if not unique_poete:
        flash("L'individu recherché n'est pas enregistré dans la base")
        return redirect("/index_individus")
    #Si l'individu recherché ne figure pas dans la base, renvoi sur l'index des individus.
    else:
        poetPublication = unique_poete.link_publication
        poetStatus=unique_poete.link_military_status
        return render_template("pages/notice.html", nom="Poets of World War I", poete=unique_poete, poetPublication=poetPublication, poetStatus=poetStatus)

# PAGES RELATIVES AU CRUD DES DONNEES #

#login_required précédé d'un décorateur permet d'imposer l'identification d'un utilisateur pour que ce dernier puisse créer une notice.
@app.route("/creation_poet", methods=["GET", "POST"])
@login_required
def creation_poet():
    """
    Route permettant à l'utilisateur de créer une notice individuelle de poète
    :returns: template 'creation_statut.html' en cas de création réussie, ou 'creation_poet.html' en cas d'échec.
    :rtype: template
    """
    poete = Poet.query.all()
    if request.method=="POST":
        # Si le formulaire est envoyé, on passe en méthode POST. Puis on applique la fonction create_poet définie dans le fichier donnees.py
        status, data = Poet.create_poet(
        nom=request.form.get("nom", None),
        prenom=request.form.get("prenom", None),
        nationalite=request.form.get("nationalite", None),
        date_naissance=request.form.get("date_naissance", None),
        date_deces=request.form.get("date_deces", None),
        lieu_naissance=request.form.get("lieu_naissance", None),
        lieu_deces=request.form.get("lieu_deces", None),
        description=request.form.get("description", None),
        login_wiki=request.form.get("login_wiki", None)
        )

        if status is True:
            flash("Création d'une nouvelle notice réussie!", "success")
            return redirect("/creation_statut")
        else:
            flash("La création d'une nouvelle notice a échoué pour les raisons suivantes:"+", ".join(data), "danger")
            return render_template("pages/creation_poet.html")
    else:
        return render_template("pages/creation_poet.html")

@app.route("/modification_poet/<int:poet_id>", methods=["POST", "GET"])
@login_required
def modification_poet(poet_id):
    """
    Route permettant de modifier un formulaire avec les données biographiques et descriptives d'un(e) poète(sse).
    :param poet_id: identifiant numérique du/de la poète(sse) récupéré(e) depuis la page notice
    :type poet_id: int
    :returns: template 'modification_poet.html'
    :rtype: template
    """

    #Si on est en méthode GET, renvoi sur la page html des éléments de l'objet poet correspondant à l'identifiant de la route.
    if request.method=="GET":
        poete_initial=Poet.query.get(poet_id)
        return render_template("pages/modification_poet.html", poete_initial=poete_initial)
    #Récupération des données du formulaire modifié grâce à la fonction modif_poet définie dans le fichier donnees.py.
    else:
        status, poeteModifie=Poet.modif_poet(
            poet_id=poet_id,
            nom=request.form.get("nom", None),
            prenom=request.form.get("prenom", None),
            date_naissance=request.form.get("date_naissance", None),
            date_deces=request.form.get("date_deces", None),
            nationalite=request.form.get("nationalite", None),
            lieu_naissance=request.form.get("lieu_naissance", None),
            lieu_deces=request.form.get("lieu_deces", None),
            description=request.form.get("description", None),
            login_wiki=request.form.get("login_wiki", None)
        )
        if status is True:
            flash("Modification réussie !", "success")
            poete_initial = Poet.query.get(poet_id)
            return render_template ("pages/modification_poet.html", poete_initial=poete_initial)

        else:
            flash("Les erreurs suivantes ont été rencontrées : " + ",".join(poeteModifie), "danger")
            poete_initial = Poet.query.get(poet_id)
            return render_template("pages/modification_poet.html", poete_initial=poete_initial)

@app.route("/suppression_poet/<int:poet_id>", methods=["GET", "POST"])
@login_required
def suppression_poet(poet_id):
    """
    Route pour gérer la suppression d'un poète (ainsi que son ESM et son/ses publication(s) grâce à la configuration cascade).
    :param poet_id: identifiant numérique du/de la poète(sse)
    :type poet_id: int
    :returns: template 'index_individus.html' en cas de réussite, sinon redirection sur le template de la notice correspondante.
    """
    poete=Poet.query.get(poet_id)

    status=Poet.delete_poet(poet_id=poet_id)

    if status is True:
        flash("Suppression réussie!", "success")
        return redirect("/index_individus")

    else:
        flash("Échec de la suppression", "danger")
        return redirect("/poets/" + str(poete.poet_id))

@app.route("/creation_statut", methods=["GET", "POST"])
@login_required
def creation_statut():
    """
    Route permettant à l'utilisateur de créer un état de situation militaire (ESM) pour le poète qu'il vient d'enregistrer.
    :returns: template 'creation_publication.html' en cas de réussite, renvoi sur le template 'creation_statut.html' en cas d'échec.
    :rtype: template
    """

    #La création d'un nouvel ESM n'étant possible que dans le cadre d'une création de notice individuelle de poète, on récupère l'id du dernier poète enregistré dans la base (celui qui vient d'être créé) pour le relier à l'ESM.
    last_id=Poet.query.order_by(Poet.poet_id.desc()).first()
    last_id_poet=last_id.poet_id
    esm = Military_status.query.all()
    #On passe en méthode POST et on applique la fonction create_military_status définie dans le fichier donnees.py
    if request.method=="POST":
        status, data = Military_status.create_military_status(
        statut=request.form.get("statut", None),
        lieu_recrutement=request.form.get("lieu_recrutement", None),
        registre_matricule=request.form.get("registre_matricule", None),
        poet_id = last_id_poet,
        grade=request.form.get("grade", None),
        login_wiki_esm=request.form.get("login_wiki_esm", None)
        )

        if status is True:
            flash("Création d'une nouvelle notice réussie!", "success")
            return redirect("/creation_publication")
        else:
            flash("La création d'une nouvelle notice a échoué pour les raisons suivantes:"+", ".join(data), "danger")
            return render_template("pages/creation_statut.html")
    else:
        return render_template("pages/creation_statut.html")

@app.route("/modification_statut/<int:military_status_id>", methods=["POST", "GET"])
@login_required
def modification_statut(military_status_id):
    """
    Route permettant de modifier un formulaire avec les données relatives à l'état de situation militaire (ESM) d'un(e) poète(sse).
    :param military_status_id: identifiant numérique de l'ESM proposé à la modification.
    :type military_status_id: int
    :returns: template 'index_individus.html' en cas de réussite,'modification_statut' en cas d'échec.
    :rtype: template
    """
    statut=Military_status.query.get(military_status_id)

    if request.method=="GET":

        return render_template("pages/modification_statut.html", statut=statut)


    else:
        #On applique la fonction modif_statut définie dans le fichier donnees.py
        status, statutModifie = Military_status.modif_statut(
            military_status_id=military_status_id,
            statut=request.form.get("statut", None),
            lieu_recrutement=request.form.get("lieu_recrutement", None),
            registre_matricule=request.form.get("registre_matricule", None),
            grade=request.form.get("grade", None),
            login_wiki_esm=request.form.get("login_wiki_esm", None)
        )

        if status is True:
            flash("Modification réussie!", "success")
            return redirect("/index_individus")

        else:
            flash("Les erreurs suivantes ont été rencontrées : " + ",".join(statutModifie), "danger")
            return render_template("pages/modification_statut.html", statut=statut)

@app.route("/creation_publication", methods=["GET", "POST"])
@login_required
def creation_publication():
    """
    Route permettant à l'utilisateur de créer une référence bibliographique inhérente à la production du/de la poète(sse) qu'il vient d'enregistrer.
    :returns: template 'creation_publication.html'
    :rtype: template
    """

    # La création d'une nouvelle référence bibliographique n'étant possible que dans le cadre d'une création de notice individuelle de poète, on récupère l'id du dernier poète enregistré dans la base (celui qui vient d'être créé) pour le relier à la référence bibliographique.
    last_id=Poet.query.order_by(Poet.poet_id.desc()).first()
    last_id_poet=last_id.poet_id
    publi = Publication.query.all()

    #On passe en méthode POST. Application de la fonction create_publication définie dans le fichier donnees.py
    if request.method=="POST":
        status, data = Publication.create_publication(
        titre=request.form.get("titre", None),
        date=request.form.get("date", None),
        genre_litteraire=request.form.get("genre_litteraire", None),
        poet_id = last_id_poet,
        login_wiki_pub=request.form.get("login_wiki_pub", None)
        )

        if status is True:
            flash("Création d'une nouvelle notice réussie!", "success")
            return redirect("/creation_publication")
        else:
            flash("La création d'une nouvelle notice a échoué pour les raisons suivantes:"+", ".join(data), "danger")
            return render_template("pages/creation_publication.html")
    else:
        return render_template("pages/creation_publication.html")

@app.route("/modification_publication/<int:publication_id>", methods=["POST", "GET"])
@login_required
def modification_publication(publication_id):
    """
    Route permettant de modifier un formulaire avec les données relatives à une référence bibliographique.
    :param publication_id: identifiant numérique de la référence bibliographique proposée à la modification.
    :type publication_id: int
    :returns: template 'index_individus.html' en cas de réussite,'modification_statut' en cas d'échec.
    :rtype: template
    """
    publication=Publication.query.get(publication_id)

    if request.method=="GET":

        return render_template("pages/modification_publication.html", publication=publication)


    else:
        poeteInitial=request.form.get("poetpub", None)
        #Application de la fonction modif_pub définie dans le fichier donnees.py
        status, pubModifie = Publication.modif_pub(
            publication_id=publication_id,
            publication_poet_id=poeteInitial,
            titre=request.form.get("titre", None),
            date=request.form.get("date", None),
            genre_litteraire=request.form.get("genre_litteraire", None),
            login_wiki_pub=request.form.get("login_wiki_pub", None)
        )

        if status is True:
            flash("Modification réussie!", "success")
            #En cas de modification réussie, redirection vers l'index des individus.
            return redirect("/index_individus")
        else:
            flash("Les erreurs suivantes ont été rencontrées : " + ",".join(pubModifie), "danger")
            return render_template("pages/modification_publication.html", publication=publication)

#PAGES RELATIVES À LA GESTION DES UTILISATEUR.RICE.S #

@app.route("/register", methods=["GET", "POST"])
def inscription():
    """
    Route gérant les inscriptions des utilisateur.rice.s
    :returns: redirection ou template 'inscription.html'
    :rtype: template
    """
    # Si on est en POST, cela veut dire que le formulaire a été envoyé.
    if request.method == "POST":
        statut, donnees = User.creer(
            login=request.form.get("login", None),
            email=request.form.get("email", None),
            nom=request.form.get("nom", None),
            motdepasse=request.form.get("motdepasse", None)
        )
        if statut is True:
            flash("Enregistrement effectué. Identifiez-vous maintenant", "success")
            return redirect("/")
        else:
            flash("Les erreurs suivantes ont été rencontrées : " + ",".join(donnees), "error")
            return render_template("pages/inscription.html")
    else:
        return render_template("pages/inscription.html")


@app.route("/connexion", methods=["POST", "GET"])
def connexion():
    """
    Route gérant les connexions des utilisateur.rice.s
    :returns: redirection ou template 'connexion.html'
    :rtype: template
    """
    if current_user.is_authenticated is True:
        flash("Vous êtes déjà connecté-e", "info")
        return redirect("/")
    # Si on est en POST, cela veut dire que le formulaire a été envoyé.
    if request.method == "POST":
        utilisateur = User.identification(
            login=request.form.get("login", None),
            motdepasse=request.form.get("motdepasse", None)
        )
        if utilisateur:
            flash("Connexion effectuée", "success")
            login_user(utilisateur)
            return redirect("/")
        else:
            flash("Les identifiants n'ont pas été reconnus", "error")

    return render_template("pages/connexion.html")
login.login_view = 'connexion'


@app.route("/deconnexion", methods=["POST", "GET"])
def deconnexion():
    """
    Route permettant de gérer les déconnexions.
    :returns: redirection vers l'accueil
    :rtype: template
    """
    if current_user.is_authenticated is True:
        logout_user()
    flash("Vous êtes déconnecté-e", "info")
    return redirect("/")