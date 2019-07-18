# FileUp (TechTeam Assignment)
## Installing 
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
* Share folders/files with groups or individuals
* Register users and manage user groups (admin side)
* Manage user preferences
* Recycle Bin lifetime
* Auto emails on certain events (Sharing file with a user/group)
* Many more...