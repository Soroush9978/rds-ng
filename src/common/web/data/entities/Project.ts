import { Type } from "class-transformer";

import { type ProjectID } from "./EntityTypes";
import { ProjectFeatures } from "./features/ProjectFeatures";

/*
 * The status of a project.
 */
export const enum ProjectStatus {
    Active = 0x0,
    Deleted = 0xff,
}

/**
 * Data for a single **Project**.
 *
 * @param project_id - The unique project identifier.
 * @param creation_time - A UNIX timestamp of the project creation time.
 * @param title - The title of the project.
 * @param description - An optional project description.
 * @param status - The project status.
 * @param features - All project features data.
 */
export class Project {
    public readonly project_id: ProjectID;

    public readonly creation_time: number;

    public readonly title: string;
    public readonly description: string;

    public readonly status: ProjectStatus = ProjectStatus.Active;

    // @ts-ignore
    @Type(() => ProjectFeatures)
    public readonly features: ProjectFeatures = new ProjectFeatures();

    public constructor(projectID: ProjectID, creationTime: number, title: string, description: string = "", features: ProjectFeatures = new ProjectFeatures()) {
        this.project_id = projectID;

        this.creation_time = creationTime;

        this.title = title;
        this.description = description;

        this.features = features;
    }
}
