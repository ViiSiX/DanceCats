"""Constant that will be used through throughout the application."""

# Project section
PROJECT_NAME = 'Dance Cat - Data Report'

# DB section
MYSQL = 1
SQLSERVER = 2

CONNECTION_TYPES_DICT = {
    MYSQL: {
        'name': 'MySQL',
        'default_port': 3306,
        'mime': 'text/x-mysql'
    },
    SQLSERVER: {
        'name': 'SQL Server',
        'default_port': 1433,
        'mime': 'text/x-mssql'
    }
}

CONNECTION_TYPES_LIST = [
    (
        MYSQL,
        CONNECTION_TYPES_DICT[MYSQL]['name']
    ),
    (
        SQLSERVER,
        CONNECTION_TYPES_DICT[SQLSERVER]['name']
    )
]

# Job Tracking section
JOB_QUEUED = 0
JOB_RUNNING = 1
JOB_RAN_SUCCESS = 2
JOB_RAN_FAILED = 3
JOB_RESULT_EXPIRED = 4

JOB_TRACKING_STATUSES_DICT = {
    JOB_QUEUED: {
        'name': 'Queued'
    },
    JOB_RUNNING: {
        'name': 'Running'
    },
    JOB_RAN_SUCCESS: {
        'name': 'Success'
    },
    JOB_RAN_FAILED: {
        'name': 'Failed'
    },
    JOB_RESULT_EXPIRED: {
        'name': 'Result Expired'
    }
}

# Job Type section
JOB_NONE = 0
JOB_QUERY = 1

JOB_TYPES_DICT = {
    JOB_NONE: {
        'name': 'No Job Type'
    },
    JOB_QUERY: {
        'name': 'Query Data Job'
    }
}

# Model versions section
MODEL_ALLOWED_EMAIL_VERSION = 1
MODEL_USER_VERSION = 1
MODEL_CONNECTION_VERSION = 1
MODEL_JOB_VERSION = 2
MODEL_SCHEDULE_VERSION = 2
MODEL_TRACK_JOB_RUN_VERSION = 1

# Schedule type section
SCHEDULE_ONCE = 0
SCHEDULE_HOURLY = 1
SCHEDULE_DAILY = 2
SCHEDULE_WEEKLY = 3
SCHEDULE_MONTHLY = 4

SCHEDULE_TYPES_DICT = {
    SCHEDULE_ONCE: {
        'name': 'Once'
    },
    SCHEDULE_HOURLY: {
        'name': 'Hourly'
    },
    SCHEDULE_DAILY: {
        'name': 'Daily'
    },
    SCHEDULE_WEEKLY: {
        'name': 'Weekly'
    },
    SCHEDULE_MONTHLY: {
        'name': 'Monthly'
    }
}

SCHEDULE_TYPES_LIST = [
    (
        SCHEDULE_ONCE,
        SCHEDULE_TYPES_DICT[SCHEDULE_ONCE]['name']
    ),
    (
        SCHEDULE_HOURLY,
        SCHEDULE_TYPES_DICT[SCHEDULE_HOURLY]['name']
    ),
    (
        SCHEDULE_DAILY,
        SCHEDULE_TYPES_DICT[SCHEDULE_DAILY]['name']
    ),
    (
        SCHEDULE_WEEKLY,
        SCHEDULE_TYPES_DICT[SCHEDULE_WEEKLY]['name']
    ),
    (
        SCHEDULE_MONTHLY,
        SCHEDULE_TYPES_DICT[SCHEDULE_MONTHLY]['name']
    )
]

# Socket Section
WS_QUERY_SEND = 'r_query'
WS_QUERY_RECEIVE = 's_query'
WS_TRACKERS_SEND = 's_trackers'
WS_TRACKERS_RECEIVE = 'r_trackers'
