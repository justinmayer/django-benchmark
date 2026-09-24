# Getting started

Create migrations.

```
python manage.py makemigrations
python manage.py migrate
```

Initialize database.

```
python manage.py shell

>>> from tickets.fixtures import create_data
>>> create_data()
``` 
