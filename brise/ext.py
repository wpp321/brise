import tornado.web
from .log_model import objects, RequestLog
import uuid
from typing import List, Optional, Union
from tornado.web import HTTPError, _has_stream_request_body
from tornado.concurrent import Future, future_set_result_unless_cancelled
from tornado import iostream
from tornado.log import app_log
from traceback import TracebackException
import sys

import copy
import tornado.ioloop

import json
from jsonschema import validate, ValidationError
from . import tor_mod_vars
import datetime
import asyncio
import decimal


def error_wrap(func):
    async def inner(self, *args, **kwargs):
        try:
            result = func(self, *args, **kwargs)
            if result is not None:
                await result
        except Exception as e:
            etype, value, tb = sys.exc_info()
            err = ''
            for line in TracebackException(type(value), value, tb, limit=None).format(chain=True):
                err += line
            app_log.error(err)

    return inner


class RequestHandler(tornado.web.RequestHandler):

    def get_ip(self):
        x_real_ip = self.request.headers.get("X-Real-IP")
        remote_ip = x_real_ip or self.request.remote_ip
        return remote_ip

    def options(self, *args, **kwargs):
        pass

    # 跨域
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', 'content-type,x-token,x-time,sign')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS,DELETE,PUT')
        self.set_header("Access-Control-Expose-Headers", 'content-type,x-token,x-time,sign')

    def get_json_arg(self, key):
        try:
            if not hasattr(self, "json_body"):
                self.json_body = json.loads(self.request.body.decode())
            return self.json_body.get(key)
        except:
            return None


class LogHandler(RequestHandler):

    async def write_request_log(self, err=None):
        if self.request.method.capitalize() == "OPTIONS":
            return
        try:
            uri = self.request.uri
            try:
                req_data = self.request.body.decode()
            except:
                req_data = str(self.request.body_arguments)
            if hasattr(self, "_write_buffer_copy"):
                resp_data = (b"".join(self._write_buffer_copy)).decode()
            else:
                resp_data = (b"".join(self._write_buffer)).decode()
            ip = self.get_ip()
            request_time = 1000 * self.request.request_time()
            await objects.create(RequestLog, log_id=uuid.uuid4().hex, uri=uri, req_data=req_data, resp_data=resp_data,
                                 ip=ip,
                                 request_time=request_time, err=err)
        except:
            etype, value, tb = sys.exc_info()
            err = ''
            for line in TracebackException(type(value), value, tb, limit=None).format(chain=True):
                err += line
            app_log.error(err)

    async def _execute(
            self, transforms: List["OutputTransform"], *args: bytes, **kwargs: bytes
    ) -> None:
        """Executes this request with the given output transforms."""
        self._transforms = transforms
        try:
            if self.request.method not in self.SUPPORTED_METHODS:
                raise HTTPError(405)
            self.path_args = [self.decode_argument(arg) for arg in args]
            self.path_kwargs = dict(
                (k, self.decode_argument(v, name=k)) for (k, v) in kwargs.items()
            )
            # If XSRF cookies are turned on, reject form submissions without
            # the proper cookie
            if self.request.method not in (
                    "GET",
                    "HEAD",
                    "OPTIONS",
            ) and self.application.settings.get("xsrf_cookies"):
                self.check_xsrf_cookie()

            result = self.prepare()
            if result is not None:
                result = await result
            if self._prepared_future is not None:
                # Tell the Application we've finished with prepare()
                # and are ready for the body to arrive.
                future_set_result_unless_cancelled(self._prepared_future, None)
            if self._finished:
                return

            if _has_stream_request_body(self.__class__):
                # In streaming mode request.body is a Future that signals
                # the body has been completely received.  The Future has no
                # result; the data has been passed to self.data_received
                # instead.
                try:
                    await self.request._body_future
                except iostream.StreamClosedError:
                    return

            method = getattr(self, self.request.method.lower())
            result = method(*self.path_args, **self.path_kwargs)
            if result is not None:
                result = await result
            if self._auto_finish and not self._finished:
                self.finish()
        except Exception as e:
            etype, value, tb = sys.exc_info()
            err = ''
            for line in TracebackException(type(value), value, tb, limit=None).format(chain=True):
                err += line
            await self.write_request_log(err)
            try:
                self._handle_request_exception(e)
            except Exception:
                app_log.error("Exception in exception handler", exc_info=True)
            finally:
                # Unset result to avoid circular references
                result = None
            if self._prepared_future is not None and not self._prepared_future.done():
                # In case we failed before setting _prepared_future, do it
                # now (to unblock the HTTP server).  Note that this is not
                # in a finally block to avoid GC issues prior to Python 3.4.
                self._prepared_future.set_result(None)

    def finish(self, chunk: Optional[Union[str, bytes, dict]] = None) -> "Future[None]":
        if self._finished:
            raise RuntimeError("finish() called twice")

        if chunk is not None:
            self.write(chunk)
        self._write_buffer_copy = copy.deepcopy(self._write_buffer)
        # Automatically support ETags and add the Content-Length header if
        # we have not flushed any content yet.
        if not self._headers_written:
            if (
                    self._status_code == 200
                    and self.request.method in ("GET", "HEAD")
                    and "Etag" not in self._headers
            ):
                self.set_etag_header()
                if self.check_etag_header():
                    self._write_buffer = []
                    self.set_status(304)
            if self._status_code in (204, 304) or (100 <= self._status_code < 200):
                assert not self._write_buffer, (
                        "Cannot send body with %s" % self._status_code
                )
                self._clear_representation_headers()
            elif "Content-Length" not in self._headers:
                content_length = sum(len(part) for part in self._write_buffer)
                self.set_header("Content-Length", content_length)

        assert self.request.connection is not None
        self.request.connection.set_close_callback(None)  # type: ignore

        future = self.flush(include_footers=True)
        self.request.connection.finish()
        self._log()
        self._finished = True
        self.on_finish()
        self._break_cycles()
        return future

    def on_finish(self):
        super(LogHandler, self).on_finish()
        asyncio.get_event_loop().create_task(self.write_request_log())


class SessionHandler(RequestHandler):
    async def prepare(self):
        ret = super(SessionHandler, self).prepare()
        if ret is not None:
            await ret
        method = self.request.method.lower()
        if method == "options":
            return
        token = self.request.headers.get("x-token")
        ret = None
        if token is not None:
            ret = await tor_mod_vars.session_conn.get(token)
        if ret is None:
            token = uuid.uuid4().hex
            self.set_header("x-token", token)
            self.session_init = True
            self.session = {}
        else:
            self.session = json.loads(ret)
            self.session_init = False
        self.session_id = token
        self.delete_session = False
        self.session_expire = tor_mod_vars.session_expire

    def clear_session(self):
        self.delete_session = True

    def set_session_expire(self, ttl):
        self.session_expire = ttl

    async def save_session(self):
        if hasattr(self, "delete_session"):
            if self.delete_session:
                await tor_mod_vars.session_conn.delete(self.session_id)
                return
            ttl = await tor_mod_vars.session_conn.ttl(self.session_id)
            if self.session_init:
                await tor_mod_vars.session_conn.setex(self.session_id, self.session_expire, json.dumps(self.session))
            else:
                await tor_mod_vars.session_conn.setex(self.session_id, max(0, ttl), json.dumps(self.session))

    def on_finish(self):
        super(SessionHandler, self).on_finish()
        asyncio.get_event_loop().create_task(self.save_session())


class LogSessionHandler(LogHandler, SessionHandler):
    pass


def TrueResponse(msg="成功", code=1, **kwargs):
    return json.dumps(dict(code=code, msg=msg, **kwargs), ensure_ascii=False)


def FalseResponse(msg="失败", code=0, **kwargs):
    return json.dumps(dict(code=code, msg=msg, **kwargs), ensure_ascii=False)


def params_validate(schema):
    def wrapper(func):
        async def inner(self, *args, **kwargs):
            try:
                data = json.loads(self.request.body.decode())
            except Exception as e:
                return self.write(FalseResponse("json 解析失败", code=502))
            try:
                validate(data, schema)
            except ValidationError as e:
                return self.write(FalseResponse("参数校验失败：{}!".format(e.message), code=503))
            except Exception as e:
                return self.write(FalseResponse("参数校验失败：{}!".format(str(e)), code=503))
            ret = func(self, *args, **kwargs)
            if ret is not None:
                await ret

        return inner

    return wrapper


# 如果同一IP连续三次没有会话ID，则锁定IP一小时不能访问；
# 如果有会话ID，最后请求时间和会话持续时间不正确（连续三次，锁定IP一小时不能访问）
# 当前会话请求IP与最后一次会话IP不一致，禁止业务处理
def check_header(func):
    async def wrapper(self, *args, **kwargs):
        if tor_mod_vars.session_conn:
            token = self.request.headers.get("x-token")
            ip = self.get_ip()
            no_token_ip_key = "no_token_ip_" + ip
            session_time_ip = "session_time_ip_" + ip
            black_ip_key = "black_ip_key_" + ip
            is_black = await tor_mod_vars.session_conn.get(black_ip_key)
            if is_black is not None:
                return self.write(FalseResponse("当前ip已锁定!", 504))
            if token:
                await tor_mod_vars.session_conn.delete(no_token_ip_key)
            else:
                no_token_times = await tor_mod_vars.session_conn.incr(no_token_ip_key)
                await tor_mod_vars.session_conn.expire(no_token_ip_key, 3600)
                if no_token_times > 2:
                    await tor_mod_vars.session_conn.setex(black_ip_key, 3600, "ok")
            if token:
                ttl = await tor_mod_vars.session_conn.ttl(token)
                session_time = self.request.headers.get("x-time")
                if not session_time or abs(self.session_expire - ttl - int(session_time)) > 10:
                    error_session_time = await tor_mod_vars.session_conn.incr(session_time_ip)
                    await tor_mod_vars.session_conn.expire(session_time_ip, 3600)
                    if error_session_time > 2:
                        await tor_mod_vars.session_conn.setex(black_ip_key, 3600, "ok")
                else:
                    await tor_mod_vars.session_conn.delete(session_time_ip)
            if token:
                token_ip_key = "token_ip_" + token
                last_ip = await tor_mod_vars.session_conn.get(token_ip_key)
                if last_ip:
                    last_ip = last_ip.decode()
                    if last_ip != ip:
                        app_log.error("ip mismatch last_ip: {}  current:{}".format(last_ip, ip))
                        return self.write(FalseResponse("ip异常!", 505))
                else:
                    await tor_mod_vars.session_conn.setex(token_ip_key, self.session_expire, ip)
        ret = func(self, *args, **kwargs)
        if ret is not None:
            await ret

    return wrapper


async def paginate(db_object, query, page=1, paginate_by=10):
    count = await db_object.count(query)
    items = await db_object.execute(query.paginate(page, paginate_by))
    data = []
    for item in items:
        dic = copy.deepcopy(item.__data__)
        for k in dic:
            if isinstance(dic[k], datetime.datetime):
                dic[k] = dic[k].strftime('%Y-%m-%d %H:%M:%S')
            if isinstance(dic[k], decimal.Decimal):
                dic[k] = float(dic[k])
        data.append(dic)
    return count, data
