# INSTALL

## From package

OS requirements: Ubuntu 20.04 LTS

> plus l'installation est fraîche, mieux c'est


## INSTALL

* SYS REQUIREMENTS
```bash
sudo apt update

sudo apt install -y libpq5 redis-server nginx supervisor
wget https://packaging.ckan.org/python-ckan_2.9-py3-focal_amd64.deb
sudo dpkg -i python-ckan_2.9-py3-focal_amd64.deb
```

* POSTGRESQL
```bash

sudo apt install -y postgresql

sudo -u postgres psql -l
sudo -u postgres createuser -S -D -R -P ckan_default
sudo -u postgres createdb -O ckan_default ckan_default -E utf-8
```

* TOMCAT + SOLR
```bash
sudo apt install -y solr-tomcat

sudo nano /etc/tomcat9/server.xml
```

```xml
<Connector port="8080" protocol="HTTP/1.1"
```
to:
```xml
<Connector port="8983" protocol="HTTP/1.1"
```

```bash
sudo mv /etc/solr/conf/schema.xml /etc/solr/conf/schema.xml.bak
sudo ln -s /usr/lib/ckan/default/src/ckan/ckan/config/solr/schema.xml /etc/solr/conf/schema.xml
```

```
# redémarrer tomat
sudo service tomcat9 restart

```
* editer le fichier de config `/etc/ckan/default/ckan.ini`
```
solr_url=http://127.0.0.1:8983/solr
```
> Attention: le package installe par default jetty et non pas tomcat avec solr !


## CONFIGURE

* Generate config for ckan:

> La documentation dit :

`ckan generate config /etc/ckan/default/ckan.ini`

Mais: 

> /etc/ckan/default/ckan.ini est déjà installé avec le package 

> il faut cependant changer le propriétaire du dossier 

> puis créer/activer un virtualenv pour le faire marcher

```
sudo chown -R `whoami`:`whoami` /etc/ckan/
```

Les parametres minimaux à configurer sont le fichier de configuration par default  `/etc/ckan/default/ckan.ini`

```
ckan.site_id = default
ckan.site_url = http://localhost:5000
sqlalchemy.url = postgresql://ckan_default:_changepassw_@localhost/ckan_default
solr_url=http://127.0.0.1:8983/solr
```


* Initialize db
```
cd /usr/lib/ckan/default/src/ckan
ckan -c /etc/ckan/default/ckan.ini db init
```

* Create virtualenv
`sudo python3 -m venv /usr/lib/ckan/default/`

* Activate virtualenv:

`source /usr/lib/ckan/default/bin/activate`

* upgrade easy install and pip
```
pip install setuptools==44.10
pip install --upgrade pip
```


## RUN

```
cd /usr/lib/ckan/default/src/ckan
ckan -c /etc/ckan/default/ckan.ini run
```

open http://localhost:5000

## NEXT

### Test
https://docs.ckan.org/en/2.9/contributing/test.html

> Fail with permissions error and dependency hell

### Deployement
see [deployement.md](Deployement instruction)

[Official doc ](https://docs.ckan.org/en/2.9/maintaining/installing/deployment.html)

### Customize


* Add storage for upload in `/etc/ckan/default/ckan.ini`
```
## Storage Settings

ckan.storage_path = /var/lib/ckan
ckan.max_resource_size = 10
ckan.max_image_size = 2
```
Relancer ckan `ckan -c /etc/ckan/default/ckan.ini run`
> Permission denied: '/var/lib/ckan/storage/

>> changer les droits sur /var/lib/ckan:
>> `sudo chown $USER:$SUSER /var/lib/ckan`

* Create an admin
```
ckan -c /etc/ckan/default/ckan.ini sysadmin add admin email=admin@localhost name=admin
```
Enter password: `A****A****I*****'

* promote him as sysadmin (duplicate)
ckan -c /etc/ckan/default/ckan.ini sysadmin add admin

* Change site title and description in `/etc/ckan/default/ckan.ini`

```
ckan.site_title = 
ckan.site_description = 
```
Relaunch to test

`ckan -c /etc/ckan/default/ckan.ini run`

> PermissionError: [Errno 13] Permission denied: '/var/lib/ckan/webassets/.webassets-cache/14026a1632531c2b1445ac9963f41c0b'

>> Changer les permissions `sudo chown -R $USER:$USER /var/lib/ckan`

La documentation dit de relancer gunicorn et nginx 
`sudo supervisorctl restart ckan-uwsgi:*`

mais valable seulement en prod
>>> ckan-uwsgi:ckan-uwsgi-00: ERROR (spawn error) 
voir les [instructions pour le deploiement](https://docs.ckan.org/en/2.9/maintaining/installing/deployment.html) 

En local
`ckan -c /etc/ckan/default/ckan.ini run ` 
Fait tourner correctement la plateforme
Si les changements n'apparaissent pas et ne semblent pas pris en compte:
`ckan -c /etc/ckan/default/ckan.ini db init `
puis
`ckan -c /etc/ckan/default/ckan.ini run ` 