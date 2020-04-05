# PWP SPRING 2020
# PandaBoard API
# Group information
* Student 1. Tatu Laakso tatu.laakso@student.oulu.fi
* Student 2. Jani Jarkima jani.jarkima@student.oulu.fi
* Student 3. Akseli Tyvelä akseli.tyvela@student.oulu.fi


# Getting Started with virtual environment
1. in your CMD create a folder for your virtual environment by running: `python -m venv /path/to/the/virtualenvironment` 
2. Download requirements.txt file from this repository and place it inside the virtual environment folder
3. In your CMD run a command: `virtualenvironment"\Scripts\activate.bat` 
4. In your CMD navigate to your created folder and run command: `pip install -r requirements.txt` 
 

# Libraries used
**All libraries can be found and installed from the requirements.txt**
* flask
* flask-sqlalchemy
* json
* mason-builder
* pytest
* pytest-cov
* ipython
* pysqlite3


# Running the tests
The resource test file is based on a resource_test that can be found at lovelace.
tests can be run with a cmd command: 
* `pytest --cov-report term-missing --cov=app` 
inside your virtual environment folder
