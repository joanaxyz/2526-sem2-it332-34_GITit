from __future__ import annotations

from functools import lru_cache
from ipaddress import ip_address, ip_network

from django.conf import settings


def _valid_ip(value: str | None) -> str | None:
    if not value:
        return None
    candidate = value.strip()
    try:
        return str(ip_address(candidate))
    except ValueError:
        return None


@lru_cache(maxsize=16)
def _trusted_networks(values: tuple[str, ...]):
    networks = []
    for value in values:
        try:
            networks.append(ip_network(value, strict=False))
        except ValueError:
            continue
    return networks


def get_client_ip(request) -> str | None:
    """Return the client IP without trusting arbitrary forwarding headers.

    X-Forwarded-For is considered only when proxy trust is enabled and the
    direct peer belongs to an explicitly configured trusted proxy network.
    """

    remote = _valid_ip(request.META.get("REMOTE_ADDR"))
    if not getattr(settings, "DJANGO_TRUST_PROXY_HEADERS", False) or remote is None:
        return remote

    networks = _trusted_networks(tuple(getattr(settings, "DJANGO_TRUSTED_PROXY_IPS", [])))
    if not networks or not any(ip_address(remote) in network for network in networks):
        return remote

    # Walk from the known peer. Never skip an invalid boundary or select an
    # attacker-controlled leftmost value when the entire chain is trusted.
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")
    for value in reversed(forwarded):
        candidate = _valid_ip(value)
        if candidate is None:
            return remote
        parsed = ip_address(candidate)
        if not any(parsed in network for network in networks):
            return candidate
    return remote
