from scenarios.models import ScenarioSession, ScenarioSkillFocus, ScenarioVariant


class VariantSelectionService:
    def select_variant(
        self,
        *,
        user,
        scenario: ScenarioSkillFocus,
        prior_session: ScenarioSession | None = None,
    ) -> ScenarioVariant:
        variants = list(scenario.variants.filter(is_published=True).order_by("id"))
        if not variants:
            raise ValueError("Scenario has no published variants.")
        if prior_session is None:
            return variants[0]
        for variant in variants:
            if variant.structure_signature != prior_session.variant.structure_signature:
                return variant
        return variants[0]
