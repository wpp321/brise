import peewee_async

database = peewee_async.MySQLDatabase(None)
session_conn = None
session_expire = 3600
