from challenges.models import ChallengeRun, ChallengeTrial, ChallengeTrialVariant


class VariantSelectionService:
    """Picks a trial-owned variant, rotating retries within the same trial."""

    def select_variant(
        self,
        *,
        player,
        trial: ChallengeTrial,
        prior_run: ChallengeRun | None = None,
        published_variants: list[ChallengeTrialVariant] | None = None,
        tried_variant_keys: set[str] | None = None,
    ) -> ChallengeTrialVariant | None:
        variants = published_variants or list(
            trial.variants.filter(is_published=True).order_by("semantic_key", "id")
        )
        if not variants:
            return None
        if prior_run is None:
            return variants[0]
        prior_key = self.variant_identity(prior_run.variant)
        tried_keys = tried_variant_keys if tried_variant_keys is not None else set()
        for variant in variants:
            identity = self.variant_identity(variant)
            if identity != prior_key and identity not in tried_keys:
                return variant
        for variant in variants:
            if self.variant_identity(variant) != prior_key:
                return variant
        return variants[0]

    def changed_between(self, *, prior, current) -> bool:
        if prior is None or current is None:
            return False
        return self.variant_identity(prior) != self.variant_identity(current)

    def is_loopback_from_keys(
        self,
        *,
        variants: list[ChallengeTrialVariant],
        selected_variant,
        tried_keys: set[str],
    ) -> bool:
        if len(variants) <= 1:
            return False
        available = {self.variant_identity(variant) for variant in variants}
        return (
            len(tried_keys.intersection(available)) >= len(available)
            and self.variant_identity(selected_variant) in tried_keys
        )

    def variant_identity(self, variant) -> str:
        return variant.semantic_key or f"id:{variant.id}"

    def _tried_variant_keys(self, *, player, trial: ChallengeTrial) -> set[str]:
        variant_ids = (
            ChallengeRun.objects.filter(player=player, challenge_trial=trial)
            .values_list("selected_variant_id", flat=True)
            .distinct()
        )
        return {
            self.variant_identity(variant)
            for variant in ChallengeTrialVariant.objects.filter(id__in=variant_ids)
        }
