from scenarios.models import DifficultyInstance, ScenarioSession, ScenarioVariant


class VariantSelectionService:
    def select_variant(
        self,
        *,
        user,
        difficulty_instance: DifficultyInstance,
        prior_session: ScenarioSession | None = None,
    ) -> ScenarioVariant:
        variants = list(difficulty_instance.variants.filter(is_published=True).order_by("id"))
        if not variants:
            raise ValueError("Difficulty instance has no published variants.")
        if prior_session is None:
            return variants[0]
        for variant in variants:
            if variant.structure_signature != prior_session.variant.structure_signature:
                return variant
        return variants[0]
