import { ListProjectsCommand } from "@common/api/project/ProjectCommands";
import { CommandComposer } from "@common/core/messaging/composers/CommandComposer";
import { ActionState } from "@common/ui/actions/ActionBase";
import { ActionNotifier } from "@common/ui/actions/notifiers/ActionNotifier";
import { OverlayNotifier } from "@common/ui/actions/notifiers/OverlayNotifier";
import { OverlayNotificationType } from "@common/ui/notifications/OverlayNotifications";

import { FrontendCommandAction } from "@/ui/actions/FrontendCommandAction";

/**
 * Action to retrieve all projects.
 */
export class ListProjectsAction extends FrontendCommandAction<ListProjectsCommand, CommandComposer<ListProjectsCommand>> {
    public prepare(): CommandComposer<ListProjectsCommand> {
        this.addDefaultNotifications();

        this._composer = ListProjectsCommand.build(this.messageBuilder).timeout(this._regularTimeout);
        return this._composer;
    }

    private addDefaultNotifications(): void {
        this.addNotifier(
            ActionState.Executing,
            new OverlayNotifier(OverlayNotificationType.Info, "Fetching projects", "Your projects are being downloaded...")
        );
        this.addNotifier(
            ActionState.Done,
            new OverlayNotifier(OverlayNotificationType.Success, "Fetching projects", "Your projects have been downloaded.")
        );
        this.addNotifier(
            ActionState.Failed,
            new OverlayNotifier(OverlayNotificationType.Error, "Error fetching projects", `An error occurred while downloading your projects: ${ActionNotifier.MessagePlaceholder}.`, true)
        );
    }
}
