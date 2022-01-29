# GD4H MVP

Minimum viable product pour la plateforme du catalogue Green Data For Health

## Fonctionnalités

- Affichage et gestion du catalogague (jeux de données, organismes, référentiels et normes, commentaires)
- Recherche plein texte.
- Filtres contextuels pour les jeux de donnée
- Commentaires sur la plateforme, sur un jeu de données, sur une section du jeu de données et sur un champs
- Traduction Français Anglais

## Architecture

Le projet est composé de plusieurs briques fonctionnelles et ordonné de la manière suivante:

#### `scripts`
  - initialisation d'une base de données (MongoDB)
  - initialisation du moteur d'indexation et de recherche (Elastic Search)
  - import/export des données d'initialisation (cf. [data](####data))

#### `back` 
  - Une API (FastAPI) qui gère les interaction avec la base de données et le moteur de recherche

#### `front`
  - un site web (Flask) (provisoire) 
  - moteur de templating Jinja2
  - fichiers sources du dsfr (font, css, js, image, icon)

#### data

Les données qui permettent la création et l'initialisation de la base de données, l'indexation mais aussi toutes les règles d'affichage 
de filtrage et de requetage.

data est le dossier qui contient toutes les données et paramétrages de départ: 
elles sont toutes au format csv puis insérée dans la base de données à l'initialisation

##### données du catalogue:
  
  - fichier issu d'un premier recensement des données du catalogue GD4H (datasets) en Français `/datasets/fr_datasets.csv` 
    > correspond à la table `datasets` accessible dans l'API via le endpoint `/datasets`
  - fichier issu d'un premier recensement des données du catalogue GD4H (organizations) en Français `/organizations/fr_organizations.csv` 
    > correspond à la table  `organizations` accessible dans l'API via le endpoint `/organizations`
  
###### données méta `/meta/`

Les données méta décrivent l'ensemble des champs qui définissent un modèle, toutes les règles qui s'attachent aux champs définitoires d'un modèle. C'est el point d'entrée du paramétrage des contenus.
En effet le fichier `rules.csv` liste tous les champs de données pour tous les modèles présents dans la BDD et dicte la manière d':

- insérer/modifier/supprimer les données dans la base
- indexer les données dans ElasticSearch
- valider les données
- afficher les données 
- afficher les filtres

##### données descriptives `/references/`

Ces données correspondent aux nomenclatures à respecter pour ajouter une valeur à un champ descriptif d'un jeu de données ou d'une organisation.
Pour décrire un jeu de données on utilse plusieurs champs tel que le nom l'url et le sujet, les règles de ce que peut contenir le champ "sujet" est défini grace aux références qui détaille les valeurs acceptées pour le champ sujet.

  - une liste de tous les champs dans les valeurs sont controlées appelée `références`:

    > Exemple: un dataset possède un champ descriptif "Nature et Usage", celui ci accepte seulement les valeurs :Biodiversité, Indicateurs géographiques et socio-démographiques, Agents Physiques, Pesticides
    
Le fichier csv puis la table `references` liste toutes les champs dont les valeurs sont controlées par un référentiel.

table `references`
  | field_slug   | table_name|field_label_fr  | field_label_en|
  |------------|-----------|----------------|---------------|
  |nature      | ref_nature| Nature et Usage| Use and Nature|



  - pour chaque référence controlée on trouve la liste des valeurs acceptées en anglais et en francais aggrémenté d'une uri si référentiel sémantique appelée `ref_<nom_du_champ>`:

    > Exemple : Le champ Nature et Usage
    
stocké dans la table `ref_nature`


|field_label_fr  | field_label_en| uri                 |
|----------------|---------------|---------------------|
|Biodiversité    | Biodiversity  |                     |
|Agents Physiques| Physical Agents  |                     |
|Indicateurs géographiques et socio-démographiques|Géographical and socio-demographical indicators||
| Pesticides     | Pesticides |http://purl.obolibrary.org/obo/ENVO_01000371|


## Installation et déploiement

Cf. [INSTALL.md](INSTALL.md)

