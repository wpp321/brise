# 斐波那契数列

这一节以斐波那契数列接口例子来介绍`brise`提供的创建module、记录日志、session等功能。
## 创建项目及模块
```
brise new demo
cd demo
brise add fib
```
创建完毕后，修改`setting` 中的`modules`，把`fib`模块添加上去，如下：
```
modules = ["fib"]
```
## 例子说明
这里写一个接口，参数为`action`，假如`action`的值为`next`，则返回一个斐波那契数，如果`action`的值为`over`，则结束此斐波那契数列。
## 添加接口
在`handlers.py`中添加如下代码，则创建一个路径为`/fib/gen`的接口。
```
from brise.ext import SessionHandler


@api.add_route("/gen")
class GenHandler(SessionHandler):
    def post(self):
        pass
```
这里使用`brise`提供的`SessionHandler`用以留存斐波那契数列的最近的值,使用`SessionHandler`需要配置`setting` 中的`session_redis`。
## 参数校验
接口有一个参数`action`为必须参数，需要校验。向`param_schemas.py`添加如下代码，用以作接口参数校验。
```
schema_fib = {
    "type": "object",
    "required": ["action"],
    "properties": {
        "action": {
            "type": "string",
            "pattern": "next|over"
        }
    }
}
```
使用`params_validate`装饰器将`schema_fib`添加到接口函数上。
```
from brise.ext import SessionHandler, params_validate
from .param_schemas import schema_fib


@api.add_route("/gen")
class Gen(SessionHandler):
    @params_validate(schema_fib)
    def post(self):
        pass
```
执行`main.py`，发送非法请求到该接口，则会提示参数校验失败。
```
curl --location --request POST 'http://127.0.0.1:8080/fib/gen' \
--header 'Content-Type: application/json' \
--data '{
    "action":""
}'
{"code": 0, "msg": "参数校验失败：'' does not match 'next|over'!"}  
```
## 添加业务逻辑
添加接口的业务代码。
```
from . import api
from brise.ext import SessionHandler, params_validate, TrueResponse
from .param_schemas import schema_fib


@api.add_route("/gen")
class Gen(SessionHandler):
    @params_validate(schema_fib)
    def post(self):
        action = self.get_json_arg("action")
        if action == "next":
            before_last = self.session.get("before_last", 0)
            last = self.session.get("last", 0)
            num = max(1, before_last + last)
            self.session["before_last"] = last
            self.session["last"] = num
            self.write(TrueResponse(num=num))
        else:
            self.clear_session()  # 清除session
            self.write(TrueResponse())
```
现在斐波那契的例子已经完成了，运行`main.py`文件，就可以调用接口。第一次调用接口，返回的`response header`会有`x-token`一项，`x-token`用来标识会话，以后调用接口时，请求`request header`要带上这个`x-token`，否则将开启新的会话。
## 加入日志记录
`brise`提供日志记录功能，可以把接口调用的信息存入mysql中。比如在这个例子中，把`SessionHandler`换成`LogSessionHandler`就可以了，同时注意把`setting log_mysql`配置项修改成要存日志的数据库，日志会存到相应的数据库表中。