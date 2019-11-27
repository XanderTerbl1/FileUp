# FileUp
## Requirements
* python 3.6+ installed (Different 3.XX versions can be used - but the installation commands may differ)

## Deploying/Installing to Localhost
(Please note, this installation is tailored for Windows machines (ps).  Linux/Mac commands might differ, but the process stays the same)

( python => python3 || py3)

1. Download the zip
2. Create and launch a new virtual environment: 
```
python -m venv venv  
venv/Scripts/activate.ps1
```
3. Install all the packages in requirements.txt
```
pip install -r requirements.txt
```
4. Make and apply the app migrations
```
python manage.py makemigrations  
python manage.py migrate
```
5. Collect Static Files
```
python manage.py collectstatic
```
6. Create a superuser (remember the username and password)
```
python manage.py createsuperuser
```
7. Run the app
```
python manage.py runserver
```
## Features
* My Files, Shared Files, Recycle Bin and Dashboard Views
* Great User interface
* Upload Files (Drag&Drop/Browse).
* Create Folders
* Move, rename, delete, share or publish files/folders
* Download Folders (as ZIP)
* Download Files
* Share folders/files with groups or individuals
* Register users and manage user groups (admin side)
* Manage user preferences
* Recycle Bin lifetime
* Auto emails on certain events (Sharing file with a user/group)
* Many more...

## Screenshots
![My Files](Screenshots/1.PNG?raw=true "1")
![My Files](Screenshots/2.PNG?raw=true "1")
![Share](Screenshots/3.PNG?raw=true "1")
![Shared Files](Screenshots/4.PNG?raw=true "1")
![Recycle Bin](Screenshots/5.PNG?raw=true "1")
![Dashboard](Screenshots/6.PNG?raw=true "1")
![Admin](Screenshots/7.PNG?raw=true "1")
