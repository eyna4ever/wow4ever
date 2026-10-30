"""Trust only the client IP supplied by an explicitly configured immediate peer."""
from ipaddress import ip_address

from werkzeug.exceptions import BadRequest
from werkzeug.http import parse_list_header
from werkzeug.middleware.proxy_fix import ProxyFix


def trusted_client_ip(application, peers):
    if isinstance(peers, str):
        peers = [value.strip() for value in peers.split(',') if value.strip()]
    try:
        trusted = {ip_address(peer) for peer in peers}
    except ValueError as exc:
        raise RuntimeError('TRUSTED_PROXY_IPS exige des adresses IP exactes, sans réseau ni joker.') from exc
    forwarded = ProxyFix(application, x_for=1, x_proto=0, x_host=0, x_port=0, x_prefix=0)

    def middleware(environ, start_response):
        try:
            peer = ip_address(environ.get('REMOTE_ADDR', ''))
        except ValueError:
            return application(environ, start_response)
        if peer not in trusted:
            return application(environ, start_response)
        values = parse_list_header(environ.get('HTTP_X_FORWARDED_FOR', ''))
        if values:
            try:
                # Exactly one trusted hop; earlier header values are never used.
                ip_address(values[-1])
            except ValueError:
                return BadRequest('Adresse client du proxy invalide.')(environ, start_response)
        return forwarded(environ, start_response)

    return middleware
