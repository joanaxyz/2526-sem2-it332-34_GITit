from scenarios.builders import RuntimeScenarioBuilder, ScenarioVariantBuildError
from scenarios.models import DifficultyInstance, ScenarioSession, ScenarioVariant


class VariantSelectionService:
    def select_variant(
        self,
        *,
        user,
        difficulty_instance: DifficultyInstance,
        prior_session: ScenarioSession | None = None,
    ) -> ScenarioVariant:
        if difficulty_instance.generation_blueprints.filter(is_published=True).exists():
            return RuntimeScenarioBuilder().generate_variant(
                user=user,
                difficulty_instance=difficulty_instance,
                prior_session=prior_session,
            )

        variants = list(difficulty_instance.variants.filter(is_published=True).order_by("id"))
        if not variants:
            raise ScenarioVariantBuildError("Difficulty instance has no published variants.")
        if prior_session is None:
            return variants[0]
        for variant in variants:
            if variant.structure_signature != prior_session.variant.structure_signature:
                return variant
        return variants[0]

    def changed_between(self, *, prior: ScenarioVariant, current: ScenarioVariant) -> bool:
        if current.variant_fingerprint or prior.variant_fingerprint:
            return current.variant_fingerprint != prior.variant_fingerprint
        if current.parameter_context or prior.parameter_context:
            return current.parameter_context != prior.parameter_context
        return current.id != prior.id
