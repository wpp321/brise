class Blueprint:
    def __init__(self, url_prefix=""):
        self.routes = []
        self.url_prefix = url_prefix

    def add_route(self, route):
        def wrap_class(cls):
            cls.api = self
            self.routes.append((self.url_prefix + route, cls))

        return wrap_class
