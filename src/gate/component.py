# pylint: disable=all
from common.py.component import (
    BackendComponent,
    ComponentType,
    ComponentUnit,
)
from common.py.component.roles import NodeRole
from common.py.core.messaging import Message, Event, Channel
from common.py.service import ServiceContext
from common.py.utils import UnitID

comp = BackendComponent(
    UnitID(ComponentType.INFRASTRUCTURE, ComponentUnit.GATE),
    NodeRole(),
    module_name=__name__,
)
app = comp.app()
svc = comp.create_service("Gate service")


@Message.define("msg/event")
class MyEvent(Event):
    some_cool_text: str = ""
    a_number: int = 12


@svc.message_handler("msg/event", MyEvent)
def h(msg: MyEvent, ctx: ServiceContext) -> None:
    ctx.logger.info(f"EVENT: {msg.some_cool_text}, {msg.a_number}")
    ctx.message_emitter.emit_event(
        MyEvent, Channel.direct(str(msg.sender)), some_cool_text="Whoops!", a_number=999
    )
    ctx.message_emitter.emit_event(
        MyEvent,
        Channel.direct(str(msg.sender)),
        some_cool_text="And another one!",
        a_number=123,
    )


comp.run()
