import re
import requests
from config import Config


REPO_PATTERN = re.compile(
    r"(?:https?://github\.com/)?([a-zA-Z0-9._-]+)/([a-zA-Z0-9._-]+?)(?:\.git)?/?$"
)


def parse_repo_url(url):
    m = REPO_PATTERN.match(url.strip())
    if not m:
        return None
    return m.group(1), m.group(2)


def api_headers(token=None):
    h = {"Accept": "application/vnd.github.v3+json"}
    t = token or Config.GITHUB_TOKEN
    if t:
        h["Authorization"] = f"Bearer {t}"
    return h


def list_repo_files(owner, repo, path="", token=None):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    r = requests.get(url, headers=api_headers(token), timeout=Config.REQUEST_TIMEOUT)
    r.raise_for_status()
    return r.json()


def get_file_content(owner, repo, filepath, token=None):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{filepath}"
    r = requests.get(url, headers=api_headers(token), timeout=Config.REQUEST_TIMEOUT)
    r.raise_for_status()
    data = r.json()
    import base64
    if data.get("encoding") == "base64":
        return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
    return data.get("content", "")


def get_repo_default_branch(owner, repo, token=None):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    r = requests.get(url, headers=api_headers(token), timeout=Config.REQUEST_TIMEOUT)
    r.raise_for_status()
    return r.json().get("default_branch", "main")