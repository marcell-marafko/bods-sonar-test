# Prerequisites

Write prerequisite section describing the required tools.
E.g. Docker/Docker Compose, pipenv, npm, Black, etc.

## Installation

### Step 1: Configure /etc/hosts

The Django app serves multiple sites on different subdomains. In order
to emulate this in development, add to `/etc/hosts`:

```sh
127.0.0.1 www.bods.local data.bods.local publish.bods.local admin.bods.local
```

and set `DJANGO_PARENT_HOST=bods.local` in your environment (see
Step 2 and Step 3).

`DJANGO_PARENT_HOST` must have at least one dot in it to make it a valid domain.
Otherwise, the browser will ignore cross-domain cookies, such as the sessionid
cookie - making it impossible to log in.

If you want to change `DJANGO_PARENT_HOST` after having already
`python manage.py migrate`, then you must edit the site records manually in the
`django_site` database table. Update the domains as necessary, e.g:

```sh
1 www.bods.local Bus Open Data Service
2 data.bods.local Find Open Data Service
3 publish.bods.local Publish Open Data Service
4 admin.bods.local Bus Open Data Service (Internal)
```

After to have made these changes running `docker-compose up`
will launch all the services. After a few minutes, you should be able to access
[www.bods.local:8000](www.bods.local:8000).

### Step 2: Set up Docker Compose

Environment configuration when using Docker Compose is achieved using a `.env`
file that is passed to the docker containers. A template for the `.env` file is
provided in the repository (`.env.local.template`).

First copy the `.env.local.template` file to `.env`.

```sh
# assuming you're in the bodp-django root directory
cp .env.local.template .env
```

The only change we need to make to the `.env` file is to set the UID and GID
variables to your user's UID/GID. These can be found as follows;

```sh
$ id -u
1001

$ id -g
1001
```

Setting these variables ensures that any files created by Django running in the
container are owned by your system user.

Remember to set `DQS_URL`.

### Step 3: Local Development (Optional)

You may prefer to run the Django app outside of the Docker environment. This is
useful for a number of reasons, mainly that tests run quicker and that its
easier to debug since you don’t need to set up a remote interpreter.

#### Install Python 3.8.0

The project uses Python 3.8.0. As it’s unlikely that you have that exact version
installed on your system. We will use [pyenv](https://github.com/pyenv/pyenv)
to install specific versions of python.
An how-to on installing and configuring pyenv can be found here.

#### Install Pipenv

Once, you have the correct Python interpreter installed, you will need to install
`pipenv`. The project uses pipenv to manage its Python dependencies. It is
recommended to install `pipenv` via the system package manager so that the `pipenv`
executable is installed system-wide and thus more readily available to your IDE.

Follow the installation instructions to set it up. E.g. on Fedora:

```sh
sudo dnf install pipenv
```

Alternatively, if you have [pipx](https://github.com/pipxproject/pipx) installed,
`pipenv` can be installed globally using `pipx install pipenv`.

#### Create a virtualenv

Before you use `pipenv` to install the project’s dependencies, you should
create a virtual environment based on the Python 3.8.0 interpreter, to isolate
the project’s dependencies from other projects that share that interpreter.

For this step to work, you should have installed pyenv via the pyenv-installer
in the previous step which will automatically install the virtualenv plugin.

Create a virtualenv for the project using:

```sh
pyenv virtualenv 3.8.0 bods
```

You can then activate the virtualenv:

```sh
pyenv activate bods
```

#### Install Python Packages

With the virtualenv activated in your terminal, install Python packages:

```sh
pipenv install --dev
```

#### Install Javascript packages

To install the javascript/frontend dependencies Node and npm need to be
installed on your system. You can find out how to install Node and `npm` here.

We use gulp as the build system for the frontend, the gulp-cli needs to be
installed globally.

```sh
npm install -g gulp-cli
```

Once installed the project dependencies can be installed using npm. This project
contains 2 `package.json` files. One in the project root directory and one in the
frontend directory.

```sh
# gulp-sass depends on libsass
dnf install proj-devel libsass-devel

# install root node modules
cd bodp-django
npm install .

# install the frontend nod modules
cd frontend
npm install .
npm start build
```

This will create a `node_modules` directory in the BODS root directory and the
frontend directory.

There are a few steps that need to be followed to ensure that a non-docker
environment can connect to the dockerized services.

Create a new `.env.nodocker` environments file using the `.env.nodocker.template`

```sh
cp .env.nodocker.template .env.nodocker
```

Before starting the development server we need to set a few environment variables
to let the Django process know it’s running outside of Docker;

```sh
DJANGO_ENV_FILE=.env.nodocker
DJANGO_READ_DOT_ENV_FILE=True
```

Install the dev dependencies to your virtual environment and run the Django
`manage.py` commands;

```sh
pipenv install --dev
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py runserver
```

Run the unit tests with coverage and HTML coverage report;

```sh
coverage run -m pytest
coverage report
coverage html
```

### Frontend Development

Gulp can automatically rebuild the frontend when changes are made, this can be
run concurrently with the Django development server using npm

```sh
# when in the project root directory
npm start
```
