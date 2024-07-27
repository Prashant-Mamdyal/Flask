# Flask
Developing a RESTful API for a Supply Chain Management System using Flask-restx with MySQL database using Sqlalchemy.

1. First Clone this project from git to your local repositary using "git clone https://github.com/Prashant-Mamdyal/Flask.git" using HTTPS
                                                                 or "git clone git@github.com:Prashant-Mamdyal/Flask.git" using SSH

2. after that create virtual environment using this command on terminal "python -m venv env"       (Note: env is your virtual enviroment name)

3. activate your virtual environment using this command on terminal ".\env\Scripts\activate" 

4. after virtual environment is activated, install all the requirement to run the application using this command on terminal "pip install -r requirement.txt"

5. inside "app" folder in "__init__.py" change the databse configuration 
    db.config['SQLALCHEMY_DATABASE_URI']='mysql://username:password@localhost/db_name'
    according to your database settings.

6. after installing all the requirments use "flask run" command on terminal to run the application.

7. to run test cases use this command or terminal "python -m unittest discover -s app/tests"