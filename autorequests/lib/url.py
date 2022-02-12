from __future__ import annotations

import urllib.parse
from typing import Any

from ..utilities import parse_url_encoded


class URL:
    def __init__(self, url: str):
        """
        Uniform Resource Locator (URL) as per
        <scheme>://<net_loc>/<path>;<params>?<query>#<fragment>
        """
        # https://www.rfc-editor.org/rfc/rfc1808.html#section-2.1
        # urlsplit automatically appends `params` to the end of path
        parsed = urllib.parse.urlsplit(url)
        self._protocol: str = parsed.scheme
        self._path: str = parsed.path
        self._query: dict[str, str] = parse_url_encoded(parsed.query)
        self._fragment: str = parsed.fragment

        # <user>:<password>@<host>:<port>
        # https://www.rfc-editor.org/rfc/rfc1738#section-3.1
        self._network_location: str = parsed.netloc

        self._username: str | None = None
        self._password: str | None = None
        self._domain: str
        self._domain_name: str
        self._subdomain: str | None = None
        # it would also make sense to default this to 80
        # None means that there is none set explicitly in the url, however
        self._port: int | None = None

        self._username, self._password, host = self._credentials(self._network_location)
        self._domain, self._port = self._domain_and_port(host)

        # subdomain, domain (this might break with domains like .co.uk)
        if self._domain.count(".") >= 2:
            self._subdomain, self._domain = self._domain.split(".", maxsplit=1)

        # domain name
        self._domain_name = self._domain.split(".")[0]

    def __repr__(self) -> str:
        return f"<URL {self.url}>"

    def __str__(self) -> str:
        return self.url

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, URL):
            return NotImplemented
        return self.url == other.url

    def __hash__(self) -> int:
        return hash(self.url)

    @staticmethod
    def _domain_and_port(host: str) -> tuple[str, int | None]:
        if ":" not in host:
            return host, None
        split = host.split(":", maxsplit=1)
        domain = split[0]
        port = int(split[1]) if split[1].isdigit() else None
        return domain, port

    @staticmethod
    def _credentials(network_location: str) -> tuple[str | None, str | None, str]:
        if "@" not in network_location:
            return None, None, network_location
        credentials, host = network_location.split("@", maxsplit=1)
        username, password = credentials.split(":", maxsplit=1)
        return username, password, host

    @property
    def url(self) -> str:
        """url without query string params"""
        return f"{self.protocol}://{self.network_location}{self.path}{'#'+self.fragment if self.fragment else ''}"

    @property
    def protocol(self) -> str:
        return self._protocol

    @property
    def path(self) -> str:
        return self._path

    @property
    def query(self) -> dict[str, str]:
        return self._query

    @property
    def fragment(self) -> str:
        return self._fragment

    @property
    def network_location(self) -> str:
        return self._network_location

    @property
    def username(self) -> str | None:
        return self._username

    @property
    def password(self) -> str | None:
        return self._password

    @property
    def domain(self) -> str:
        return self._domain

    @property
    def domain_name(self) -> str:
        return self._domain_name

    @property
    def subdomain(self) -> str | None:
        return self._subdomain

    @property
    def port(self) -> int | None:
        return self._port
