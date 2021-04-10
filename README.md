# WWI-Poets

WWI-Poets est une application web recensant les poètes de la Première Guerre mondiale et leurs productions. Elle a été développée par Pauline Breton-Chauvet avec le framework Flask pour l'évaluation du module Python (École nationale des Chartes-Master 2 TNAH). Son graphisme est réalisé grâce au framework Bootstrap.

## Contexte et fonctionnalités

WWI-Poets est une application (Python3) reliée à une base de données relationnelle à visée prosopographique. Elle est dédiée au recensement et à la présentation des poètes de la Première Guerre mondiale, issus de toutes les nationalités belligérantes. Ce projet s'inspire du programme numérique Poésie-Grande Guerre (Université Paris Ouest-Nanterre la Défense), conçu en partie par l'auteure de cette application. Les données inhérentes aux individus, aux oeuvres littéraires ainsi qu'aux états de situation militaire (ESM) ont ainsi été partiellement extraites de la maquette fonctionnelle de PGG avant d'être traitées, intégrées à un nouveau modèle relationnel et stockées dans une base DBBrowser for SQLite.

**Sans inscription et identification préalable, chacun(e) peut:**
- Effectuer une recherche rapide par mot(s)-clé(s), dont la liste générique figure en présentation de l'application et sous la barre de recherche.
- Parcourir les index d'individus et index de productions littéraires.
- Consulter les notices individuelles de poètes et en exporter les données en format Json.

**Chaque utilisateur-trice inscrit(e) et identifié(e) a accès aux fonctionnalités suivantes:**
- Création et suppression de notices biographiques complètes de poètes (comprenant également la/les production(s) littéraire(s) et l'ESM)
- Modifications ciblées en particulier sur la notice biographique, l'ESM et/ou la/les référence(s) bibliographique(s).

## Installation

### Linux (Ubuntu/Debian)

**Première utilisation**

  - Installer python3
  - À l'aide d'un terminal, cloner ce dépôt Git : `https://github.com/PaulineChauvet/WWI-Poets.git`
  - Rentrer dedans
  - Installer, configurer et lancer un environnement virtuel avec Python3 : `virtualenv env -p python3` pour l'installation.
    Puis `source env/bin/activate` pour le lancement.
  - Installer les librairies nécessaires au fonctionnement de l’application: `pip install -r requirements.txt`
  - Lancer l'application avec la commande : `python3 run.py`

**Lors des utilisations suivantes**

  - `source env/bin/activate` pour le lancement
  - Lancer l'application avec la commande `python3 run.py`





