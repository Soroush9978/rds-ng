import threading
import typing

import socketio

from .. import Message
from ...logging import info, warning, error, debug
from ....utils import UnitID
from ....utils.config import Configuration


class Client(socketio.Client):
    """
    The client connection, based on ``socketio.Client``.
    """
    def __init__(self, comp_id: UnitID, config: Configuration):
        """
        Args:
            comp_id: The component identifier.
            config: The global configuration.
        """
        self._comp_id = comp_id
        self._config = config
        
        from ....settings import NetworkClientSettingIDs
        self._server_address: str = self._config.value(NetworkClientSettingIDs.SERVER_ADDRESS)
        self._connection_timeout: int = self._config.value(NetworkClientSettingIDs.CONNECTION_TIMEOUT)
        
        super().__init__(reconnection_delay_max=self._connection_timeout)
        
        self._lock = threading.Lock()
        
        self._connect_events()
        
    def _connect_events(self) -> None:
        self.on("connect", self._on_connect)
        self.on("connect_error", self._on_connect_error)
        self.on("disconnect", self._on_disconnect)

    def run(self) -> None:
        """
        Automatically connects to a server if one was configured.
        """
        if self._server_address != "":
            info(f"Connecting to {self._server_address}...", scope="client")
            
            from socketio.exceptions import ConnectionError
            try:
                self.connect(self._server_address, auth=self._get_authentication(), wait=True, wait_timeout=self._connection_timeout)
            except ConnectionError as e:
                error(f"Failed to connect to server: {str(e)}", scope="client")
            
    def send_message(self, msg: Message) -> None:
        """
        Sends a message to the server (if connected).
        
        For this, the message will be encoded as *JSON* first.
        
        Args:
            msg: The message to send.
        """
        if self.connected:
            debug(f"Sending message: {msg}", scope="client")
            with self._lock:
                self.emit(msg.name, data=msg.to_json())
    
    def _on_connect(self) -> None:
        info("Connected to server", scope="client")
        
    def _on_connect_error(self, reason: typing.Any) -> None:
        warning("Unable to connect to server", scope="client", reason=str(reason))
    
    def _on_disconnect(self) -> None:
        info("Disconnected from server", scope="client")
        
    def _get_authentication(self) -> typing.Dict[str, str]:
        return {"component_id": str(self._comp_id)}
