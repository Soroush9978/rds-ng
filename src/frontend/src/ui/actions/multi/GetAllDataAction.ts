import { FrontendComponent } from "@/component/FrontendComponent";
import { ListConnectorsAction } from "@/ui/actions/connector/ListConnectorsAction";
import { ListProjectsAction } from "@/ui/actions/project/ListProjectsAction";
import { GetUserConfigurationAction } from "@/ui/actions/user/GetUserConfigurationAction";
import { ActionState } from "@common/ui/actions/ActionBase";
import { MultiAction } from "@common/ui/actions/MultiAction";
import { ActionNotifier } from "@common/ui/actions/notifiers/ActionNotifier";
import { OverlayNotifier } from "@common/ui/actions/notifiers/OverlayNotifier";
import { OverlayNotificationType } from "@common/ui/notifications/OverlayNotifications";

/**
 * Multi-action to fetch all data from the server.
 */
export class GetAllDataAction extends MultiAction {
    public prepare(comp: FrontendComponent): void {
        this.prepareNotifiers();

        const listConAction = new ListConnectorsAction(comp, true);
        const getUserConfigAction = new GetUserConfigurationAction(comp, true);
        const listProjAction = new ListProjectsAction(comp, true);

        listConAction.prepare();
        getUserConfigAction.prepare();
        listProjAction.prepare();

        this.addActions([listConAction, getUserConfigAction, listProjAction]);
    }

    protected addDefaultNotifiers(): void {
        this.addNotifier(
            ActionState.Executing,
            new OverlayNotifier(OverlayNotificationType.Info, "Fetching data", "The data are being downloaded...")
        );
        this.addNotifier(
            ActionState.Done,
            new OverlayNotifier(OverlayNotificationType.Success, "Fetching data", "All data have been downloaded.")
        );
        this.addNotifier(
            ActionState.Failed,
            new OverlayNotifier(OverlayNotificationType.Error, "Error fetching data", `An error occurred while downloading the data: ${ActionNotifier.MessagePlaceholder}.`, true)
        );
    }
}
