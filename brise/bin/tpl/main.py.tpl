from brise.server import run_server
import setting


if __name__ == '__main__':
    run_server(modules=setting.modules,
               log_mysql=setting.log_mysql,
               session_redis=setting.session_redis,
               session_expire=setting.session_expire,
               port=setting.port,
               project_url=setting.project_url)
