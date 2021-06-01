# 分页函数

`brise`提供`brise.ext.check_header`函数来进行数据库数据的分页操作。

## 函数签名
```
async def paginate(db_object, query, page=1, paginate_by=10) -> count,data
```
###  参数
`db_object`：  peewee_async.Managerd对象

`query`: peewee.ModelSelect对象

`page`：页码，从第一页开始

`paginate_by`:每页显示的条数

### 返回值
`count`:个数

`data`：查询出来的数据列表