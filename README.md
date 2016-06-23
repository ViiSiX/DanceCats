#### Installation

Download and install mysql-connector-python [here](https://dev.mysql.com/downloads/connector/python/). My version is 2.1.3.
```
tar zvfx mysql-connector-python-2.1.3.tar.gz
cd mysql-connector-python-2.1.3
python setup.py install
```

Install the rest of requirements.
```
pip install -r requirement.txt
npm install
bower install
```

Setup DB using python console.

`cp config.py.dist config.py`

Update configs that suite your needs. Then setup DB using python console:
```
python
from DanceCat import db
db.create_all()
```

Run local web server.

`python DanceCat.py`

If you want to run it on your server, please using uWSGI and nginx.
