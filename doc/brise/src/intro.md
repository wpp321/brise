# 介绍
Tornado 是一个Python web框架和异步网络库，起初由 FriendFeed 开发. 通过使用非阻塞网络I/O， Tornado可以支撑上万级的连接，处理 长连接, WebSockets ，和其他需要与每个用户保持长久连接的应用。

Tornado官方没有提供模块化的方案。`brise`是对`tornado`简单封装，提供一个简单的模块化方案，并提供了日志、会话、参数校验等常用的功能。

