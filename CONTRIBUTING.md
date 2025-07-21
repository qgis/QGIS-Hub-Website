# ✨ Contributing to QGIS-Hub-Website

Thank you for considering contributing to QGIS Hub Website!
We welcome contributions of all kinds, including bug fixes, feature requests,
documentation improvements, and more. Please follow the guidelines below to
ensure a smooth contribution process.

![-----------------------------------------------------](./img/green-gradient.png)


## 🏃Before you start
 
This project requires [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) to run the development and production environments.  
Please ensure both are installed on your system before proceeding.

![Docker logo](https://www.docker.com/wp-content/uploads/2022/03/Moby-logo.png)

You can check your installation with:
```bash
docker --version
docker-compose --version
```

![-----------------------------------------------------](./img/green-gradient.png)

## 🛒 Getting the Code

- Clone git repo `git clone https://github.com/qgis/QGIS-Hub-Website.git`
- Run `$ pwd` in order to get your current directory
- Path to your repo should be `<your current directory>/QGIS-Hub-Website `
- Go to dockerize directory `cd QGIS-Hub-Website/dockerize`


![-----------------------------------------------------](./img/green-gradient.png)


## 🧑💻 Development


- Create .env file
```bash
$ cp .env.template .env
```

- Edit .env file and set your environment variables
- Enable debug mode by setting `DEBUG=True`.

- Build and spin container
```bash
$ make build
$ make web
$ make devweb
```

- Run migrate
```bash
$ make migrate
```

If you have a backup, you can restore it:

```bash
make dbrestore
```

otherwise, you can seed initial data from fixtures:
```
make dbseed
```

- Set up python interpreter in PyCharm or just runserver from devweb container:
```bash
$ make devweb-runserver
```
and now, you can see your site at `http://0.0.0.0:62202` (skip this step if you are using PyCharm interpreter)


- You can use the following credentials to log in if you ran the `make dbseed` command:
```
Admin account:
username: admin
password: admin

Staff account:
username: staff
password: staff

Plugin author account:
username: creator
password: creator
```

For more information about make commands, please see the full docs [here](./dockerize/README.md).


### Nix

Run the following command on this project root folder:

```sh
nix-shell
./vscode.sh
```
TODO: Install all dependecies when running nix-shell.


### Setup git-hooks and local linting

In the root directory of the repo, run:

```bash
pip install -r REQUIREMENTS-dev.txt

pre-commit install --config .pre-commit-config.yaml
```


### Setting up a remote interpreter in PyCharm

- PyCharm -> Preferences -> Project: QGIS-Hub-Website
- Click on the gear icon next to project interpreter -> add
- SSH Interpreter -> New server configuration
- Host : `localhost`
- Port : `62203`
- Username: `root`
- Click next button
- Auth type: password (and tick 'save password')
- Click next button
- password : `docker`
- Interpreter : ``/usr/local/bin/python``
- Sync folders -> click on the folder icon
  - local : `<path to your repo>/dockerize/qgis-app`
  - remote : `/home/web/django_project`
  After that you should see something like this in sync folder:
   `<Project root>/django_project→/home/web/django_project`
- Automatically upload project files to the server -> untick the checkbox to avoid overwriting in your files.
- Click the Apply button


#### In settings, django support:

- Language & Framework -> Django
- tick to Enable Django Support.
- Django project root: ``<path to your repo>/qgis_app``
- Settings: setting_docker.py
- Click the Apply button

#### Create the django run configuration

- Run -> Edit configurations
- Click the `+` icon in the top left corner
- Choose ``Django server`` from the popup list

Now set these options:

* **Name:** Django Server
* **Host:** 0.0.0.0
* **Port:** 8080
* **Additional options:** ``--settings=settings.docker``
* **Run browser** If checked, it will open the url after you click run. You should be able to access the running on 0.0.0.0:62202 (the port that mapped to 8080)

* **Environment vars** , you can add the variables value one-by-one by clicking on browse icon at right corner in the input field, or just copy-paste this value:
`PYTHONUNBUFFERED=1;DJANGO_SETTINGS_MODULE=settings_docker;DATABASE_NAME=gis;DATABASE_USERNAME=docker;DATABASE_PASSWORD=docker;DATABASE_HOST=db`
* **Python interpreter:** Ensure it is set you your remote interpreter (should be
  set to that by default)

* **Path mappings:** Here you need to indicate path equivalency between your host
  filesystem and the filesystem in the remote (docker) host. Click the ellipsis
  and add a run that points to your git checkout on your local host and the
  /home/web directory in the docker host. e.g.
  * **Local path:** <path to your git repo>/QGIS-Hub-Website/qgis-app
  * **Remote path:** /home/web/django_project
* click OK to save your run configuration

Now you can run the server using the green triangle next to the Django server
label in the run configurations pull down. Debug will also work and you will be
able to step through views etc as you work.

![-----------------------------------------------------](./img/green-gradient.png)


## Setup Style Managers Group

The members of this group will receive style related emails.
Follow these steps for setting up:
- Open admin page: `http://0.0.0.0:62202/admin`, login with superuser account.
- Create new Group: `Authentication and Authorization > Groups > Add group`
- Set the options:
  - **Name:** `Style Managers`
  - **Permissions:**
    choose all styles | in **Available permissions** by typing `styles` in search input and click `Choose all`
    - styles | style | Can add style
    - styles | style | Can change style
    - styles | style | Can delete style
    - styles | style | Can view style
    - styles | style review | Can add style review
    - styles | style review | Can change style review
    - styles | style review | Can delete style review
    - styles | style review | Can view style review
    - styles | style type | Can add style type
    - styles | style type | Can change style type
    - styles | style type | Can delete style type
    - styles | style type | Can view style type


![-----------------------------------------------------](./img/green-gradient.png)

## Setup Map Publishers Group

The members of this group will receive map related emails.
Follow these steps for setting up:
- Open admin page: `http://0.0.0.0:62202/admin`, login with superuser account.
- Create new Group: `Authentication and Authorization > Groups > Add group`
- Set the options:
  - **Name:** `Map Publishers`
  - **Permissions:**
    choose all styles | in **Available permissions** by typing `map` in search input and click `Choose all`
    - map_gallery | map | Can change map


![-----------------------------------------------------](./img/green-gradient.png)

## Backup and Restore

- Go to repo directory and run backup.sh
```bash
$ ./backup.sh
```
- You will find dumps file in backups directory
```bash
$ tree -L 3 backups
backups
├── 2016
├── 2017
├── 2018
├── 2019
├── 2020
│   ├── April
│   │   └── PG_QGIS_HUB_gis.07-April-2020.dmp
│   ├── August
│   ├── December
│   │   ├── PG_QGIS_HUB_gis.01-December-2020.dmp
│   │   ├── PG_QGIS_HUB_gis.02-December-2020.dmp
│   │   ├── PG_QGIS_HUB_gis.03-December-2020.dmp
│   │   ├── PG_QGIS_HUB_gis.04-December-2020.dmp
│   │   ├── PG_QGIS_HUB_gis.05-December-2020.dmp
│   │   ├── PG_QGIS_HUB_gis.06-December-2020.dmp
│   │   ├── PG_QGIS_HUB_gis.07-December-2020.dmp
│   │   ├── PG_QGIS_HUB_gis.08-December-2020.dmp
│   │   ├── PG_QGIS_HUB_gis.09-December-2020.dmp
│   │   ├── PG_QGIS_HUB_gis.10-December-2020.dmp
│   │   ├── PG_QGIS_HUB_gis.11-December-2020.dmp
│   │   ├── PG_QGIS_HUB_gis.12-December-2020.dmp
│   │   ├── PG_QGIS_HUB_gis.13-December-2020.dmp
│   │   ├── PG_QGIS_HUB_gis.14-December-2020.dmp
│   │   ├── PG_QGIS_HUB_gis.15-December-2020.dmp
│   │   └── PG_QGIS_HUB_gis.16-December-2020.dmp
│`
```

- Copy the dump file you wish to restore to dockerize/backups/latest.dmp file
```bash
$ cp backups/2020/December/PG_QGIS_HUB_gis.16-December-2020.dmp dockerize/backups/latest.dmp
```

- Restore the dump file
```bash
$ cd dockerize
$ make dbrestore
```


![-----------------------------------------------------](./img/green-gradient.png)

## Production Environment
For the production environment, please see the the private repo of the System Administration Documentation.
