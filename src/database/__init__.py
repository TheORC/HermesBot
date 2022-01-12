from .databasemanager import (DatabaseManager,
                              DatabaseQuery,
                              DatabaseUpdate)

_DATABASE_HOLDER = {'db': None}


def connect_database(bot):
    if _DATABASE_HOLDER['db'] is None:
        _DATABASE_HOLDER['db'] = DatabaseManager(bot.loop)
    else:
        raise Exception(
              'Database has already been initalized.  This can only be done once!')  # noqa


def hermes_database():
    if _DATABASE_HOLDER['db'] is None:
        raise Exception(
              'Database has not been initalized but you are trying to use it!')
    return _DATABASE_HOLDER['db']


__all__ = [
    # Classes
    'DatabaseManager', 'DatabaseQuery', 'DatabaseUpdate',

    # Methods
    'connect_database', 'hermes_database'
]
