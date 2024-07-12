import importlib
import importlib.util
import pkgutil
from odooghost.utils import misc
from odooghost.constant import PLUGIN_START_WITH, PLUGIN_VARIABLE_NAME
from odooghost.exceptions import InvalidPluginNameError, PluginsNoCliError
from typing import Dict, List
from pydantic import BaseModel, create_model
from loguru import logger

@misc.singleton
class Plugins:
    # def __init__(self, *args, **kwargs):≤
        # self.plugins = self._get_plugins()

    @property
    def plugins(self):
        return self._get_plugins()
    
    @property
    def plugins_list(self):
        for _finder, name, _ispkg in pkgutil.iter_modules():
            if name.startswith(PLUGIN_START_WITH):
                yield name

    def _get_plugins(self) -> List[Dict[str, str]]:
        plugins_dict: dict = {
            name: importlib.import_module(name)
            for _finder, name, _ispkg in pkgutil.iter_modules()
            if name.startswith(PLUGIN_START_WITH)
        }
        plugins_list: list = list()
        for name, plugin in plugins_dict.items():
            plugin_name: str = plugin.__dict__.get(PLUGIN_VARIABLE_NAME)
            # Plugin validation
            if not plugin_name:
                raise InvalidPluginNameError(f"Plugin {name} does not have a valid name. Variable {PLUGIN_VARIABLE_NAME} is missing.")
            if not getattr(plugin, "cli", None):
                raise PluginsNoCliError(f"Plugin {name} does not have a cli attribute")
            if not getattr(plugin.cli, "registered_callback", None):
                raise PluginsNoCliError(f"Plugin {name} does not have a registered callback")
            
            plugins_list.append((plugin_name.replace(PLUGIN_START_WITH, ""), plugin))
                
        return plugins_list
    
    def configs(self, config: BaseModel) -> BaseModel:
        for plugin_config in self._plugins_config:
            new_config = getattr(plugin_config, config.__name__, None)
            if not new_config:
                continue
            config_dict: dict = dict()
            for field_name in new_config.model_fields:
                field = new_config.model_fields.get(field_name)
                config_dict[field_name] = (field.annotation, field.default)

            config = create_model(
                config.__name__,
                **config_dict,
                __base__=config,
            )
        return config
    
    @property
    def clis(self):
        for plugin in self.plugins_list:
            try:
                var_name: str = ".cli"
                plugin_cli = importlib.import_module(var_name, package=plugin)
                yield (getattr(plugin_cli, PLUGIN_VARIABLE_NAME), plugin_cli.cli)
            except ImportError:
                raise PluginsNoCliError(f"Plugin {plugin} does not have a cli attribute")
        
    @property
    def _plugins_config(self):
        for plugin in self.plugins_list:
            try:
                var_name: str = ".config"
                yield importlib.import_module(var_name, package=plugin)
            except ImportError:
                pass