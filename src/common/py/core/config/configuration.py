import typing
import os


class Configuration:
    """ A simple class for retrieving configuration settings. """
    def __init__(self, env_prefix: str = "RDS"):
        self._settings = {}
        self._defaults = {}
        
        self._env_prefix = env_prefix
        
    def load(self, filename: str) -> None:
        if os.path.exists(filename):
            with open(filename, "rb") as f:
                import tomli
                self._settings = tomli.load(f)
        else:
            raise FileNotFoundError("Configuration file doesn't exist")
        
    def add_defaults(self, defaults: typing.Dict) -> None:
        from deepmerge import always_merger
        self._defaults = always_merger.merge(self._defaults, defaults)

    def value(self, key: str) -> typing.Any:
        """ The value is first looked up in the environment variables. If not found, the loaded settings are searched.
            If that also fails, the defaults are used. In case the key is missing everywhere, an exception is raised.
        """
        env_key = f"{self._env_prefix}_{key.replace('.', '_')}".upper()
        if env_key in os.environ:
            return os.environ.get(env_key)
        
        try:
            return self._traverse_dict(key.split("."), self._settings)
        except:
            return self._traverse_dict(key.split("."), self._defaults)

    def _traverse_dict(self, path: typing.List[str], d: typing.Dict) -> typing.Any:
        d = d[path[0]]
        return d if len(path) == 1 else self._traverse_dict(path[1:], d)
