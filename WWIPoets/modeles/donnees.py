from flask import url_for
#Importation de url_for pour construire des URL vers les fonctions et les pages html depuis flask.
import datetime
#Importation du module datetime pour accéder aux données de date et horaires dans le fuseau adéquat.
from flask_login import current_user
#Importation de la variable current_user depuis flask_login
from ..app import db
#Importation de la base de données


class Poet(db.Model):
    __tablename__ = "Poet"
    poet_id = db.Column(db.Integer, unique=True, nullable=False, autoincrement=True, primary_key=True)
    poet_name = db.Column(db.Text, nullable=False)
    poet_firstname = db.Column(db.Text)
    poet_birthdate = db.Column(db.Text)
    poet_deathdate = db.Column(db.Text)
    poet_country = db.Column(db.Text)
    poet_birthplace = db.Column(db.Text)
    poet_deathplace = db.Column(db.Text)
    poet_description = db.Column(db.Text)
    poet_external_login=db.Column(db.Text, nullable=False)
    #Jointures entre les tables Authorship_poet et Poet; entre les tables Publication et Poet; ainsi qu'entre les tables Military_status et Poet.
    authorships_poet = db.relationship("Authorship_poet", back_populates="poet", cascade="all, delete")
    link_publication = db.relationship("Publication", primaryjoin="Poet.poet_id==Publication.publication_poet_id", cascade="all, delete")
    link_military_status = db.relationship("Military_status", primaryjoin="Poet.poet_id==Military_status.military_status_poet_id", cascade="all, delete")
    #Le comportement en cascade, configuré en 'all, delete' au niveau du côté one de la relation one to many permet d'appliquer l'action exercée sur l'objet parent à ses enfants automatiquement. 'Delete' signifie que l'objet enfant doit également être supprimé lorsque son parent n'existe plus.

    def poete_to_json(self):
        """
        Fonction qui permet l'export en format Json des informations principales de la notice d'un poète.
        rtype: dictionnaire
        """
        return {
            "id": self.poet_id,
            "attributes": {
                "name": self.poet_name,
                "firstname":self.poet_firstname,
                "birthdate":self.poet_birthdate,
                "birthdeath":self.poet_deathdate,
                "country":self.poet_country,
                "birthplace":self.poet_birthplace,
                "deathplace":self.poet_deathplace,
                "description":self.poet_description
            },
            "links": {
                "json": url_for("api_poets_single", poet_id=self.poet_id, _external=True)
            },
            "publication": [
                    lien.publication_to_json()
                    for lien in self.link_publication
                ],
            "statut_militaire": [
                    lien.status_to_json()
                    for lien in self.link_military_status
                ]
            }


    @staticmethod
    def create_poet(nom, prenom, nationalite, date_naissance, date_deces, lieu_naissance, lieu_deces, description, login_wiki):
        """
        Fonction permettant la création d'un(e) nouveau/nouvelle poète(sse) dans la base de données.
        :param nom : nom de l'individu
        :param prenom : prénom de l'individu
        :param nationalite : nationalité (d'origine ou par naturalisation) de l'individu
        :param date_naissance : date de naissance de l'individu
        :param date_deces : date de déces de l'individu
        :param lieu_naissance: lieu de naissance de l'individu
        :param lieu_deces: lieu de décès de l'individu
        :param description : description de l'individu en rapport avec la Première Guerre mondiale
        :param login_wiki : identifiant externe créé par l'utilisateur lors d'une création de notice
        :type nom, prenom, nationalite, date_naissance, date_deces, lieu_naissance, lieu_deces, description, login_wiki: string
        returns : Tuple (booléen, liste/objet).
        S'il y a une erreur, la fonction renvoie False suivi d'une liste d'erreurs.
        """

        errors = []
        #Création d'une liste vide pour y stocker les erreurs.
        if not (nom or prenom):
            errors.append("La mention du nom et du prénom sont obligatoires")
        if not nationalite:
            errors.append("La mention de la nationalité est obligatoire")
        if not description:
            errors.append("La mention de la description est obligatoire")
        if not (date_naissance or date_deces):
            errors.append("La mention d'au moins une date (de naissance ou de décès) est obligatoire")
        if not (lieu_naissance or lieu_deces):
            errors.append("La mention d'au moins un lieu (de naissance ou de naissance) est obligatoire")
        if not login_wiki:
            errors.append("La création d'un identifiant composé au maximum de 10 lettres et/ou chiffres est obligatoire")
        #Vérifie que les champs 'nom', 'prenom', 'nationalite', 'description', 'date_naissance', 'date_deces', 'lieu_naissance', 'lieu_deces' et login_wiki soient remplis.
        #Si au moins un champ reste vide, retourne une erreur.
        if len(errors) > 0:
            return False, errors

        # Vérifie que la taille des caractères insérés ne dépasse pas 12 afin que la date puisse avoir un format lisible.
        if len(date_naissance) > 12 or len(date_deces) > 12:
            errors.append("La taille des caractères des dates a été dépassée")
        #Sinon, retourne une erreur.
        if len(errors) > 0:
            return False, errors

        # Vérifie que la taille des caractères insérés (login_wiki) ne dépasse pas la limite de 10.
        if len(login_wiki) > 10:
            errors.append("La taille des caractères du champ Identifiant de notice a été dépassée")
        if len(errors) > 0:
            return False, errors

        # Vérifie si le/la poète(sse) existe déjà dans la base de données.
        poete = Poet.query.filter(db.and_(Poet.poet_name == nom, Poet.poet_firstname == prenom)).count()
        if poete > 0:
            errors.append("La personne est déjà inscrite dans la base de données")

        #Vérifie si le login wiki existe déjà
        poete = Poet.query.filter(Poet.poet_external_login==login_wiki).count()

        if poete > 0:
            errors.append("Cet identifiant est déjà utilisé")

        if len(errors) > 0:
            return False, errors
        # Sinon, on crée une nouvelle entrée dans la table Poet
        created_poet = Poet(
            poet_name=nom,
            poet_firstname=prenom,
            poet_country=nationalite,
            poet_birthdate=date_naissance,
            poet_deathdate=date_deces,
            poet_birthplace=lieu_naissance,
            poet_deathplace=lieu_deces,
            poet_description=description,
            poet_external_login=login_wiki
        )
        try:
            #Ajout de cette nouvelle entrée dans la base de données.
            db.session.add(created_poet)
            db.session.commit()

            #Création d'un enregistrement dans authorship_poet avec utilisation de la fonction authorship_event.
            creation = Poet.query.filter(Poet.poet_external_login==login_wiki).one()
            authorship_poet=Authorship_poet.authorship_event(
                updated=creation)
            #Renvoi des informations d'enregistrement vers le contributeur
            return True, created_poet

        except Exception as error_creation:
            return False, [str(error_creation)]

    @staticmethod
    def modif_poet(poet_id, nom, prenom, nationalite, date_naissance, date_deces, lieu_naissance, lieu_deces, description, login_wiki):
        """
        Fonction permettant la modification de notice d'un(e) poète(sse) dans la base de données.
        :param poet_id: identifiant numérique de l'individu
        :type poet_id: int
        :param nom : nom de l'individu
        :param prenom : prénom de l'individu
        :param nationalite : nationalité (d'origine ou par naturalisation) de l'individu
        :param date_naissance : date de naissance de l'individu
        :param date_deces : date de déces de l'individu
        :param lieu_naissance: lieu de naissance de l'individu
        :param lieu_deces: lieu de décès de l'individu
        :param description : description de l'individu en rapport avec la Première Guerre mondiale
        :param login_wiki : identifiant externe créé par l'utilisateur lors d'une création de notice
        :type nom, prenom, nationalite, date_naissance, date_deces, lieu_naissance, lieu_deces, description, login_wiki: string
        returns : Tuple (booléen, liste/objet).
        S'il y a une erreur, la fonction renvoie False suivi d'une liste d'erreurs.
        Sinon, elle renvoie True, suivi de l'objet mis à jour.
        """
        errors=[]
        # Création d'une liste vide pour y stocker les erreurs.
        if not (nom or prenom):
            errors.append("La mention du nom et du prénom est obligatoire")
        if not nationalite:
            errors.append("La mention de la nationalité est obligatoire")
        if not description:
            errors.append("La mention de la description est obligatoire")
        if not (date_naissance or date_deces):
            errors.append("La mention d'au moins une date (de naissance ou de décès) est obligatoire")
        if not (lieu_naissance or lieu_deces):
            errors.append("La mention d'au moins un lieu (de naissance ou de naissance) est obligatoire")
        if not login_wiki:
            errors.append("La création d'un identifiant composé au maximum de 10 lettres et/ou chiffres est obligatoire")
        if len(errors) > 0:
            return False, errors
        #Récupération d'un(e) poète(sse) dans la base.
        poete = Poet.query.get(poet_id)

        #On s'assure que l'utilisateur modifie au moins un champ. Sinon, retourne une erreur.
        if poete.poet_name == nom \
                and poete.poet_firstname == prenom \
                and poete.poet_birthdate == date_naissance \
                and poete.poet_deathdate == date_deces \
                and poete.poet_birthplace == lieu_naissance \
                and poete.poet_deathplace == lieu_deces \
                and poete.poet_country == nationalite \
                and poete.poet_description == description \
                and poete.poet_external_login == login_wiki:
            errors.append("Aucune modification n'a été réalisée")

        if len(errors) > 0:
            return False, errors

        if len(date_naissance) > 12 or len(date_deces) > 12:
            errors.append("La date ne doit pas dépasser 12 caractères")
        if len(errors) > 0:
            return False, errors

        # Vérifie que la taille des caractères insérés (login_wiki) par l'utilisateur ne dépasse pas la limite de 10.
        if len(login_wiki) > 10:
            errors.append("L'identifiant ne doit pas dépasser 10 caractères'")
        if len(errors) > 0:
            return False, errors
        #Mise à jour des données de la notice.
        else:
            poete.poet_name = nom
            poete.poet_firstname = prenom
            poete.poet_birthdate = date_naissance
            poete.poet_deathdate = date_deces
            poete.poet_birthplace = lieu_naissance
            poete.poet_deathplace = lieu_deces
            poete.poet_country = nationalite
            poete.poet_description = description
            poete.poet_external_login = login_wiki
        #Ajout de la mise à jour dans la base de données.
        try:
            db.session.add(poete)
            db.session.commit()
        #Création d'un enregistrement dans Authorship_poet.
            authorship_poet=Authorship_poet.authorship_event(
                updated=Poet.query.get(poet_id)
            )

            return True, poete

        except Exception as error_modif_poet:
            return False, [str(error_modif_poet)]

    @staticmethod
    def delete_poet(poet_id):
        """
        Fonction qui supprime la notice d'un(e) poète(sse)
        :param poet_id: identifiant numérique de l'individu
        :type poet_id: integer
        :returns: True si la suppression a réussi, sinon False.
        :rtype: booléen

        """
        poete = Poet.query.get(poet_id)
        #On enregistre cette suppression dans la base de données. Suppression des enregistrements liés dans Authorship_poet.
        try:
            Authorship_poet.delete_logs(
                id_poet=poet_id
            )
            db.session.delete(poete)
            db.session.commit()
            return True
        except Exception as failed:
            print(failed)
            return False


class Publication(db.Model):
    __tablename__ = "Publication"
    publication_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    publication_titre = db.Column(db.Text)
    publication_date = db.Column(db.Text)
    publication_genre_litteraire = db.Column(db.Text)
    publication_poet_id = db.Column(db.Integer, db.ForeignKey("Poet.poet_id"))
    publication_external_login=db.Column(db.Text)
    #Jointures entre les tables Poet et Publication; ainsi qu'entre les tables Poet et Authorship_publication.
    poetpub = db.relationship("Poet", foreign_keys=[publication_poet_id])
    authorships_pub = db.relationship("Authorship_publication", back_populates="pub", cascade="all, delete")

    def publication_to_json(self):
        """
        Fonction qui permet l'export en Json des informations relatives aux publications d'un(e) poète(sse).
        rtype: dictionnaire.
        """
        return {
            "id": self.publication_id,
            "attributes": {
                "title": self.publication_titre,
                "date": self.publication_date,
                "category": self.publication_genre_litteraire
            }
        }

    @staticmethod
    def create_publication(titre, date, genre_litteraire, poet_id, login_wiki_pub):
        """
        Fonction permettant la création d'une nouvelle référence bibliographique lors de la création d'une notice de poète par un utilisateur identifié.
        :param titre : titre de la publication ou de la production
        :param date : date de la publication originale ou de la production
        :param genre_litteraire : genre littéraire de la publication ou de la production
        :param poet_id : identifiant numérique de l'auteur
        :type poet_id : integer
        :param login_wiki_pub : identifiant externe créé par l'utilisateur lors d'une création de notice
        :type titre, date, genre_litteraire, login_wiki_pub: string
        returns : Tuple (booléen, liste/objet).
        S'il y a une erreur, la fonction renvoie False suivi d'une liste d'erreurs.
        """

        errors = []
        # Création d'une liste vide pour y stocker les erreurs.
        if not titre:
            errors.append("La mention du titre est obligatoire")
        if not date:
            errors.append("La mention de la date est obligatoire")
        if len(errors) > 0:
            return False, errors

        publication_log = Publication.query.filter(
            Publication.publication_external_login == login_wiki_pub).count()
        #On vérifie que l'identifiant externe n'est pas déjà utilisé.
        if publication_log > 0:
            errors.append("Cet identifiant est déjà utilisé")

        if len(errors) > 0:
            return False, errors

        created_publication = Publication(
            publication_titre=titre,
            publication_date=date,
            publication_genre_litteraire=genre_litteraire,
            publication_poet_id=poet_id,
            publication_external_login=login_wiki_pub

        )

        try:
            # Création d'une nouvelle entrée dans la table Publication.
            db.session.add(created_publication)
            db.session.commit()

            # Création d'un enregistrement dans Authorship_publication avec utilisation de la fonction authorship_pub_event.
            creation = Publication.query.filter(
                Publication.publication_external_login == login_wiki_pub).one()
            authorship_publication = Authorship_publication.authorship_pub_event(
                updated=creation
            )
            # Renvoi des informations d'enregistrement vers le contributeur
            return True, created_publication

        except Exception as error_creation:
            return False, [str(error_creation)]

    @staticmethod
    def modif_pub(publication_id, publication_poet_id, titre, date, genre_litteraire, login_wiki_pub):
        """
        Fonction permettant la modification d'une référence bibliographique dans la base de données.
        :param publication_id: identifiant numérique de la publication ou de la production
        :type publication_id: integer
        :param publication_poet_id: identifiant numérique de l'auteur
        :type publication_poet_id: integer
        :param titre : titre de la publication ou de la production
        :param date : date de la publication originale ou de la production
        :param genre_litteraire : genre littéraire de la publication ou de la production
        :param login_wiki_pub : identifiant externe créé par l'utilisateur lors d'une création de notice
        :type titre, date, genre_litteraire, login_wiki_pub: string
        :returns : Tuple (booléen, liste/objet).
        S'il y a une erreur, la fonction renvoie False suivi d'une liste d'erreurs.
        Sinon, elle renvoie True, suivi de l'objet mis à jour.
        """
        errors=[]
        # Création d'une liste vide pour y stocker les erreurs.
        if not publication_id:
            errors.append("erreur d'identification de la référence à éditer")
        if not titre:
            errors.append("La mention du titre est obligatoire")
        if not date:
            errors.append("La mention de la date d'édition originale ou de production est obligatoire")
        if not genre_litteraire:
            errors.append("La mention du genre littéraire est obligatoire")
        if not login_wiki_pub:
            errors.append("La création d'un identifiant composé au maximum de 10 lettres et/ou chiffres est obligatoire")
        if len(errors) > 0:
            return False, errors

        #Récupération d'une référence bibliographique dans la base.
        modif_pub = Publication.query.get(publication_id)
        # On s'assure que l'utilisateur modifie au moins un champ. Sinon, retourne une erreur.
        if modif_pub.publication_titre == titre \
                and modif_pub.publication_date == date \
                and modif_pub.publication_genre_litteraire == genre_litteraire \
                and modif_pub.publication_external_login == login_wiki_pub:
            errors.append("Aucune modification n'a été réalisée")

        if len(errors) > 0:
            return False, errors

        if len(date) > 12 :
            errors.append("La date ne doit pas dépasser 12 caractères")
        if len(errors) > 0:
            return False, errors

        # Vérifie que la taille des caractères insérés (login_wiki_pub) par l'utilisateur ne dépasse pas la limite de 10.
        if len(login_wiki_pub) > 10:
            errors.append("L'identifiant ne doit pas dépasser 10 caractères'")
        if len(errors) > 0:
            return False, errors
        #Mise à jour des données de la référence bibliographique modifiée.
        else:
            modif_pub.publication_titre = titre
            modif_pub.publication_date = date
            modif_pub.publication_genre_litteraire = genre_litteraire
            modif_pub.publication_external_login = login_wiki_pub
        #Ajout de la mise à jour dans la base de données.
        try:
            db.session.add(modif_pub)
            db.session.commit()
        #Ajout d'un enregistrement dans Authorship_publication grâce à la fonction authorship_pub_event.
            authorship_publication=Authorship_publication.authorship_pub_event(
                updated=Publication.query.get(publication_id)
            )

            return True, modif_pub

        except Exception as error_modif_pub:
            return False, [str(error_modif_pub)]

class Military_status(db.Model):
    __tablename__ = "Military_status"
    military_status_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    military_status_statut = db.Column(db.Text)
    military_status_lieu_recrutement = db.Column(db.Text)
    military_status_registre_matricule = db.Column(db.Text)
    military_status_poet_id = db.Column(db.Integer, db.ForeignKey("Poet.poet_id"), nullable=False)
    military_status_grade = db.Column(db.Text)
    military_status_external_login=db.Column(db.Text)
    #Jointures entre les tables Military_status et Poet; ainsi qu'entre les tables Military_status et Authorship_military_status.
    poetstatus = db.relationship("Poet", foreign_keys=[military_status_poet_id])
    authorships_esm = db.relationship("Authorship_military_status", back_populates="status", cascade="all, delete")

    def status_to_json(self):
        """
        Fonction qui permet l'export en Json des informations relatives à l'ESM d'un(e) poète(sse)
        rtype: dictionnaire.
        """
        return {
            "id": self.military_status_id,
            "attributes": {
                "statut": self.military_status_statut,
                "lieu_recrutement": self.military_status_lieu_recrutement,
                "registre_matricule": self.military_status_registre_matricule,
                "grade": self.military_status_grade
            }
        }

    @staticmethod
    def create_military_status(statut, lieu_recrutement, registre_matricule, poet_id, grade, login_wiki_esm):
        """
        Fonction permettant la création d'un nouvel ESM lors de la création d'une notice de poète par un utilisateur identifié.
        :param statut : statut militaire de l'individu
        :param lieu_recrutement : lieu de recrutement si l'individu est mobilisé ou engagé volontaire
        :param registre_matricule : numéro de registre matricule si l'individu est mobilisé ou engagé volontaire
        :param poet_id : identifiant numérique de l'auteur
        :type poet_id : integer
        :param grade: grade militaire de l'individu s'il est mobilisé ou engagé volontaire
        :param login_wiki_esm : identifiant externe créé par l'utilisateur lors d'une création de notice
        :type statut, lieu_recrutement, registre_matricule, grade, login_wiki_esm: string
        returns : Tuple (booléen, liste/objet).
        S'il y a une erreur, la fonction renvoie False suivi d'une liste d'erreurs.
        """
        errors = []
        # Création d'une liste vide pour y stocker les erreurs.
        #Génération d'une erreur si le champ du statut militaire est vide.
        if not statut:
            errors.append("La mention du statut militaire est obligatoire")
        if len(errors) > 0:
            return False, errors

        military_status_log = Military_status.query.filter(Military_status.military_status_external_login == login_wiki_esm).count()
        #On vérifie que l'identifiant externe n'est pas déjà utilisé.
        if military_status_log > 0:
            errors.append("Cet identifiant est déjà utilisé")

        if len(errors) > 0:
            return False, errors

        created_military_status = Military_status(
            military_status_statut=statut,
            military_status_lieu_recrutement=lieu_recrutement,
            military_status_registre_matricule=registre_matricule,
            military_status_poet_id=poet_id,
            military_status_grade=grade,
            military_status_external_login=login_wiki_esm

        )

        try:
            # Création d'une nouvelle entrée dans la table Military_status
            db.session.add(created_military_status)
            db.session.commit()

            # Création d'un enregistrement dans Authorship_military_status avec utilisation de la fonction authorship_esm_event.
            creation = Military_status.query.filter(Military_status.military_status_external_login==login_wiki_esm).one()
            authorship_military_status=Authorship_military_status.authorship_esm_event(
                updated=creation
            )
            #Renvoi des informations d'enregistrement vers le contributeur
            return True, created_military_status

        except Exception as error_creation:
            return False, [str(error_creation)]

    @staticmethod
    def modif_statut(military_status_id, statut, lieu_recrutement, registre_matricule, grade, login_wiki_esm):
        """
        Fonction permettant la modification d'un ESM dans la base de données.
        :param military_status_id: identifiant numérique de l'ESM
        :type military_status_id: integer
        :param statut : statut militaire de l'individu
        :param lieu_recrutement : lieu de recrutement si l'individu est mobilisé ou engagé volontaire
        :param registre_matricule : numéro de registre matricule si l'individu est mobilisé ou engagé volontaire
        :type statut, lieu_recrutement, registre_matricule, grade, login_wiki_esm: string
        :returns : Tuple (booléen, liste/objet).
        S'il y a une erreur, la fonction renvoie False suivi d'une liste d'erreurs.
        Sinon, elle renvoie True, suivi de l'objet mis à jour.
        """

        errors=[]
        # Création d'une liste vide pour y stocker les erreurs.
        if not military_status_id:
            errors.append("erreur d'identification de l'ESM à éditer")
        if not statut:
            errors.append("La mention du statut militaire est obligatoire")
        if not login_wiki_esm:
            errors.append("La mention d'un identifiant composé au maximum de 10 lettres et/ou chiffres est obligatoire")
        if len(errors) > 0:
            return False, errors
        #Récupération d'un ESM dans la base.
        modif_statut = Military_status.query.get(military_status_id)
        # On s'assure que l'utilisateur modifie au moins un champ. Sinon, retourne une erreur.
        if modif_statut.military_status_statut == statut \
                and modif_statut.military_status_lieu_recrutement == lieu_recrutement \
                and modif_statut.military_status_registre_matricule == registre_matricule \
                and modif_statut.military_status_grade == grade \
                and modif_statut.military_status_external_login == login_wiki_esm:
            errors.append("Aucune modification n'a été réalisée")

        if len(errors) > 0:
            return False, errors

        # Vérifie que la taille des caractères insérés (login_wiki_esm) par l'utilisateur ne dépasse pas la limite de 10.
        if len(login_wiki_esm) > 10:
            errors.append("L'identifiant ne doit pas dépasser 10 caractères'")
        if len(errors) > 0:
            return False, errors
        # Mise à jour des données de l'ESM modifié.
        else:
            modif_statut.military_status_statut = statut
            modif_statut.military_status_lieu_recrutement = lieu_recrutement
            modif_statut.military_status_registre_matricule = registre_matricule
            modif_statut.military_status_external_login = login_wiki_esm
        # Ajout de la mise à jour dans la base de données.
        try:
            db.session.add(modif_statut)
            db.session.commit()
        # Création d'un enregistrement dans Authorship_military_status.
            authorship_military_status=Authorship_military_status.authorship_esm_event(
                updated=Military_status.query.get(military_status_id)
            )

            return True, modif_statut

        except Exception as error_modif_statut:
            return False, [str(error_modif_statut)]

class Authorship_poet(db.Model):
    __tablename__ = "Authorship_poet"
    authorship_poet_id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    authorship_poet_user_id = db.Column(db.Integer, db.ForeignKey("User.user_id"))
    authorship_poet_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    authorship_poet_poet_id = db.Column(db.Integer, db.ForeignKey("Poet.poet_id"))
    #Jointures entre les tables Authorship_poet et Poet; ainsi qu'entre les tables Authorship_poet et User.
    poet = db.relationship("Poet", back_populates="authorships_poet")
    user_poet = db.relationship("User", back_populates ="authorship_poet")

    @staticmethod
    def authorship_event(updated):
        """
        Fonction permettant l'inscription d'un événement (création ou modification) concernant un objet de la table Poet.
        :returns: True en cas de réussite, False en cas d'échec.
        :rtype: booléen
        """
        entry = Authorship_poet(
            authorship_poet_user_id=current_user.get_id(),
            authorship_poet_poet_id=updated.poet_id
        )
        #Ajout et enregistrement dans la base de données.
        try:
            db.session.add(entry)
            db.session.commit()
            return True

        except Exception as why:
            print(why)
            return False

    @staticmethod
    def delete_logs(id_poet):
        """
        Fonction qui supprime les enregistrements liés au poète récupéré par son id.
        :param id_poet: identifiant numérique du/de la poète(sse) à supprimer
        :type id_poet: integer
        :returns: booléen
        """
        logs = Authorship_poet.query.filter(Authorship_poet.authorship_poet_poet_id == id_poet).all()
        for log in logs:
            db.session.delete(log)
            db.session.commit()

class Authorship_military_status(db.Model):
    __tablename__ = "Authorship_military_status"
    authorship_military_status_id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    authorship_military_status_user_id = db.Column(db.Integer, db.ForeignKey("User.user_id"))
    authorship_military_status_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    authorship_military_status_military_status_id = db.Column(db.Integer, db.ForeignKey("Military_status.military_status_id"))
    #Jointures entre les tables Authorship_military_status et Military_status; ainsi qu'entre les tables Authorship_military_status et User.
    status = db.relationship("Military_status", back_populates="authorships_esm")
    user_status = db.relationship("User", back_populates="authorship_military_status")

    @staticmethod
    def authorship_esm_event(updated):
        """
        Fonction permettant l'inscription d'un événement (création ou modification) concernant un objet de la table Military_status.
        :returns: True en cas de réussite, False en cas d'échec.
        :rtype: booléen
        """
        entry = Authorship_military_status(
            authorship_military_status_user_id=current_user.get_id(),
            authorship_military_status_military_status_id=updated.military_status_id
        )
        try:
            db.session.add(entry)
            db.session.commit()
            return True

        except Exception as why:
            print(why)
            return False



class Authorship_publication(db.Model):
    __tablename__ = "Authorship_publication"
    authorship_publication_id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    authorship_publication_user_id = db.Column(db.Integer, db.ForeignKey("User.user_id"))
    authorship_publication_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    authorship_publication_publication_id = db.Column(db.Integer, db.ForeignKey("Publication.publication_id"))
    #Jointures entre les tables Authorship_publication et Publication; ainsi qu'entre les tables Authorship_publication et User.
    pub = db.relationship("Publication", back_populates="authorships_pub")
    user_pub = db.relationship("User", back_populates="authorship_pub")

    @staticmethod
    def authorship_pub_event(updated):
        """
        Fonction permettant l'inscription d'un événement (création ou modification) concernant un objet de la table Publication.
        :returns: True en cas de réussite, False en cas d'échec.
        :rtype: booléen
        """
        entry = Authorship_publication(
            authorship_publication_user_id=current_user.get_id(),
            authorship_publication_publication_id=updated.publication_id
        )
        try:
            db.session.add(entry)
            db.session.commit()
            return True

        except Exception as why:
            print(why)
            return False