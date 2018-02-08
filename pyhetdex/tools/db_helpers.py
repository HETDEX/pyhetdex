'''Database utilities, mostly SQLite3'''


class SQLiteConnector(object):
    '''Context manager to open and close the database connection.

    Returns the current connection when using the instance in a :keyword:`with`
    statement.

    Examples
    --------
    >>> import peewee
    >>> database = peewee.SqliteDatabase(':memory:')
    >>> connect = SQLiteConnector(database)
    >>> # the following takes care of opening and closing the connection for
    >>> # you, unless the database is on memory
    >>> with connect:
    ...     pass
    >>> # this is equivalent, use the form you are more comfortable with
    >>> with connect():
    ...     pass
    >>> # the connection is returned (which has also the advantage to connect
    >>> # in the case of a in memory database)
    >>> with connect() as ctx_conn:
    ...     pass

    Parameters
    ----------
    database : object
        object that represent a database connection and that has the following
        attributes and methods: :attr:`database.database`,
        :meth:`database.connect`, :meth:`database.close` and either
        :meth:`database.connection` or :meth:`database.get_conn`
    keep_open : string, optional
        if :attr:`database.database` is equal to ``keep_open``, the database is
        not opened nor closed. In SQLite3 is useful for in memory databases,
        that are removed when closed
    '''
    def __init__(self, database, keep_open=':memory:'):
        self._database = database
        self._keep_open = keep_open

    def __call__(self):
        '''Make the object look like a function (backward compatibility
        mostly)'''
        return self

    def __enter__(self):
        if self._database.database != self._keep_open:
            self._database.connect()

        try:
            connection = self._database.connection()
        except AttributeError:
            # peewee < 3 the attribute is called get_conn
            connection = self._database.get_conn()
        return connection

    def __exit__(self, exc_type, exc_value, traceback):
        if self._database.database != self._keep_open:
            self._database.close()


def max_sqlite_variables(high=100000):
    """Get the maximum number of arguments allowed in a query by the current
    sqlite3 implementation. Based on `this question
    <http://stackoverflow.com/questions/17872665/determine-maximum-number-of-columns-from-sqlite3>`_

    Parameters
    ----------
    high : int, optional
        maximum number of arguments to test. The number seems a reasonable
        compromise between execution speed for this function and number of
        parameters.

    Returns
    -------
    int
        inferred SQLITE_MAX_VARIABLE_NUMBER
    """
    import sqlite3
    db = sqlite3.connect(':memory:')
    cur = db.cursor()
    cur.execute('CREATE TABLE t (test)')
    low = 0

    # if high is allowed, simply returns it
    try:
        _query(cur, high)
    except Exception:
        # I know is bad, but whatever exception will be caught and dealt with
        # in the while loop
        pass
    else:
        return high

    while low < high - 1:
        guess = (high + low) // 2
        try:
            _query(cur, guess)
        except sqlite3.OperationalError as e:
            high = guess
        else:
            low = guess
    cur.close()
    db.close()
    return low


def _query(cursor, n_args):
    """Create a query with n_args and execute it"""
    query = 'INSERT INTO t VALUES ' + ','.join(['(?)' for _ in
                                                range(n_args)])
    args = [str(i) for i in range(n_args)]
    cursor.execute(query, args)


SQLITE_MAX_VARIABLE_NUMBER = max_sqlite_variables()
