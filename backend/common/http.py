from __future__ import annotations

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


def _trusted_networks():
    networks = []
    for value in getattr(settings, "DJANGO_TRUSTED_PROXY_IPS", []):
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

    networks = _trusted_networks()
    if not networks or not any(ip_address(remote) in network for network in networks):
        return remote

    forwarded = [
        valid
        for item in request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")
        if (valid := _valid_ip(item)) is not None
    ]
    if not forwarded:
        return remote

    chain = [*forwarded, remote]
    for candidate in reversed(chain):
        parsed = ip_address(candidate)
        if not any(parsed in network for network in networks):
            return candidate
    return forwarded[0]
