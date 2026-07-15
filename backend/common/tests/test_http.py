from django.test import RequestFactory, override_settings

from common.http import get_client_ip


def test_client_ip_ignores_forwarded_header_by_default():
    request = RequestFactory().get(
        "/", REMOTE_ADDR="10.0.0.10", HTTP_X_FORWARDED_FOR="203.0.113.8"
    )
    assert get_client_ip(request) == "10.0.0.10"


@override_settings(
    DJANGO_TRUST_PROXY_HEADERS=True,
    DJANGO_TRUSTED_PROXY_IPS=["10.0.0.0/8"],
)
def test_client_ip_uses_forwarded_chain_from_trusted_proxy():
    request = RequestFactory().get(
        "/",
        REMOTE_ADDR="10.0.0.10",
        HTTP_X_FORWARDED_FOR="203.0.113.8, 10.0.0.9",
    )
    assert get_client_ip(request) == "203.0.113.8"


@override_settings(
    DJANGO_TRUST_PROXY_HEADERS=True,
    DJANGO_TRUSTED_PROXY_IPS=["10.0.0.0/8"],
)
def test_client_ip_rejects_forwarded_header_from_untrusted_peer():
    request = RequestFactory().get(
        "/", REMOTE_ADDR="198.51.100.20", HTTP_X_FORWARDED_FOR="203.0.113.8"
    )
    assert get_client_ip(request) == "198.51.100.20"
