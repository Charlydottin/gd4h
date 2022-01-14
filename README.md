# GD4H MVP

Minimum viable product pour la plateforme du catalogue Green Data For Health

## Fonctionnalités

- Affichage et gestion du catalogague (jeux de données, organismes, référentiels et normes)
- Recherche plein texte 
- Filtres contextuels pour les jeux de donnée
- Commentaires sur la plateforme, sur un jeu de données, sur une section du jeu de données, et sur un champs
- Traduction Français Anglais

## Architecture

Le projet est organisé de la manière suivante:
```
.
├── back
│   ├── apps
│   │   ├── dataset
│   │   ├── filter
│   │   ├── __init__.py
│   │   ├── organization
│   │   ├── references
│   │   ├── search
│   │   └── translate
│   ├── config
│   ├── index.py
│   ├── __init__.py
│   ├── main.py
│   ├── requirements.in
│   ├── requirements.txt
│   ├── scripts
│   ├── static
│   └── tests
├── data
│   ├── comments
│   ├── datasets
│   ├── es_indexation
│   ├── meta
│   ├── organizations
│   ├── raw
│   └── references
├── front
│   ├── flask_app
│   └── future_react
└── README.md
```

### Data

Dossier qui contient les données sont sous forme de fichiers csv:

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

sudo apt-get update
sudo apt install apt-transport-https ca-certificates wget
sudo apt-get install -Y git python3 virtualenv
sudo apt-get install python3-pip python3-dev nginx

#### MongoDB

```
wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list

sudo apt update
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
sudo systemctl status mongod
sudo systemctl enable mongod
```

#### ElasticSearch
```
sudo apt install openjdk-8-jre-headless
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb https://artifacts.elastic.co/packages/6.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elasticsearch-6.list
sudo apt update
sudo apt install elasticsearch
sudo systemctl enable --now elasticsearch.service
curl -X GET "localhost:9200/"
```

#### ArgosTranslate
```
sudo snap install argos-translate
argospm install translate-fr_en
argospm install translate-en_fr
```

### BACK

```
cd back
virtualenv .env
source .venv/bin/activate
pip install -r requirement.txt
source .env
```
#### Initialize database

```
source .venv/bin/activate
cd back/scripts/
python init_db.py
```

### FRONT

```

cd front/flask_app
virtualenv .env
source .venv/bin/activate
pip install -r requirement.txt
```


## Deployement

### BACK

* nginx 

/etc/nginx/sites-available/gd4h-api

```

server{
       server_name api.gd4h api.gd4h.fr;
       location / {
           include proxy_params;
           proxy_pass http://127.0.0.1:3000;
       }
}
```
sudo ln -s /etc/nginx/sites-available/gd4h-api /etc/nginx/sites-enabled/


sudo systemctl restart nginx.service


* Service systemd
  
Edit /etc/systemd/system/gd4h-api.service

```
[Unit]
Description=Gunicorn instance to serve gd4h-api
After=network.target

[Service]
User=gd4h-admin
Group=www-data
WorkingDirectory=/home/gd4h-admin/GD4H/back/
Environment="PATH=/home/gd4h-admin/GD4H/back/.venv/bin"
ExecStart=/home/gd4h-admin/GD4H/back/.venv/bin/gunicorn --bind=127.0.0.1:3000 -w 4 -k uvicorn.workers.UvicornWorker main:app

[Install]
WantedBy=multi-user.target
```

sudo systemctl start gd4h-api.service


### FRONT


