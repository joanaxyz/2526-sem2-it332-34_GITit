import time

from common.agent_debug_log import agent_debug_log
from scenarios.builders import ScenarioVariantBuildError
from scenarios.models import DifficultyInstance, ScenarioSession, ScenarioVariant


class VariantSelectionService:
    def select_variant(
        self,
        *,
        user,
        difficulty_instance: DifficultyInstance,
        prior_session: ScenarioSession | None = None,
        published_variants: list[ScenarioVariant] | None = None,
    ) -> ScenarioVariant:
        # #region agent log
        select_t0 = time.perf_counter()
        # #endregion
        variants = published_variants or list(
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
        tried_keys = self._tried_variant_keys(
            user=user,
            difficulty_instance=difficulty_instance,
        )
        # #region agent log
        agent_debug_log(
            location="retries/services.py:select_variant",
            message="select_variant_retry_path",
            data={
                "elapsed_ms": round((time.perf_counter() - select_t0) * 1000, 2),
                "variant_count": len(variants),
                "tried_key_count": len(tried_keys),
            },
            hypothesis_id="C",
        )
        # #endregion
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

        tried_keys = self._tried_variant_keys(
            user=user,
            difficulty_instance=difficulty_instance,
            exclude_session_id=exclude_session_id,
        )
        return self.is_loopback_from_keys(
            variants=variants,
            selected_variant=selected_variant,
            tried_keys=tried_keys,
        )

    def is_loopback_from_keys(
        self,
        *,
        variants: list[ScenarioVariant],
        selected_variant: ScenarioVariant,
        tried_keys: set[str],
    ) -> bool:
        if len(variants) <= 1:
            return False
        available_keys = {self._identity(variant) for variant in variants}
        return (
            len(tried_keys.intersection(available_keys)) >= len(available_keys)
            and self._identity(selected_variant) in tried_keys
        )

    def _tried_variant_keys(
        self,
        *,
        user,
        difficulty_instance: DifficultyInstance,
        exclude_session_id: int | None = None,
    ) -> set[str]:
        sessions_qs = ScenarioSession.objects.filter(
            user=user,
            difficulty_instance=difficulty_instance,
        ).exclude(variant_id__isnull=True)
        if exclude_session_id is not None:
            sessions_qs = sessions_qs.exclude(id=exclude_session_id)
        variant_ids = sessions_qs.values_list("variant_id", flat=True).distinct()
        if not variant_ids:
            return set()
        variants = ScenarioVariant.objects.filter(id__in=variant_ids)
        return {self._identity(variant) for variant in variants}

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
