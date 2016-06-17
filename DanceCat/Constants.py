# Project section
PROJECT_NAME = 'Dance Cat - Data Report'
# DB section
MYSQL = 1
SQLSERVER = 2

DB_DEFAULT_PORT = {
    MYSQL: 3306,
    SQLSERVER: 1433
}

CONNECTION_TYPES_LIST = [
    (MYSQL, 'MySQL'),
    (SQLSERVER, 'SQL Server')
]

CONNECTION_TYPES_DICT = {
    MYSQL: {
        'name': 'MySQL',
        'default_port': 3306
    },
    SQLSERVER: {
        'name': 'SQL Server',
        'default_port': 1433
    }
}
