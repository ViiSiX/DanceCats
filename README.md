# Dance Cat
-----------
#### Installation

Download and install mysql-connector-python [here](https://dev.mysql.com/downloads/connector/python/). My version is 2.1.3.
```
tar zvfx mysql-connector-python-2.1.3.tar.gz
cd mysql-connector-python-2.1.3
python setup.py install
```

Install the rest of requirements. Then run `webpack` to package frontend things.
```
pip install -r requirement.txt
npm install
bower install
webpack
```

#### DB

Setup DB using python console.

`cp config.py.dist config.py`

Update configs that suite your needs. Then setup DB using python console:
```
python
from DanceCat import db
db.create_all()
```

#### SSL

Generate new key using openssl
```
openssl genrsa 1024 > ssl.key
openssl req -new -x509 -nodes -sha1 -days 365 -key ssl.key > ssl.cert
```

#### Run

Copy main python file

`cp DanceCat.py.dist DanceCat.py`

Run local web server.

`python DanceCat.py`
