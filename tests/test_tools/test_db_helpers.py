'''Test the db_helpers module'''

import peewee
import pytest

from pyhetdex.tools import db_helpers

sqlite3 = pytest.importorskip('sqlite3')

parametrize = pytest.mark.parametrize


@parametrize('in_file', [True, False])
@parametrize('action', (lambda: True, lambda: [][0]))
def test_sqlite_connector(request, in_file, action):
    '''Test the connection to the database'''
    if in_file:
        tmpdir = request.getfixturevalue('tmpdir')
        location = tmpdir.join('test.db').strpath
    else:
        location = ':memory:'

    database = peewee.SqliteDatabase(location)
    connect = db_helpers.SQLiteConnector(database)

    assert database.is_closed()

    try:
        with connect():
            assert not database.is_closed()
            action()
    except IndexError:
        # I don't care about the exception, I just want to make sure that the
        # database is properly handled
        pass

    assert database.is_closed() == in_file


def test_max_sqlite():
    assert db_helpers.SQLITE_MAX_VARIABLE_NUMBER > 0


@parametrize('high, max_vars', [(42, 1000), (1000, 100)])
def test_max_sqlite_branches(monkeypatch, high, max_vars):
    '''Make sure that when hitting the high and low limits all is nice and
    fine'''
    def __query(_, n_args):
        if n_args > max_vars:
            raise sqlite3.OperationalError('test')
    monkeypatch.setattr(db_helpers, '_query', __query)

    n_var = db_helpers.max_sqlite_variables(high=high)

    assert n_var == min([high, max_vars])
