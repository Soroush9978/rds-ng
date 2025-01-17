import { io, Socket } from "socket.io-client";

import { ClientConnectedEvent, ClientConnectionErrorEvent, ClientDisconnectedEvent } from "../../../api/network/NetworkEvents";
import { NetworkClientSettingIDs } from "../../../settings/NetworkSettingIDs";
import { Configuration } from "../../../utils/config/Configuration";
import { UnitID } from "../../../utils/UnitID";
import logging from "../../logging/Logging";
import { MessageBuilder } from "../composers/MessageBuilder";
import { Channel } from "../Channel";
import { Message } from "../Message";

type ClientMessageHandler = (msgName: string, data: string) => void;

/**
 * The client connection, based on ``socketio``.
 */
export class Client {
    private readonly _compID: UnitID;
    private readonly _config: Configuration;

    private readonly _socket: Socket;
    private readonly _messageBuilder: MessageBuilder;

    private readonly _serverAddress: string;
    private readonly _connectionTimeout: number;

    private _messageHandler: ClientMessageHandler | null = null;

    /**
     * @param compID - The component identifier.
     * @param config - The global configuration.
     * @param messageBuilder - A message builder instance.
     */
    public constructor(compID: UnitID, config: Configuration, messageBuilder: MessageBuilder) {
        this._compID = compID;
        this._config = config;

        this._serverAddress = this._config.value<string>(NetworkClientSettingIDs.ServerAddress);
        this._connectionTimeout = this._config.value<number>(NetworkClientSettingIDs.ConnectionTimeout);

        this._socket = this.createSocket();
        this._messageBuilder = messageBuilder;

        this.connectEvents();
    }

    private createSocket(): Socket {
        if (this._serverAddress == "") {
            throw new Error("No server address configured");
        }

        return io(this._serverAddress, {
            auth: this.getAuthentication(),
            autoConnect: false,
            reconnection: false,
            timeout: this._connectionTimeout * 1000
        });
    }

    private connectEvents(): void {
        this._socket.on("connect", () => this.onConnect());
        this._socket.on("connect_error", (reason: any) => this.onConnectError(reason));
        this._socket.on("disconnect", () => this.onDisconnect());
        this._socket.onAny((msgName: string, data: string) => this.onMessage(msgName, data));
    }

    /**
     * Automatically connects to a server.
     */
    public run(): void {
        this.connectToServer();
    }

    /**
     * Periodically performs certain tasks.
     */
    public process(): void {
    }

    /**
     * Establishes the connection to the server.
     */
    public connectToServer(): void {
        if (!this._socket.connected) {
            logging.info(`Connecting to ${this._serverAddress}...`, "client");

            try {
                this._socket.connect();
            } catch (err) {
                logging.error(`Failed to connect to server: ${String(err)}`, "client");
            }
        }
    }

    /**
     * Sets a handler that gets called when a message arrives.
     *
     * @param msgHandler - The message handler to be called.
     */
    public setMessageHandler(msgHandler: ClientMessageHandler): void {
        this._messageHandler = msgHandler;
    }

    /**
     * Sends a message to the server (if connected).
     *
     * For this, the message will be encoded as *JSON* first.
     *
     * @param msg - The message to send.
     */
    public sendMessage(msg: Message): void {
        if (this._socket.connected) {
            logging.debug(`Sending message: ${String(msg)}`, "client");
            this._socket.emit(msg.name, msg.convertToJSON());
        }
    }

    private onConnect(): void {
        ClientConnectedEvent.build(this._messageBuilder).emit(Channel.local());

        logging.info("Connected to server", "client");
    }

    private onConnectError(reason: any): void {
        ClientConnectionErrorEvent.build(this._messageBuilder, String(reason)).emit(Channel.local());

        logging.warning("Unable to connect to server", "client", { reason: String(reason) });
    }

    private onDisconnect(): void {
        ClientDisconnectedEvent.build(this._messageBuilder).emit(Channel.local());

        logging.info("Disconnected from server", "client");
    }

    private onMessage(msgName: string, data: string): void {
        if (this._messageHandler) {
            this._messageHandler(msgName, data);
        }
    }

    private getAuthentication(): Record<string, any> {
        return { "component_id": this._compID.toString() };
    }
}
