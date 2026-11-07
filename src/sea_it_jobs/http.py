import time
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

USER_AGENT = "VietnamITMarketResearch/1.0 (+educational data engineering project)"


class HttpClient:
    def __init__(self, delay: float = 1.0):
        if delay < 0.5:
            raise ValueError("Request interval must be at least 0.5 seconds")
        self.delay = delay
        self.last_request = 0.0
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET",),
            respect_retry_after_header=True,
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retry))
        self.robots = {}

    def get(self, url: str, *, check_robots: bool = False):
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.username or parsed.password:
            raise ValueError("Only HTTPS URLs without embedded credentials are supported")
        if check_robots:
            origin = f"https://{parsed.netloc}"
            if origin not in self.robots:
                response = self.get(origin + "/robots.txt")
                rules = RobotFileParser()
                rules.parse(response.text.splitlines())
                self.robots[origin] = rules
            if not self.robots[origin].can_fetch(USER_AGENT, url):
                raise ValueError("Source robots.txt disallows this path")
        time.sleep(max(0, self.delay - (time.monotonic() - self.last_request)))
        self.last_request = time.monotonic()
        response = self.session.get(url, timeout=(10, 45), allow_redirects=True)
        response.raise_for_status()
        if urlparse(response.url).netloc != parsed.netloc:
            raise ValueError("Unexpected cross-host redirect")
        return response
