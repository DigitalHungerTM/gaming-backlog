# Gaming Backlog

A simple web application written with Flask. It uses the Flask-SQLAlchemy for ORM, Flask-WTF for forms and
Bootstrap-Flask for styling. As this is a small project nothing more than an sqlite database is required.

## Project layout

- `backlog_app`: This is where the magic happens
- `instance`: This is the location of the sqlite database (aptly called `db.sqlite`) (will be created if it doesn't
  exist)
- `tools`: Some scripts for running / debugging the application

## Starting the application

```shell
source .venv/bin/activate
flask --app backlog_app run [--debug]
```