import threading
import typing

from .dispatchers import MessageDispatcher
from .handlers import MessageService, MessageContextType
from .message import Message, MessageType
from .message_router import MessageRouter
from .meta import MessageMetaInformationType, MessageMetaInformation
from .networking import NetworkEngine
from ..logging import LoggerProxy, default_logger, error, debug, warning
from ...component import BackendComponentData


class MessageBus:
    """
    Bus for dispatching messages.

    The message bus is probably the most central aspect of the system as a whole. It not only invokes local message handlers (which are basically
    callback functions), it also sends messages across the network to other components if necessary. The message bus on the remote side will then
    decide what to do with the incoming message: Dispatch it locally there, send it to yet another component, or just ignore it.

    Message handlers are always registered through a ``MessageService``. When a message gets dispatched locally by the bus, it will call any handlers
    associated with the message (via its name). If a message needs to be sent to another component, the bus will invoke the ``NetworkEngine`` to do
    so.

    To be error tolerant, any exceptions that arise during message handling will be logged but won't result in program termination.

    Notes:
        The message bus is thread-safe.
    """

    def __init__(self, comp_data: BackendComponentData):
        """
        Args:
            comp_data: The global component data.
        """
        from .dispatchers import (
            CommandDispatcher,
            CommandReplyDispatcher,
            EventDispatcher,
        )
        from .command import Command
        from .command_reply import CommandReply
        from .event import Event

        self._comp_data = comp_data

        debug("Creating network engine", scope="bus")
        self._network_engine = self._create_network_engine()

        self._services: typing.List[MessageService] = []
        self._dispatchers: typing.Dict[type[MessageType], MessageDispatcher] = {
            Command: CommandDispatcher(),
            CommandReply: CommandReplyDispatcher(),
            Event: EventDispatcher(),
        }
        self._router = MessageRouter(comp_data.comp_id)

        self._lock = threading.Lock()

    def _create_network_engine(self) -> NetworkEngine:
        return NetworkEngine(self._comp_data, self)

    def add_service(self, svc: MessageService) -> bool:
        """
        Adds a new message service to the bus.

        Args:
            svc: The message service to add.

        Returns:
            Whether the message service was added.
        """
        with self._lock:
            if svc in self._services:
                return False

            self._services.append(svc)
            return True

    def remove_service(self, svc: MessageService) -> bool:
        """
        Removes a message service from the bus.

        Args:
            svc: The message service to remove.

        Returns:
            Whether the message service was removed.
        """
        with self._lock:
            if svc not in self._services:
                return False

            self._services.remove(svc)
            return True

    def run(self) -> None:
        """
        Initiates periodic tasks performed by the bus.
        """
        self._network_engine.run()
        self._process()

    def dispatch(self, msg: Message, msg_meta: MessageMetaInformationType) -> None:
        """
        Dispatches a message.

        To do so, the message is first checked for validity (whether it actually *may* be dispatched). If it is valid,
        the ``MessageRouter`` will determine if it needs to be dispatched to another component or locally (or both).

        Args:
            msg: The message to be dispatched.
            msg_meta: The message meta information.
        """
        try:
            self._router.verify_message(msg, msg_meta)
        except MessageRouter.RoutingError as exc:
            error(
                f"A routing error occurred: {str(exc)}", scope="bus", message=str(msg)
            )
        else:
            if self._router.check_remote_routing(msg, msg_meta):
                self._remote_dispatch(msg, msg_meta)

            # The local dispatchers are always invoked for their pre- and post-steps
            self._local_dispatch(msg, msg_meta)

    def _process(self) -> None:
        self._network_engine.process()

        for _, dispatcher in self._dispatchers.items():
            dispatcher.process()

        threading.Timer(1.0, self._process).start()

    def _local_dispatch(
        self, msg: Message, msg_meta: MessageMetaInformationType
    ) -> None:
        local_routing = self._router.check_local_routing(msg, msg_meta)
        for msg_type, dispatcher in self._dispatchers.items():
            if not isinstance(msg, msg_type):
                continue

            dispatcher.pre_dispatch(msg, msg_meta)

            if local_routing:
                msg_dispatched = False
                for svc in self._services:
                    msg_dispatched |= self._dispatch_to_service(
                        dispatcher, msg, msg_type, msg_meta, svc
                    )

                if not msg_dispatched:
                    warning(
                        "A message was dispatched locally but not handled",
                        scope="bus",
                        message=str(msg),
                    )

            dispatcher.post_dispatch(msg, msg_meta)

    def _remote_dispatch(
        self, msg: Message, msg_meta: MessageMetaInformationType
    ) -> None:
        self._network_engine.send_message(msg, msg_meta)

    def _dispatch_to_service(
        self,
        dispatcher: MessageDispatcher,
        msg: Message,
        msg_type: type[MessageType],
        msg_meta: MessageMetaInformationType,
        svc: MessageService,
    ) -> bool:
        msg_dispatched = False
        for handler in svc.message_handlers.find_handlers(msg.name):
            try:
                act_msg = typing.cast(msg_type, msg)
                ctx = self._create_context(msg, msg_meta, svc)
                dispatcher.dispatch(act_msg, msg_meta, handler, ctx)
                msg_dispatched = True
            except Exception as exc:  # pylint: disable=broad-exception-caught
                import traceback

                error(
                    f"An exception occurred while processing a message: {str(exc)}",
                    scope="bus",
                    message=str(msg),
                    exception=type(exc),
                )
                debug(f"Traceback:\n{''.join(traceback.format_exc())}", scope="bus")

        return msg_dispatched

    def _create_context(
        self, msg: Message, msg_meta: MessageMetaInformation, svc: MessageService
    ) -> MessageContextType:
        logger_proxy = LoggerProxy(default_logger())
        logger_proxy.add_param("trace", str(msg.trace))
        return svc.create_context(
            msg_meta, logger=logger_proxy, config=self._comp_data.config
        )

    @property
    def network(self) -> NetworkEngine:
        """
        The network engine instance.
        """
        return self._network_engine
