@ECHO off
python -m venv venv
venv/Scripts/activate.ps1
pip install -r requirements.txt
python manage.py makemigrations  
python manage.py migrate
python manage.py collectstatic
PAUSE