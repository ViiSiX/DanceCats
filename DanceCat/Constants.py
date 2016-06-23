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

# Job Tracking section
JOB_RUN_SUCCESS = 1
JOB_RUN_FAILED = 2

# Model versions section
MODEL_ALLOWED_EMAIL_VERSION = 1
MODEL_USER_VERSION = 1
MODEL_CONNECTION_VERSION = 1
MODEL_JOB_VERSION = 1
MODEL_SCHEDULE_VERSION = 1
MODEL_TRACK_JOB_RUN_VERSION = 1

# Schedule type
SCHEDULE_ONCE = 0
SCHEDULE_HOURLY = 1
SCHEDULE_DAILY = 2
SCHEDULE_WEEKLY = 3
SCHEDULE_MONTHLY = 4
