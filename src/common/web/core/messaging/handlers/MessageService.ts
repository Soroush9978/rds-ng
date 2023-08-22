import { type Constructable } from "../../../utils/Types";
import { UnitID } from "../../../utils/UnitID";
import { LoggerProxy } from "../../logging/LoggerProxy";
import { type MessageBusProtocol } from "../MessageBusProtocol";
import { MessageContext } from "./MessageContext";
import { MessageEmitter } from "./MessageEmitter";
import { MessageHandlers } from "./MessageHandlers";

/**
 * Base class for all message services.
 *
 * A *message service* wraps message handlers and proper message context creation (i.e., using a flexible context type). It
 * is used by the message bus as an encapsulated layer for message dispatching.
 */
export class MessageService<CtxType extends MessageContext = MessageContext> {
    private readonly _compID: UnitID;

    private readonly _messageBus: MessageBusProtocol;
    private readonly _messageHandlers: MessageHandlers;
    private readonly _contextType: Constructable<CtxType>;

    /**
     * @param compID - The global component identifier.
     * @param messageBus - The global message bus.
     * @param contextType - The type to use when creating a message context.
     */
    public constructor(compID: UnitID, messageBus: MessageBusProtocol, contextType: Constructable<CtxType> = MessageContext as Constructable<CtxType>) {
        this._compID = compID;

        this._messageBus = messageBus;
        this._messageHandlers = new MessageHandlers();
        this._contextType = contextType;
    }

    /**
     * Creates a new service context.
     *
     * @param logger - The logger to be used within the new context.
     * @param args - Any additional parameters.
     *
     * @returns - The newly created message context.
     */
    public createContext(logger: LoggerProxy, ...args: any[]): MessageContext {
        return new this._contextType(this.createMessageEmitter(), logger, ...args);
    }

    /**
     * Creates a new message emitter.
     *
     * @returns - The newly created message emitter.
     */
    public createMessageEmitter(): MessageEmitter {
        return new MessageEmitter(this._compID, this._messageBus);
    }

    /**
     * The message handlers maintained by this message service.
     */
    public get messageHandlers(): MessageHandlers {
        return this._messageHandlers;
    }
}
