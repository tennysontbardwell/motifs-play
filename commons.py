import yaml
import os
import logging
import sys


try:
    _path = os.environ['SETTING']
except KeyError:
    _path = './settings.yaml'

with open(_path) as fp:
    settings = yaml.safe_load(fp)


def make_log(name):
    LOG = logging.getLogger(name)
    LOG.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    LOG.addHandler(ch)
    return LOG


LOG = make_log(__name__)


def file_cached(function):
    '''Only runs if the path does not yet exist, uses a temp file
    for atomic operation. Will create directories if they don't exit'''
    def wrapper(path, *args, **kwargs):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            temp = path +  '.temp'
            if os.path.exists(temp):
                LOG.info('removing left over temp file {}'.format(temp))
                os.remove(temp)
            function(temp, *args, **kwargs)
            os.rename(temp, path)

    return wrapper

