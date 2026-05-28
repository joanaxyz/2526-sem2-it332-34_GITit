from scenarios.builders import ScenarioVariantBuildError
from scenarios.models import DifficultyInstance, ScenarioSession, ScenarioVariant


class VariantSelectionService:
    def select_variant(
        self,
        *,
        user,
        difficulty_instance: DifficultyInstance,
        prior_session: ScenarioSession | None = None,
    ) -> ScenarioVariant:
        variants = list(
            difficulty_instance.variants.filter(is_published=True).order_by(
                "semantic_key",
                "id",
            )
        )
        if not variants:
            raise ScenarioVariantBuildError(
                "Difficulty instance has no published authored variants."
            )
        if prior_session is None:
            return variants[0]

        prior_key = self._identity(prior_session.variant)
        tried_keys = {
            self._identity(session.variant)
            for session in ScenarioSession.objects.select_related("variant").filter(
                user=user,
                difficulty_instance=difficulty_instance,
            )
            if session.variant_id
        }
        for variant in variants:
            identity = self._identity(variant)
            if identity != prior_key and identity not in tried_keys:
                return variant
        for variant in variants:
            identity = self._identity(variant)
            if identity != prior_key:
                return variant
        return variants[0]

    def changed_between(self, *, prior: ScenarioVariant, current: ScenarioVariant) -> bool:
        current_key = self.variant_identity(current)
        prior_key = self.variant_identity(prior)
        if current_key or prior_key:
            return current_key != prior_key
        if current.parameter_context or prior.parameter_context:
            return current.parameter_context != prior.parameter_context
        return current.id != prior.id

    def variant_identity(self, variant: ScenarioVariant) -> str:
        return self._identity(variant)

    def is_loopback_selection(
        self,
        *,
        user,
        difficulty_instance: DifficultyInstance,
        selected_variant: ScenarioVariant,
        prior_session: ScenarioSession | None,
        exclude_session_id: int | None = None,
    ) -> bool:
        if prior_session is None:
            return False
        variants = list(
            difficulty_instance.variants.filter(is_published=True).order_by(
                "semantic_key",
                "id",
            )
        )
        if len(variants) <= 1:
            return False

        available_keys = {self._identity(variant) for variant in variants}
        sessions_qs = ScenarioSession.objects.select_related("variant").filter(
            user=user,
            difficulty_instance=difficulty_instance,
        )
        if exclude_session_id is not None:
            sessions_qs = sessions_qs.exclude(id=exclude_session_id)
        tried_keys = {
            self._identity(session.variant)
            for session in sessions_qs
            if session.variant_id
        }
        return (
            len(tried_keys.intersection(available_keys)) >= len(available_keys)
            and self._identity(selected_variant) in tried_keys
        )

    def _identity(self, variant: ScenarioVariant) -> str:
        if variant.semantic_key:
            return variant.semantic_key
        if variant.case_id:
            return f"case:{variant.case_id}"
        case_id = (variant.parameter_context or {}).get("case_id")
        if case_id:
            return f"case:{case_id}"
        if variant.structure_signature:
            return f"structure:{variant.structure_signature}"
        return f"id:{variant.id}"
