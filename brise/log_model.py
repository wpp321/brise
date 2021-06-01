from peewee import *
import peewee_async
import datetime
from . import tor_mod_vars


class UnknownField(object):
    def __init__(self, *_, **__): pass


class BaseModel(Model):
    class Meta:
        database = tor_mod_vars.database


class RequestLog(BaseModel):
    create_time = DateTimeField(index=True, default=datetime.datetime.now)  # 创建时间
    err = TextField(null=True)  # 错误
    log_id = CharField(primary_key=True)  # 日志id
    ip = CharField()  # ip
    req_data = TextField(null=True)  # 请求数据
    request_time = FloatField()  # 请求时间 单位ms
    resp_data = TextField(null=True)  # 返回数据
    uri = CharField()  # 请求地址

    class Meta:
        table_name = 'request_log'


objects = peewee_async.Manager(tor_mod_vars.database)
