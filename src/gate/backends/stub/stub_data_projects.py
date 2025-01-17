import time


def fill_stub_data_projects() -> None:
    """
    Adds some hardcoded data to the stub data storage.
    """
    from common.py.data.entities.project import Project, ProjectOptions

    from ...data.storage.memory import MemoryStoragePool

    pool = (
        MemoryStoragePool()
    )  # The memory storage pool uses shared data objects, so we can fill them using a new instance

    pool.project_storage.add(
        Project(
            project_id=pool.project_storage.next_id(),
            creation_time=time.time(),
            title="Our first project",
            description="This is our first attempt to create a project",
            options=ProjectOptions(
                optional_features=["metadata", "dmp"],
                ui={"optional_snapins": ["metadata", "dmp"]},
            ),
        )
    )
    pool.project_storage.add(
        Project(
            project_id=pool.project_storage.next_id(),
            creation_time=time.time(),
            title="Top-secret experiments",
            description="If you read this, the FBI is already on their way to you!",
            options=ProjectOptions(
                optional_features=["metadata", "dmp"],
                ui={"optional_snapins": ["metadata", "dmp"]},
            ),
        )
    )
    pool.project_storage.add(
        Project(
            project_id=pool.project_storage.next_id(),
            creation_time=time.time(),
            title="This is crap",
            description="To be honest, this project sucks. It is crap. Do not even look at it!",
            options=ProjectOptions(
                optional_features=["metadata"],
                ui={"optional_snapins": ["metadata"]},
            ),
        )
    )
    pool.project_storage.add(
        Project(
            project_id=pool.project_storage.next_id(),
            creation_time=time.time(),
            title="Sorry, but this project has a way too long title to be displayed",
            description="And frankly, the description should also be shorter. But that's not my fault, it is yours. Of course. BAH! Let me tell you this, never write such a LONG description, trust me, it displays totally crappy.",
            options=ProjectOptions(
                optional_features=["dmp"],
                ui={"optional_snapins": ["dmp"]},
            ),
        )
    )
    pool.project_storage.add(
        Project(
            project_id=pool.project_storage.next_id(),
            creation_time=time.time(),
            title="A fine project",
            description="Last but not least, a fine one.",
        )
    )
