import { ComponentType, ComponentUnit } from "@common/component/ComponentIDs";
import { WebComponent } from "@common/component/WebComponent";
import { Service } from "@common/services/Service";
import { UnitID } from "@common/utils/UnitID";

import { registerProjectFeatures } from "@/features/Features";
import { getFrontendSettings } from "@/settings/FrontendSettings";
import { FrontendUserInterface } from "@/ui/FrontendUserInterface";

import createFrontendService from "@/services/FrontendService";
import createProjectsService from "@/services/ProjectsService";

import Frontend from "@/ui/Frontend.vue";

/**
 * The main frontend component class.
 */
export class FrontendComponent extends WebComponent<FrontendUserInterface> {
    private _frontendService: Service | null = null;
    private _projectsService: Service | null = null;

    public constructor() {
        super(import.meta.env, new UnitID(ComponentType.Web, ComponentUnit.Frontend), Frontend, FrontendUserInterface);

        this.addFrontendSettings();

        registerProjectFeatures();
    }

    public run(): void {
        super.run();

        // Create frontend-specific services
        this._frontendService = createFrontendService(this);
        this._projectsService = createProjectsService(this);
    }

    private addFrontendSettings(): void {
        this.data.config.addDefaults(getFrontendSettings());
    }

    /**
     * The main frontend service.
     */
    public get frontendService(): Service {
        if (!this._frontendService) {
            throw new Error("Tried to access the frontend service before its creation");
        }
        return this._frontendService;
    }

    /**
     * The projects service.
     */
    public get projectsService(): Service {
        if (!this._projectsService) {
            throw new Error("Tried to access the projects service before its creation");
        }
        return this._projectsService;
    }

    /**
     * The global ``FrontendComponent`` instance via Vue's injection mechanism.
     *
     * @throws Error - If no instance has been created.
     */
    public static inject(): FrontendComponent {
        return super.injectComponent<FrontendComponent>();
    }
}
