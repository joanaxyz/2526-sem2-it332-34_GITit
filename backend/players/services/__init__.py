from players.models import Player


def get_or_create_player(user) -> Player:
    """Resolves ``user``'s Player, memoized on the user instance for the
    lifetime of one request so repeated lookups in the same call tree (e.g.
    walking every chapter in a track) cost one query, not N."""
    cached = getattr(user, "_cached_player", None)
    if cached is not None:
        return cached
    player, _created = Player.objects.get_or_create(user=user)
    user._cached_player = player
    return player
