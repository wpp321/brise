import os
import types
import sys
import pickle
from .sm_util import sm4_encrypt_byte, sm4_decrypt_byte

key = "dkgsdfhkgsfkghfdghkfdkfg"


def dump_mod(mod_name):
    modules = {}
    for item in os.walk(mod_name):
        if "__pycache__" not in item[0] and "__init__.py" in item[2]:
            with open(os.path.join(item[0], "__init__.py"), "r", encoding="utf-8") as f:
                code = f.read()
            mod = item[0].replace(os.sep, ".")
            modules[mod] = {
                "code": code,
                "is_package": True
            }
            for doc in item[2]:
                if "__init__.py" != doc and doc.endswith(".py"):
                    with open(os.path.join(item[0], doc), "r", encoding="utf-8") as f:
                        modules[mod + "." + doc[:-3]] = {
                            "code": f.read(),
                            "is_package": False
                        }
    return modules


def dumps_to_file(data, path):
    data = sm4_encrypt_byte(key[:16], pickle.dumps(data))
    with open(path, "wb") as f:
        f.write(data)


def loads_file(path):
    with open(path, "rb") as f:
        data = sm4_decrypt_byte(key[:16], f.read())
    return pickle.loads(data)


class ModImporter:

    def __init__(self, modules):
        self._modules = modules

    def find_module(self, fullname, path):
        if fullname in self._modules.keys():
            return self
        return None

    def load_module(self, fullname):
        code = self.get_code(fullname)
        ispkg = self.is_package(fullname)
        mod = sys.modules.setdefault(fullname, types.ModuleType(fullname))
        mod.__file__ = "<%s>" % self.__class__.__name__
        mod.__loader__ = self
        if ispkg:
            mod.__path__ = []
            mod.__package__ = fullname
        else:
            mod.__package__ = fullname.rpartition('.')[0]
        exec(code, mod.__dict__)
        return mod

    def get_code(self, fullname):
        return self._modules[fullname]["code"]

    def is_package(self, fullname):
        return self._modules[fullname]["is_package"]
