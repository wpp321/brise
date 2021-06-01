from . import tor_mod_vars
import aredis
import tornado
import tornado.options
import tornado.ioloop
from tornado.web import Application
import importlib
import os
import sys
from .password_verify import password_de
from .mod import loads_file, ModImporter
from tornado.log import app_log
from . import plugins


class Server:
    def __init__(self, log_mysql=None, session_redis=None, port=8080, session_expire=3600):
        tornado.options.parse_command_line()
        if log_mysql:
            table_name = log_mysql.pop('table_name', None)
            log_mysql["password"] = password_de(log_mysql["password"])
            tor_mod_vars.database.init(**log_mysql)
            from .log_model import RequestLog
            if table_name:
                setattr(RequestLog._meta, "table_name", table_name)
            else:
                setattr(RequestLog._meta, "table_name", "request_log")
            tor_mod_vars.database.create_tables([RequestLog])
        if session_redis:
            if session_redis["password"]:
                session_redis["password"] = password_de(session_redis["password"])
            tor_mod_vars.session_conn = aredis.StrictRedis(**session_redis)
        tor_mod_vars.session_expire = session_expire
        app = Application()
        app.listen(port)
        app_log.info("run at {}".format(port))
        self.app = app

    def register_blueprint(self, blue_print, project_prefix_path=""):
        routes = []
        for path, handler in blue_print.routes:
            routes.append((project_prefix_path + path, handler))
        self.app.add_handlers(".*$", routes)

    def run(self):
        app_log.info("start serving...")
        tornado.ioloop.IOLoop.current().start()


def run_server(modules=None, log_mysql=None, session_redis=None, port=8080, session_expire=3600,
               project_url=""):
    server = Server(log_mysql=log_mysql, session_redis=session_redis, port=port, session_expire=session_expire,
                    )
    for item in os.walk("plugins"):
        for module in item[2]:
            if module.endswith(".mod"):
                sys.meta_path.append(ModImporter(loads_file(os.path.join(item[0], module))))
                module_name = module[:-4]
                m = importlib.import_module(module_name)
                setattr(plugins, module_name, m)
                app_log.info("load plugin {}".format(module_name))
    if modules:
        for module in modules:
            m = importlib.import_module(module)
            server.register_blueprint(m.api, project_url)
            app_log.info("load module {}".format(module))
    for item in os.walk("apps"):
        for module in item[2]:
            if module.endswith(".mod"):
                sys.meta_path.append(ModImporter(loads_file(os.path.join(item[0], module))))
                module_name = module[:-4]
                m = importlib.import_module(module_name)
                server.register_blueprint(m.api, project_url)
                app_log.info("load module {}".format(module_name))
    server.run()
