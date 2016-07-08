# Dance Cat
-----------

[![Code Health](https://landscape.io/github/scattm/DanceCat/master/landscape.svg?style=flat)](https://landscape.io/github/scattm/DanceCat/master)

#### Installation

Download and install mysql-connector-python [here](https://dev.mysql.com/downloads/connector/python/). My version is 2.1.3.
```
tar zvfx mysql-connector-python-2.1.3.tar.gz
cd mysql-connector-python-2.1.3
python setup.py install
```

Install the rest of requirements. Then run `webpack` to package frontend things.
```
virtualenv /path/to/your/virtualenv
source /path/to/your/virtualenv/bin/activate
pip install -r requirement.txt
npm install
bower install
webpack
```

#### DB

Setup DB using python console.

`cp config.cfg.dist /path/to/your/config.cfg`

Update `config.cfg` file that suite your needs. Then setup DB using python console:
```
source /path/to/your/virtualenv/bin/activate
export CONFIG_FILE=</path/to/config/file>
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

Copy main python file and update it.

`cp DanceCat.py.dist DanceCat.py`

Export environment variable and then run local web server. You can use the start.sh.dist as reference.
```
source /path/to/your/virtualenv/bin/activate
python DanceCat.py
```
