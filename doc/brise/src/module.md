# 创建项目及模块
## brise命令使用
`brise`命令包含四种用法

+ `brise new` 创建项目
+ `brise add` 添加模块
+ `brise pack` 打包模块
+ `brise password-enc` 用于加密日志mysql、session redis密码
+ `brise fingerprint` 用于获取硬件指纹信息
## 示例
创建一个名称为`demo`的项目，并添加一个名称为`demo`的模块
```
brise new project_demo
cd project_demo/
brise add module_demo
```
生成的文件结构如下
```
project_demo/
├── apps
├── main.py
├── module_demo
│   ├── handlers.py
│   ├── __init__.py
│   └── param_schemas.py
├── plugins
└── setting.py
```
## 文件描述

### main.py
项目启动文件，启动项目执行此文件，一般不用修改。
### apps
模块文件夹。打包好的模块放在这里，程序启动时会自动加载apps目录下以`.mod`结尾的文件。
### plugins
插件文件夹。打包好的插件放在这里，程序启动时会自动加载plugins目录下以`.mod`结尾的文件。
### setting.py
项目配置文件，可根据需要修改。配置如下：
####  modules
该项配置项目所有的模块，需要添加模块运行`brise add`命令后，开发的时候把模块名添加到这里即可。
#### log_mysql
该项为项目日志数据库的配置。如果使用`brise`提供的`LogSessionHandler`或`LogHandler`时，需要配置此项，配置示例如下：
```
log_mysql = {
    'host': "127.0.0.1", # mysql数据库ip
    'user': "root", # mysql 用户名
    'password': "iFaqPeUv1RSk1vkxOc3KnQ==", # 密码
    'database': "log", # 数据库名称
    "charset": "utf8", # 字符编码
    "table_name":None # 日志表名称，默认为request_log
}
```
> password 的内容为原密码经brise加密后的内容。加密方法为使用 brise password-enc 命令进行加密。假如原密码为123456，则执行命令 `brise password-enc 123456`，则会打印出字符串`iFaqPeUv1RSk1vkxOc3KnQ==`，填入`iFaqPeUv1RSk1vkxOc3KnQ==`即可。
#### session_redis
`brise`默认的session实现使用redis做数据存储，该项为session的redis地址。如果使用`brise`提供的`SessionHandler`、` LogSessionHandler`时，需要配置此项，配置示例如下：
```
session_redis = {
    "host": "127.0.0.1",#redis ip
    "port": 6379,# redis 端口
    "db": 0,# redis数据库号
    "password": None #密码
}
```
> redis没有密码则填入`None`，如果有密码则填入加密后的密码，参考`log_mysql`密码加密
#### session_expire
该项为项目session的默认超时时间，单位为秒。另外`SessionHandler`提供`set_session_expire`方法在代码中设置session超时时间。
#### port
项目监听的端口，默认8080

#### project_url
项目url前缀。

### __init__.py
模块标识文件，这个文件中创建了一个`Blueprint`来创建模块路由。`Blueprint`类构造函数有两个参数。第一个`url_prefix`为模块的根路径，使用`brise`命令生成模块时，默认以模块名为根路径。第二个参数`allow_ip`为模块限制访问ip，默认`*`表示任意ip都可以访问该模块，多个ip用逗号隔开。`api = Blueprint("/test", "127.0.0.1,192.168.1.2")`表示创建一个根路径为`/test`，允许访问ip为`127.0.0.1`和`192.168.1.2`的模块路由。
### handlers.py
`handlers.py` 为模块放`RequestHandler`的地方，主要的业务逻辑放在这里。
> 如果业务代码非常多，可以把业务代码拆成多个文件，使用时注意在模块`__init__.py`后面导入相应的`RequestHandler`即可。如下代码所示：
> ```
> from brise.blueprint import Blueprint
> api = Blueprint("/")
> from bussiness1_handlers import a_handler, b_handler
> from bussiness2_handlers import c_handler
> ```

### param_schemas.py
`param_schemas.py`为模块放校验参数的地方。`brise`提供`params_validate`函数校验json格式参数。参数校验采用`json schema`来进行格式匹配。`json schema`的用法可参考[json schema](http://json-schema.org/)。

## 部署
### 源代码部署
把相应的模块文件夹放到项目根目录里，同时把模块名称添加到`setting` `modules`配置项上。
### 打包部署
使用`brise pack`命令打包相应模块，会在target文件夹下生成相应的`.mod`文件，把此文件放到apps目录里，程序启动时会自动加载，用这种方法部署`setting` `modules`不需要配置相应的module，之前配置的需要删除掉。
