# 插件

`brise` 提供插件化开发方式，来方便不同的模块间共用组件，下面以一个例子，介绍如何创建及使用插件。

## 创建插件
`brise`的插件其实是一个python包，插件提供的功能写在模块`__init_.py`里面。比创建一个名叫`system_plug`的组件，可以先创建一个`system_plug`的python包，包结构如下：

```
system_plug/
└── __init__.py
```

在`__init__.py`文件里加如下代码
```
def print_hello():
    print("hello world")
```
使用 `brise pack system_plug`命令即可把`system_plug`打包为插件。
## 使用插件
把打包好的`system_plug.mod`文件放在`plugins`目录下，然后在代码中导入插件。
```
from brise.plugins import system_plug
```
调用`system_plug.print_hello()`即可打印出`hello world`字符串。

