# 防伪装饰器
`brise.ext.check_header`装饰器对http请求的请求头做了一些检查，以此来增强接口的安全性。
## 装饰器检查规则
1. 如果同一IP连续三次没有会话ID，则锁定IP一小时不能访问；
2. 如果有会话ID，最后请求时间和会话持续时间不正确（连续三次，锁定IP一小时不能访问）；
3. 当前会话请求IP与最后一次会话IP不一致，禁止业务处理；
## 使用
`check_header`装饰器只能用在`SessionHandler`和`LogSessionHandler`中，放在要进行安全检查的接口函数上（如果接口函数上有多个装饰，放到最外面）。下面为**斐波那契数列**例子添加防伪装饰器的代码。
```
@api.add_route("/gen")
class Gen(LogSessionHandler):
    @check_header
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
## 调用者注意
调用者除在请求头上添加`x-token`字段外，还需要添加`x-time`字段。调用者在拿到`x-token`的时候，需要记录拿到token的时间，以后每次使用这个token需要带上`x-time`这个请求头。`x-time`的值为第一次拿到`x-token`经过的秒数。防伪装饰器会校验这个值，如果秒数与服务器记录的时间不一致（相差超过10秒）超过3次，则此ip将被锁定一小时。
