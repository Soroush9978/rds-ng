import json
import typing

import socketio

from .component_data import ComponentData
from .component_id import ComponentID
from .roles.component_role import ComponentRole
from ..core import Core
from ..core.service import Service, ServiceContext, ServiceContextType
from ..core.logging import info, warning
from ..utils.config import Configuration


class Component:
    """ Base application class for all RDS components. """
    def __init__(self, comp_id: ComponentID, role: ComponentRole, *, module_name: str, config_file: str = "./config.toml"):
        config = self._create_config(config_file)
        comp_id = self._sanitize_component_id(comp_id, config)
        
        from .meta_information import MetaInformation
        meta_info = MetaInformation()
        comp_info = meta_info.get_component(comp_id.component)
        
        self._data = ComponentData(
            comp_id=comp_id,
            role=role,
            config=config,
            title=meta_info.title,
            name=comp_info["name"],
            version=meta_info.version,
        )
        
        info(str(self), role=self._data.role.name)
        info("-- Starting component...")
        
        self._core = Core(module_name, self._data)
        
        self._add_default_routes()
        
    def app(self) -> typing.Any:
        # Note: This is the only dependency on socket.io outside the network engine, as we need to use their app logic
        return socketio.WSGIApp(self._core.network.server, self._core.flask)
    
    def create_service(self, name: str, *, context_type: typing.Type[ServiceContextType] = ServiceContext) -> Service:
        svc = Service(self._data.comp_id, name, message_bus=self._core.message_bus, context_type=context_type)
        self._core.register_service(svc)
        return svc
    
    def run(self) -> None:
        self._core.run()
    
    def _create_config(self, config_file: str) -> Configuration:
        from ..settings import get_default_settings
        config = Configuration()
        config.add_defaults(get_default_settings())
        
        try:
            config.load(config_file)
        except Exception as e:
            warning("Component configuration could not be loaded", scope="core", error=str(e))
        
        return config
    
    def _sanitize_component_id(self, comp_id: ComponentID, config: Configuration) -> ComponentID:
        if comp_id.instance is None:
            from ..settings import ComponentSettingIDs
            return ComponentID(comp_id.type, comp_id.component, config.value(ComponentSettingIDs.INSTANCE))
        else:
            return comp_id
    
    @property
    def config(self) -> Configuration:
        return self._data.config

    @property
    def core(self) -> Core:
        return self._core
    
    @property
    def data(self) -> ComponentData:
        return self._data
    
    def __str__(self) -> str:
        return f"{self._data.title} v{self._data.version}: {self._data.name} ({self._data.comp_id})"
    
    def _add_default_routes(self) -> None:
        # The main entry point (/) returns basic component info as a JSON string
        self._core.flask.add_url_rule("/", view_func=lambda: json.dumps({
            "id": str(self._data.comp_id),
            "name": self._data.name,
            "version": str(self._data.version),
        }))
