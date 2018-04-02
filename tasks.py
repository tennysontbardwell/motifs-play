from os import path


def file_cached(function):
    def wrapper(path, *args, **kwargs):
        if not path.exists(path):
            function(path, *args, **kwargs)

    return wrapper

