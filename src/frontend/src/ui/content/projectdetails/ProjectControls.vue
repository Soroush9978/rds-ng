<script setup lang="ts">
import Button from "primevue/button";
import { toRefs } from "vue";

import { Project } from "@common/data/entities/project/Project";

import { FrontendComponent } from "@/component/FrontendComponent";
import { UpdateProjectAction } from "@/ui/actions/project/UpdateProjectAction";

const comp = FrontendComponent.inject();
const props = defineProps({
    project: {
        type: Project,
        required: true
    }
});
const { project } = toRefs(props);

function editProject() {
    const action = new UpdateProjectAction(comp);
    action.showEditDialog(project.value).then((data) => {
        action.prepare(project.value.project_id, data.title, data.description, data.options);
        action.execute();
    });
}
</script>

<template>
    <div>
        <Button
            severity="secondary"
            label="Project settings"
            icon="material-icons-outlined mi-engineering"
            icon-class="!text-3xl"
            @click="editProject"
        />
    </div>
</template>

<style scoped lang="scss">

</style>
