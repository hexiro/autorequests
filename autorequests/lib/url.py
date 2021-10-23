import urllib.parse
from typing import Dict, Optional


class URL:

    def __init__(self, url: str):
        """
        Uniform Resource Locator (URL) as per
        <scheme>://<net_loc>/<path>;<params>?<query>#<fragment>
        """
        # https://www.rfc-editor.org/rfc/rfc1808.html#section-2.1
        # urlsplit automatically appends `params` to the end of path
        parsed = urllib.parse.urlsplit(url)
        self._url: str = url
        self._protocol: str = parsed.scheme
        self._path: str = parsed.path
        self._query = dict(urllib.parse.parse_qsl(parsed.query, keep_blank_values=True))
        self._fragment = parsed.fragment

        # <user>:<password>@<host>:<port>
        # https://www.rfc-editor.org/rfc/rfc1738#section-3.1
        network_location = parsed.netloc
        self._username: Optional[str] = None
        self._password: Optional[str] = None
        self._domain: str
        # it would also make sense to default this to 80
        # None means that there is none set explicitly in the url, however
        self._port: Optional[int] = None

        host: str = network_location
        if "@" in network_location:
            credentials, host = network_location.split("@", maxsplit=1)
            self._username, self._password = credentials.split(":", maxsplit=1)
        if ":" in host:
            self._domain, port = host.split(":", maxsplit=1)
            if port.isdigit():
                self._port = int(port)
        else:
            self._domain = host

    def __repr__(self):
        return f"<URL {self.url}>"

    def __eq__(self, other):
        if not isinstance(other, URL):
            return NotImplemented
        return self.url == other.url

    def __hash__(self):
        return hash(self.url)

    @property
    def url(self) -> str:
        return self._url

    @property
    def protocol(self) -> str:
        return self._protocol

    @property
    def username(self) -> Optional[str]:
        return self._username

    @property
    def password(self) -> Optional[str]:
        return self._password

    @property
    def domain(self) -> str:
        return self._domain

    @property
    def port(self) -> Optional[int]:
        return self._port

    @property
    def path(self) -> str:
        return self._path

    @property
    def query(self) -> Dict[str, str]:
        return self._query

    @property
    def fragment(self) -> str:
        return self._fragment
