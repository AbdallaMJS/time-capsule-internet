from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse


def normalize_url(raw: str) -> str:
    raw = raw.strip()
    if not raw:
        raise ValueError("Please enter a website URL.")
    if not raw.startswith(("http://", "https://")):
        raw = "https://" + raw
    parsed = urlparse(raw)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("Please enter a valid public http/https URL.")
    return raw


def ensure_public_host(url: str) -> None:
    """Reject localhost/private/link-local/reserved destinations to reduce SSRF risk."""
    hostname = urlparse(url).hostname
    if not hostname:
        raise ValueError("Invalid host.")
    if hostname.lower() in {"localhost", "localhost.localdomain"}:
        raise ValueError("Local/private addresses are not allowed.")

    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror as exc:
        raise ValueError("The website address could not be resolved.") from exc

    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if any(
            (
                ip.is_private,
                ip.is_loopback,
                ip.is_link_local,
                ip.is_multicast,
                ip.is_reserved,
                ip.is_unspecified,
            )
        ):
            raise ValueError("Local/private network addresses are not allowed.")
