import abc

from ...messaging import Message
from ...messaging.meta import MessageMetaInformation
from ....component import ComponentID


class NetworkRouter(abc.ABC):
    class RoutingError(RuntimeError):
        pass
    
    def __init__(self, comp_id: ComponentID, *, has_client: bool, has_server: bool):
        self._comp_id = comp_id
        
        self._has_client = has_client
        self._has_server = has_server
        
    def verify_in_message(self, msg: Message) -> None:
        if msg.target.is_local:
            self._verify_local_in_message(msg)
        if msg.target.is_direct:
            self._verify_direct_in_message(msg)
        elif msg.target.is_room:
            self._verify_room_in_message(msg)
    
    def verify_out_message(self, msg: Message, msg_meta: MessageMetaInformation) -> None:
        if msg.target.is_local:
            self._verify_local_out_message(msg, msg_meta)
        if msg.target.is_direct:
            self._verify_direct_out_message(msg, msg_meta)
        elif msg.target.is_room:
            self._verify_room_out_message(msg, msg_meta)
            
    def check_client_out_routing(self, msg: Message, msg_meta: MessageMetaInformation) -> bool:
        return self._has_client
    
    def check_server_out_routing(self, msg: Message, msg_meta: MessageMetaInformation) -> bool:
        return self._has_server
    
    def _verify_local_in_message(self, msg: Message) -> None:
        # Local messages should never land here
        raise NetworkRouter.RoutingError("A local message was received over the network")
    
    def _verify_direct_in_message(self, msg: Message) -> None:
        # An incoming direct message must be targeted to a component
        if msg.target.target_id is None:
            raise NetworkRouter.RoutingError("Direct message without a target received")
    
    def _verify_room_in_message(self, msg: Message) -> None:
        # Room messages must be targeted to a room
        if msg.target.target is None or msg.target.target == "":
            raise NetworkRouter.RoutingError("Room message without a target room received")
    
    def _verify_local_out_message(self, msg: Message, msg_meta: MessageMetaInformation) -> None:
        # Local messages should never land here
        raise NetworkRouter.RoutingError("A local message was sent through the network engine")
    
    def _verify_direct_out_message(self, msg: Message, msg_meta: MessageMetaInformation) -> None:
        # An outgoing direct message must be targeted to another component
        if msg.target.target_id is None:
            raise NetworkRouter.RoutingError("Direct message without a target sent")
        elif msg.target.target_id.equals(self._comp_id):
            raise NetworkRouter.RoutingError("Direct message to this component sent through the network engine")
    
    def _verify_room_out_message(self, msg: Message, msg_meta: MessageMetaInformation) -> None:
        # Room messages must be targeted to a room
        if msg.target.target is None or msg.target.target == "":
            raise NetworkRouter.RoutingError("Room message without a target room sent")
