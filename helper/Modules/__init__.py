# pylint: disable-msg=C0114
import os

_PATH = 'helper/Modules'
ALL = [os.path.splitext(i)[0] for i in os.listdir(_PATH) if
       os.path.isfile(os.path.join(_PATH, i)) and
       os.path.splitext(i)[1] == '.py' and
       i != '__init__.py']
