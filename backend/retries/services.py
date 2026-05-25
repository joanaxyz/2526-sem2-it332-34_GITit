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
            if self._identity(variant) != prior_key:
                return variant
        return variants[0]

    def changed_between(self, *, prior: ScenarioVariant, current: ScenarioVariant) -> bool:
        current_key = self._identity(current)
        prior_key = self._identity(prior)
        if current_key or prior_key:
            return current_key != prior_key
        if current.parameter_context or prior.parameter_context:
            return current.parameter_context != prior.parameter_context
        return current.id != prior.id

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
