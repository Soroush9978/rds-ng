/**
 * All known component types.
 */
export const enum ComponentType {
    Infrastructure = "infra",
    Web = "web",
    Connector = "connector",
}

/**
 * All known component units.
 */
export const enum ComponentUnit {
    // Infrastructure
    Server = "server",
    Gate = "gate",

    // Web
    Frontend = "frontend",
}
