import { Message, Trace } from "./Message";

// @ts-ignore
import { v4 as uuidv4 } from "uuid";

/**
 * Used when a command failed.
 */
export enum CommandFailType {
    None = 0,
    Timeout,
    Exception,
    Unknown
}

/**
 * A command reply message.
 *
 * Every command needs to receive a reply in the form of a ``CommandReply`` message. The reply contains
 * information about its ``success``, as well as a text message which is usually used to describe reasons for
 * failures.
 */
export class CommandReply extends Message {
    public readonly success: boolean = true;
    public readonly message: string = "";

    public readonly unique: Trace = uuidv4();
}

export type CommandDoneCallback = (Command, boolean, string) => void;
export type CommandFailCallback = (CommandFailType, string) => void;
