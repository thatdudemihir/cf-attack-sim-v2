"""
engine.py — Shared HTTP request sender used by all industry scenarios.
AUTHORIZED USE ONLY — only target systems you own or have permission to test.
"""

import random
import time

import requests
import urllib3
from requests.exceptions import RequestException

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

FAKE_IPS = [
    "185.220.101.47",   # Tor exit node
    "194.165.16.72",    # Eastern Europe
    "103.21.244.0",     # Asia Pacific
    "45.142.212.100",   # Russia
    "91.108.4.0",       # Telegram bot range
    "198.144.121.93",   # Known scanner range
    "212.102.63.0",
    "162.247.74.27",    # US Tor
    "77.247.181.162",   # Netherlands Tor
    "171.25.193.77",    # Sweden Tor
    "89.234.157.254",   # France
    "46.165.230.5",     # Germany
]


def _next_id(log_counter):
    log_counter[0] += 1
    return log_counter[0]


def send_request(url, method="GET", params=None, data=None, headers=None,
                 label="", log_buffer=None, log_counter=None, stop_flag=None,
                 phase=1, industry=""):
    """
    Fire one HTTP request and append result to log_buffer.
    Returns status code or 0 on error.
    """
    if stop_flag and stop_flag.is_set():
        return 0

    fake_ip = random.choice(FAKE_IPS)
    base_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "X-Forwarded-For": fake_ip,
        "X-Real-IP": fake_ip,
    }
    if headers:
        base_headers.update(headers)

    try:
        if method == "POST":
            resp = requests.post(url, data=data, headers=base_headers,
                                 timeout=8, allow_redirects=False, verify=False)
        else:
            resp = requests.get(url, params=params, headers=base_headers,
                                timeout=8, allow_redirects=False, verify=False)

        status = resp.status_code
        blocked = status in (403, 429, 444)

        entry = {
            "id": _next_id(log_counter) if log_counter else 0,
            "type": "blocked" if blocked else "passed",
            "method": method,
            "url": url,
            "status": status,
            "blocked": blocked,
            "label": label or str(params or data or "")[:80],
            "ip": fake_ip,
            "phase": phase,
            "industry": industry,
        }
        if log_buffer is not None:
            log_buffer.append(entry)
        return status

    except RequestException as exc:
        entry = {
            "id": _next_id(log_counter) if log_counter else 0,
            "type": "error",
            "method": method,
            "url": url,
            "status": 0,
            "blocked": False,
            "label": f"Connection error: {exc}",
            "ip": fake_ip,
            "phase": phase,
            "industry": industry,
        }
        if log_buffer is not None:
            log_buffer.append(entry)
        return 0


def log_phase_event(message, phase, industry, log_buffer, log_counter, entry_type="phase"):
    entry = {
        "id": _next_id(log_counter) if log_counter else 0,
        "type": entry_type,
        "phase": phase,
        "industry": industry,
        "message": message,
        "url": "",
        "method": "",
        "status": 0,
        "blocked": False,
        "label": message,
        "ip": "",
    }
    if log_buffer is not None:
        log_buffer.append(entry)


def sleep_between_requests(mode="preseed", custom_range=None):
    if custom_range:
        time.sleep(random.uniform(*custom_range))
    elif mode == "live":
        time.sleep(random.uniform(3, 8))
    else:
        time.sleep(random.uniform(0.05, 0.2))
