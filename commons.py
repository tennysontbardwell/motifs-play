import yaml
import os


try:
    _path = os.environ['SETTING']
except KeyError:
    _path = './settings.yaml'

with open(_path) as fp:
    settings = yaml.safe_load(fp)



