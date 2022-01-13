# GD4H MVP

Minimum viable product pour la plateforme du catalogue Green Data For Health

## Fonctionnalités

- Affichage et gestion du catalogague (jeux de données, organismes, référentiels et normes)
- Recherche plein texte 
- Filtres contextuels pour les jeux de donnée
- Commentaires sur la plateforme, sur un jeu de données, sur une section du jeu de données, et sur un champs


## Architecture

Le projet est organisé de la manière suivante:

### Data

Dossier qui contient les données sont forme de fichiers csv:

- un premier recensement des données du catalogue GD4H (datasets)
- une premiere liste de producteurs de données (organizations)
- une liste de référentiels: soit toutes les valeurs controlées pour les champ descriptifs de chaque modele (references)
- un dossier meta qui recense toutes les règles d'affichage, de traitement pour chaque modele et chaque champ descriptif (meta)

> Les données sont initialisées dans la Base de données via le script /back/init_db

### BACK 

Le back-end consiste dans une:
- API FastAPI (Python3) qui gère toutes les interactions avec la 
- Base de Données (MongoDB pour le moment)
- et le moteur d'indexation ElasticSearch

### FRONT
  
Le front-end consiste pour le moment en une application :
- Flask qui charge :
  - des templates jinja2  utilisant les fichiers sources du design system de l'état (css, icons, js)
  - les données de la BAse de données via l'API Back


## Install

Pour le moment l'installation a été prévue simplement sur le système d'exploitation Ubuntu 20.04

clone this repository

git clone 

### System requirements

sudo apt-get install -Y git python3 nginx systemd virtualenv mongodb elasticsearch


### FRONT