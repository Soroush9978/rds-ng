from enum import Flag, auto

from ..messaging import Message


class NetworkRouteResolver:
    class RouteType(Flag):
        CLIENT = auto()
        SERVER = auto()
        
    def __init__(self, *, has_client: bool, has_server: bool):
        self._has_client = has_client
        self._has_server = has_server
        
    def resolve(self, msg: Message) -> RouteType:
        route_type = NetworkRouteResolver.RouteType(0)
        
        if self._check_send_through_client(msg):
            route_type |= NetworkRouteResolver.RouteType.CLIENT
        
        if self._check_send_through_server(msg):
            route_type |= NetworkRouteResolver.RouteType.SERVER
        
        return route_type
    
    def _check_send_through_client(self, msg: Message) -> bool:
        if self._has_client and not self._has_server:
            return True
        
        return False
    
    def _check_send_through_server(self, msg: Message) -> bool:
        if self._has_server and not self._has_client:
            return True
        
        return False
