"""
Docstring for DanceCat.DatabaseConnector module.

This module contain DatabaseConnector and DatabaseConnectorException class
which is used to wrap different DBMS Connector drivers.
"""

import traceback
import re
import pymssql
import mysql.connector
from . import Constants
from . import Helpers


class DatabaseConnector(object):
    """
    DatabaseConnector class.

    DatabaseConnector will be use to wrap around
    other DBMS Connector drivers to different DBMS.
    """

    def __init__(self, connection_type, config, **kwargs):
        """
        Constructor for DatabaseConnector class.

        :param connection_type:
            Connection type which is defined in Constant module.
            This value will allow DatabaseConnector to choose the
            right driver for the connection.
        :param config:
            The dictionary config that will be passed to the drivers
            connect function.
        :param kwargs:
            Keyword argument which will allow to control the class's
            behaviour.
                sql_data_type: return data in SQL data style or not.
                hide_password: hide password field in the result or not.
                dict_format: return data rows in dictionary or tuple format.
                timeout: default timeout for the connection.
        """
        self.type = connection_type
        self.config = config
        self.is_sql_data_type = kwargs.get('sql_data_style', False)
        self.is_hiding_password = kwargs.get('hide_password', True)
        self.is_return_dict = kwargs.get('dict_format', False)
        self.timeout = kwargs.get('timeout', 60)

        self.connection = None
        self.cursor = None

        self.columns_name = ()
        self.ignore_position = []

    def connect(self, timeout=None):
        """
        Connect to the Database via the right driver.

        :param timeout:
            Default timeout to be passed to the new connection.
        :return: raise DatabaseConnectorException on failed.
        """
        try:
            if self.type == Constants.MYSQL:
                self.config['connection_timeout'] = \
                    self.timeout if timeout is None else timeout
                self.connection = mysql.connector.connect(**self.config)
            elif self.type == Constants.SQLSERVER:
                self.connection = pymssql.connect(**self.config)
        except Exception as exception:
            traceback.print_exc()
            raise DatabaseConnectorException(
                'Could not connect to the database.',
                self.type,
                trace_back=exception
            )

    def close(self):
        """Close connection or Raise DatabaseConnectorException on failed."""
        try:
            if self.type in [
                Constants.MYSQL, Constants.SQLSERVER
            ]:
                self.connection.close()
        except Exception as exception:
            traceback.print_exc()
            raise DatabaseConnectorException(
                'Could not close the connection.',
                self.type,
                trace_back=exception
            )

    def connection_test(self, timeout=None):
        """
        Test the connection.

        :param timeout:
            Passed this timeout setting to ignore
            the class's default timeout.
        :return: True if connection is established else False.
        """
        self.connect(timeout)
        self.close()
        return bool(self.connection)

    def execute(self, query):
        """Execute the given query. Return True on success."""
        try:
            if self.type == Constants.MYSQL:
                self.cursor = self.connection.cursor()
                self.cursor.execute(query)
                self.columns_name = self.cursor.column_names
                if self.is_hiding_password:
                    self._password_field_coordinator()

            elif self.type == Constants.SQLSERVER:
                self.cursor = self.connection.cursor()
                self.cursor.execute(query)

                # create columns' name tuple
                self.columns_name = ()
                for i in range(0, len(self.cursor.description)):
                    self.columns_name += (self.cursor.description[i][0],)
                if self.is_hiding_password:
                    self._password_field_coordinator()
        except Exception as exception:
            traceback.print_exc()
            raise DatabaseConnectorException(
                'Could not query "%s".' % query,
                self.type,
                trace_back=exception
            )
        else:
            return True

    def fetch(self):
        """Fetch single row of the result."""
        try:
            if self.type in [Constants.MYSQL, Constants.SQLSERVER]:
                data = self.cursor.fetchone()
                return self._convert_dict_one(data) \
                    if self.is_return_dict else self._tuple_process_one(data)
        except Exception as exception:
            traceback.print_exc()
            raise DatabaseConnectorException(
                'Could not fetch result(s).',
                self.type,
                trace_back=exception
            )

    def fetch_many(self, size=1):
        """Fetch given number of rows of the result."""
        try:
            if self.type in [Constants.MYSQL, Constants.SQLSERVER]:
                data = self.cursor.fetchmany(size)
                return self._convert_dict_many(data) \
                    if self.is_return_dict else self._tuple_process_many(data)
        except Exception as exception:
            traceback.print_exc()
            raise DatabaseConnectorException(
                'Could not fetch result(s).',
                self.type,
                trace_back=exception
            )

    def fetch_all(self):
        """Fetch all result rows."""
        try:
            if self.type in [Constants.MYSQL, Constants.SQLSERVER]:
                data = self.cursor.fetchall()
                return self._convert_dict_many(data) \
                    if self.is_return_dict else self._tuple_process_many(data)
        except Exception as exception:
            traceback.print_exc()
            raise DatabaseConnectorException(
                'Could not fetch result(s).',
                self.type,
                trace_back=exception
            )

    def _convert_dict_one(self, data_tuple):
        if len(self.columns_name) == 0:
            raise DatabaseConnectorException('Column(s) name is empty.', self.type)

        data_dict = {}

        for i in range(0, len(self.columns_name)):
            if i in self.ignore_position:
                continue
            data_dict[self.columns_name[i]] = \
                Helpers.py2sql_type_convert(data_tuple[i]) if self.is_sql_data_type \
                else data_tuple[i]

        return data_dict

    def _convert_dict_many(self, data_tuple_list):
        if len(self.columns_name) == 0:
            raise DatabaseConnectorException('Column(s) name is empty.', self.type)

        data_dict_list = []

        for i in range(0, len(data_tuple_list)):
            data_dict = {}

            for j in range(0, len(self.columns_name)):
                if j in self.ignore_position:
                    continue
                data_dict[self.columns_name[j]] = \
                    Helpers.py2sql_type_convert(data_tuple_list[i][j]) \
                    if self.is_sql_data_type else data_tuple_list[i][j]

            data_dict_list.append(data_dict)

        return data_dict_list

    def _tuple_process_one(self, data_tuple):
        new_data_tuple = ()

        for i in range(0, len(data_tuple)):
            if i in self.ignore_position:
                new_data_tuple += (None,)
                continue
            new_data_tuple += (
                Helpers.py2sql_type_convert(data_tuple[i])
                if self.is_sql_data_type else data_tuple[i],
            )

        return new_data_tuple

    def _tuple_process_many(self, data_tuple_list):
        new_data_tuple_list = []

        for i in range(0, len(data_tuple_list)):
            new_data_tuple_list.append(self._tuple_process_one(data_tuple_list[i]))

        return new_data_tuple_list

    def _password_field_coordinator(self):
        if len(self.columns_name) == 0:
            raise DatabaseConnectorException('Column(s) name is empty.', self.type)
        for i in range(0, len(self.columns_name)):
            if self.is_hiding_password:
                if re.search(
                        r'password|secret|userpass|confidential',
                        self.columns_name[i],
                        re.IGNORECASE
                ) is not None:
                    self.ignore_position.append(i)


class DatabaseConnectorException(Exception):
    """Use as a exception type of DatabaseConnector class."""

    def __init__(self, message, connection_type, trace_back=None):
        """
        Constructor for DatabaseConnectorException.

        :param message:
            Exception's message.
        :param connection_type:
            The connection type defined in Constant module.
        :param trace_back:
            Exception's trace back.
        """
        super(DatabaseConnectorException, self).__init__(message)

        self.connection_type = connection_type
        self.trace_back = trace_back
