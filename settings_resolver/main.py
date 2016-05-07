import re
from settings_overrider import override

# Deferred is used to wrap a setting variable lambda function, that will be 
# resolved late, after all the imports
class Deferred(object):
    def __init__(self, func):
        self.func = func

# deferred is a function that wraps a setting's lambda function into a
# Deferred object. Users could import this as `d` for convenience.
def deferred(func):
    return Deferred(func)

# An instance of Resolver wraps the settings module. This class provides a 
# default getter function, used to resolve settings after all of the
# overrides have happened.
class Resolver(object):
    def __getattr__(self, name):
        v = self.settings[name]
        return v.func() if isinstance(v, Deferred) else v

# resolver provides the getter that resolves the Deferreds. This should be
# used inside the lambda functions, to dereference any other setting value.
# Users can import this as `s` for convenience.
resolver = Resolver()

def resolve(settings, yaml=None, env=None):
    """
    If either yaml or env is given, this delegates to 
    settings_overrider.override to override settings with environment variables
    or a yaml file.
    :param dict settings: settings dict to be updated; usually it's ``globals()``
    :param yaml: path to YAML file
    :type yaml: str or FileIO
    :param str env: prefix for environment variables
    """
    resolver.settings = settings
    if (yaml is not None or env is not None): 
        override(settings, yaml=yaml, env=env)

    # Resolve all the deferreds, recursively
    for k, v in settings.items():
        if isinstance(v, Deferred): settings[k] = resolver.__getattr__(k)
