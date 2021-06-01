# Hello World

## 导入所需python包

```
from brise.server import Server
from brise.blueprint import Blueprint
from brise.ext import RequestHandler
```

## 定义蓝图

```
blueprint = Blueprint()
```

##  创建RequestHandler

```
@blueprint.add_route("/")  # 添加此handler到蓝图中，路径为/
class HelloWorld(RequestHandler):
    def get(self):  
        self.write("Hello World")
```

## 启动server

```
server = Server()  # 创建server
server.register_blueprint(blueprint)  # 注册蓝图
server.run()  # 运行server
```

## 完整代码

```
from brise.server import Server
from brise.blueprint import Blueprint
from brise.ext import RequestHandler

blueprint = Blueprint()


@blueprint.add_route("/")  # 添加此handler到蓝图中，路径为/
class HelloWorld(RequestHandler):
    def get(self): 
        self.write("Hello World")


if __name__ == '__main__':
    server = Server()  # 创建server
    server.register_blueprint(blueprint)  # 注册蓝图
    server.run()  # 运行server
```

运行脚本后打开浏览器输入http://127.0.0.1:8080/ 就可以看见hello world页面。