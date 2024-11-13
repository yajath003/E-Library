E - L i b r a r y

**This is a platform to manage books**
• By adding new book
• By deleting existing books
• Revoking access to a book 
• Returning a book in time

After cloning the project using **git clone** command the libraries required to run the file can be installed using the command 
**pip install -r requirements.txt**

**This application is divided into 5 main modules, created using python.**
• Librarian              • User
• Books                  • Section
• intro

Each module has the following 4 python files:
• __init__               • models
• forms                  • views

**__init__:**
__init__ is a built-in method that initializes a newly created object from a class.

**models:**
models contain all the tables that are present in the database.
They can be modified, updated using the following commands:
• flask --app main.py db init
• flask --app main.py db migrate
• flask --app main.py db upgrade
this is associated with flask_migrations

**forms:**
forms contains all the input validations of the application

**views:**
views store all the connecting route of the application along with all the logics accociated with each page of the application


