# OGDATA

## A propos

Open Green Data est un prototype de mise à disposition du catalogue de jeux de données autour de la thématique santé-environnement.


## Objectifs

Rendre consultable le catalogue de jeux de données disponibles sur la thématique Santé et Environnement aujourd'hui disponible en Excel



### MUST
- Consulter le catalogue des jeux de données Santé Environnement facilement via une interface web (aujourd'hui disponible en Excel)
- Consulter, ajouter et modifier les informations relatives aux licenses
- Consulter Ajouter modifier, supprimer les informations concernant les producteurs de données
- Recherche d'un jeux de données par mot clés (anglais et français)
- Recherche et tri par filtres (selon les dimensions présentes dans le fichier excel)
- Ajout, modification, suppression d'un jeux de données manuel et automatique
- Ajout, modification, suppression d'un producteur de données
- Ajout, modification, suppression d'une license


### SHOULD
- Ajout, modification et suppression de producteurs de données
- Gestion de droits de consultation en fonction du paramêtre du JDDS d'accessibilité (OUVERT/FERME)
- Commentaires utilisateurs sur le jeux de données

### NICE TO HAVE

- Suivi de version du catalogue (versionning git) au niveau d'un jeu de données
- Statistiques avancées (consultations, modifications, ajouts, nombre de datasets, nombre de contributeurs actifs )
- Retour utilisateur qualifié sur une dimension d'un jeu de données




## Stack technique:

- Base de données: MongoDB
- Application WEB: 
    - Back Flask Python
    - Front ReactJS
    - HTML5/CSS3/JS
- API:
    - Flask Restfull/ FASTAPI?
- Indexation: 
    - ElasticSearch

- Serveur: Ubuntu/Debian? + Nginx + GNUnicorn


## Schéma fonctionnel


