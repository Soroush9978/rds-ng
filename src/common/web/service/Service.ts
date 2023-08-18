import { MessageEmitter } from "../core/messaging/handlers/MessageEmitter";
import { type MessageHandler } from "../core/messaging/handlers/MessageHandler";
import { MessageService } from "../core/messaging/handlers/MessageService";
import { Message, type MessageType } from "../core/messaging/Message";
import { type MessageBusProtocol } from "../core/messaging/MessageBusProtocol";
import { type Constructable } from "../utils/Types";
import { UnitID } from "../utils/UnitID";
import { ServiceContext } from "./ServiceContext";

/**
 * Base service class providing easy message handler mapping.
 *
 * A service can be seen as the bridge between the inner workings of a component (represented by a ``Core``) and the
 * outside component domain.
 *
 * Services register the various message handlers that are called when a certain message is received by the message bus and
 * dispatched locally. They also create instances of ``ServiceContext`` (or a subclass) that represent a single *unit of work*
 * when executing a message handler.
 *
 * Message handlers are defined using the ``message_handler`` decorator, as can be seen in this example (``svc`` being a ``Service`` instance):
 * ```
 *     @svc.messageHandler("msg/event", Event)
 *     function h(msg: Event, ctx: ServiceContext): void {
 *         ctx.logger.info("EVENT HANDLER CALLED");
 *     }
 * ```
 */
export class Service<CtxType extends ServiceContext = ServiceContext> extends MessageService<CtxType> {
    private readonly _name: string;

    /**
     * @param compID - The global component identifier.
     * @param name - The service name.
     * @param messageBus - The global message bus.
     * @param contextType - The type to use when creating a message context.
     */
    public constructor(compID: UnitID, name: string, messageBus: MessageBusProtocol,
                       contextType: Constructable<CtxType> = ServiceContext as Constructable<CtxType>) {
        super(compID, messageBus, contextType);

        this._name = name;
    }

    /**
     * A decorator to declare a message handler.
     *
     * To define a new message handler, use the following pattern:
     * ```
     *     @svc.messageHandler("msg/event", Event)
     *     function h(msg: Event, ctx: ServiceContext): void {
     *         ctx.logger.info("EVENT HANDLER CALLED");
     *     }
     * ```
     *
     * @param filter - The message name filter to match against; wildcards (*) are supported for more generic handlers.
     * @param messageType - The type of the message.
     */
    public messageHandler(filter: string, messageType: MessageType = Message): Function {
        return (handler: MessageHandler): MessageHandler => {
            this.messageHandlers.addHandler(filter, handler, messageType);
            return handler;
        };
    }

    /**
     * The name of this service.
     */
    public get name(): string {
        return this._name;
    }

    /**
     * The service's message emitter.
     */
    public get messageEmitter(): MessageEmitter {
        return this.createMessageEmitter();
    }

    /**
     * Gets the string representation of this service.
     */
    public toString(): string {
        return this._name;
    }
}
