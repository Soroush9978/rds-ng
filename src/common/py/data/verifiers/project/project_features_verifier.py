import typing

from common.py.data.verifiers.verifier import Verifier
from common.py.data.entities.project.features import ProjectFeatures, ProjectFeatureID


class ProjectFeaturesVerifier(Verifier):
    """
    Verifies project features.
    """

    def __init__(
        self,
        project_features: ProjectFeatures,
        *,
        selected_features: typing.List[ProjectFeatureID] | None = None,
    ):
        self._project_features = project_features
        self._selected_features = selected_features

    def verify_create(self) -> None:
        self._verify_features()

    def verify_update(self) -> None:
        self._verify_features()

    def verify_delete(self) -> None:
        pass

    def _verify_features(self) -> None:
        def is_selected(feature_id: ProjectFeatureID) -> bool:
            return (
                self._selected_features is None or feature_id in self._selected_features
            )

        from ..entities.project.features import (
            MetadataFeature,
            DataManagementPlanFeature,
        )

        # Important! When adding new features, include them here as well
        if is_selected(MetadataFeature.feature_id):
            self._verify_metadata_feature()
        if is_selected(DataManagementPlanFeature.feature_id):
            self._verify_dmp_feature()

    def _verify_metadata_feature(self) -> None:
        # TODO
        pass

    def _verify_dmp_feature(self) -> None:
        # TODO
        pass
