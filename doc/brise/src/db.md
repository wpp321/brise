#  数据库操作

```
from brise.server import Server
from brise.blueprint import Blueprint
from brise.ext import RequestHandler, TrueResponse, FalseResponse
from peewee import *
import peewee_async

database = peewee_async.MySQLDatabase('xxx', **{'charset': 'utf8', 'sql_mode': 'PIPES_AS_CONCAT', 'use_unicode': True,
                                                'host': 'xxx', 'port': 3306, 'user': 'root',
                                                'password': 'xxx'})


class UnknownField(object):
    def __init__(self, *_, **__): pass


class BaseModel(Model):
    class Meta:
        database = database


class User(BaseModel):
    age = IntegerField()
    name = CharField(primary_key=True)

    class Meta:
        table_name = 'user'


db_object = peewee_async.Manager(database)

blueprint = Blueprint()


@blueprint.add_route("/")  # 添加此handler到蓝图中，路径为/
class DbHandler(RequestHandler):
    async def get(self):  # get请求
        name = self.get_argument("name")
        if not name:
            return self.write(FalseResponse("参数不全"))
        try:
            user = await db_object.get(User, name=name)
            self.write(TrueResponse(age=user.age))
        except:
            self.write(FalseResponse("用户不存在"))

    async def post(self):  # post请求
        name = self.get_json_arg("name")
        age = self.get_json_arg("age")
        if not all([name, age]):
            return self.write(FalseResponse("参数不全"))
        try:
            await db_object.create(User, name=name, age=age)
            self.write(TrueResponse())
        except:
            self.write(FalseResponse("添加失败"))

    async def put(self):  # put请求
        name = self.get_json_arg("name")
        age = self.get_json_arg("age")
        if not all([name, age]):
            return self.write(FalseResponse("参数不全"))
        try:
            user = User(name=name, age=age)
            await db_object.update(user)
            self.write(TrueResponse())
        except:
            self.write(FalseResponse("修改失败"))

    async def delete(self):  # delete请求
        name = self.get_json_arg("name")
        if not name:
            return self.write(FalseResponse("参数不全"))
        try:
            user = User(name=name)
            await db_object.delete(user)
            self.write(TrueResponse())
        except:
            self.write(FalseResponse())


if __name__ == '__main__':
    server = Server()  # 创建server
    server.register_blueprint(blueprint)  # 注册蓝图
    server.run()  # 运行server
```
相关类库参考[peewee](http://docs.peewee-orm.com/en/latest/)、[peewee_async](https://peewee-async.readthedocs.io/en/latest/)