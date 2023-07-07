import dataclasses
import typing

from .client import Client
from .routing import NetworkRouter
from .server import Server
from .. import Message, MessageBusProtocol
from ..meta import MessageMetaInformation
from ....component import ComponentData


class NetworkEngine:
    """ The main network management class, based on socket.io. """
    def __init__(self, comp_data: ComponentData, message_bus: MessageBusProtocol):
        self._comp_data = comp_data
        
        self._message_bus = message_bus
        
        self._client = self._create_client() if self._comp_data.role.networking_aspects.has_client else None
        self._server = self._create_server() if self._comp_data.role.networking_aspects.has_server else None
        
        self._router = typing.cast(NetworkRouter, self._comp_data.role.networking_aspects.router_type(comp_data.comp_id))
        if not isinstance(self._router, NetworkRouter):
            raise RuntimeError("An invalid router type was specified in the networking aspects")

    def _create_client(self) -> Client:
        return Client(self._comp_data)
    
    def _create_server(self) -> Server:
        return Server(self._comp_data)
    
    def run(self) -> None:
        if self.has_server:
            self._server.on("*", lambda msg_name, _, data: self._handle_received_message(MessageMetaInformation.Entrypoint.SERVER, msg_name, data))
            self._server.run()
            
        if self.has_client:
            self._client.on("*", lambda msg_name, data: self._handle_received_message(MessageMetaInformation.Entrypoint.CLIENT, msg_name, data))
            self._client.run()
            
    def send_message(self, msg: Message, msg_meta: MessageMetaInformation) -> None:
        try:
            self._router.verify_message(NetworkRouter.Direction.OUT, msg)
        except NetworkRouter.RoutingError as e:
            self._routing_error(str(e), message=str(msg))
        else:
            if self._router.check_server_routing(NetworkRouter.Direction.OUT, msg, msg_meta):
                self._server.send_message(msg, skip_components=[self._comp_data.comp_id])
                
            if self._router.check_client_routing(NetworkRouter.Direction.OUT, msg, msg_meta):
                self._client.send_message(msg)
    
    def _handle_received_message(self, entrypoint: MessageMetaInformation.Entrypoint, msg_name: str, data: str) -> None:
        try:
            msg = self._unpack_message(msg_name, data)
            msg_meta = self._create_message_meta_information(msg, entrypoint)
        except Exception as e:
            self._routing_error(str(e), data=data)
        else:
            if self._router.check_local_routing(NetworkRouter.Direction.IN, msg, msg_meta):
                self._message_bus.dispatch(msg, msg_meta)
                
            # Perform rerouting if necessary
            msg = dataclasses.replace(msg, sender=self._comp_data.comp_id)
            
            if self._router.check_server_routing(NetworkRouter.Direction.IN, msg, msg_meta):
                self._server.send_message(msg, skip_components=[self._comp_data.comp_id, msg.sender])
            
            if self._router.check_client_routing(NetworkRouter.Direction.IN, msg, msg_meta):
                self._client.send_message(msg)
                
    def _unpack_message(self, msg_name: str, data: str) -> Message:
        # Look up the actual message via its name
        from .. import MessageTypesCatalog
        msg_type = MessageTypesCatalog.find_type(msg_name)
        
        if msg_type is None:
            raise RuntimeError(f"The message type '{msg_name}' is unknown")
        
        # Unpack the message into its actual type
        msg = typing.cast(Message, msg_type.from_json(data))
        self._router.verify_message(NetworkRouter.Direction.IN, msg)
        
        msg.hops.append(self._comp_data.comp_id)
        return msg
    
    def _create_message_meta_information(self, msg: Message, entrypoint: MessageMetaInformation.Entrypoint, **kwargs) -> MessageMetaInformation:
        from ..meta import MessageMetaInformationCreator
        return MessageMetaInformationCreator.create_meta_information(msg, entrypoint, **kwargs)
    
    def _routing_error(self, msg: str, **kwargs) -> None:
        from ...logging import error
        error(f"A routing error occurred: {msg}", scope="network", **kwargs)
    
    @property
    def has_server(self) -> bool:
        return self._server is not None
    
    @property
    def server(self) -> Server:
        return self._server

    @property
    def has_client(self) -> bool:
        return self._client is not None
    
    @property
    def client(self) -> Client:
        return self._client
