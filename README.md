# CF Attack Simulator v2

Fires realistic, industry-specific HTTP attack campaigns at a target URL to generate meaningful security events in **Cloudflare WAF** and **SentinelOne AI-SIEM**.

Three verticals · Five phases each · Two demo modes

| Industry | Campaign | Phases |
|---|---|---|
| 🏦 Financial Services | Operation Wire Fraud | Recon → Enumeration → Credential Stuffing → SQLi → Log4Shell |
| 💊 Healthcare | Operation HIPAA Breach | Recon → PHI Probe → EHR Stuffing → SQLi → Spring4Shell |
| ☁️ SaaS / Tech | Operation Tenant Escape | Recon → API Key Theft → Privilege Escalation → IDOR → Log4Shell |

**AUTHORIZED USE ONLY** — only target systems you own or have written permission to test.

---

## Demo Modes

| Mode | Use when | Speed | Phases |
|---|---|---|---|
| 🌙 Pre-seed | Night before the demo | Fast (0.05–0.4s between requests) | Choose 1–5 or all |
| 📡 Live | During the presentation | Slow drip (3–8s, batches of 5 every 30s) | All 5 auto-advance every 3 min |

---

## DigitalOcean App Platform Deployment

### First-time setup

1. Fork or push this repo to GitHub
2. Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps) → **Create App**
3. Connect your GitHub repo (`cf-attack-sim-v2`)
4. App Platform auto-detects the Python app via `Procfile` — no extra config needed
5. Under **Environment Variables**, add:

   | Key | Value |
   |---|---|
   | `SECRET_KEY` | Random 32-char hex string |
   | `APP_USERNAME` | `admin` (or your choice) |
   | `APP_PASSWORD` | A strong password |
   | `TARGET_URL` | `https://mihirkansagra.com` |

6. (Optional) Set a custom domain, e.g. `cloudflare.mihirkansagra.com`
7. HTTPS is automatic — no certbot or Nginx config needed
8. Click **Deploy**

### Subsequent deployments (auto-deploy)

App Platform watches your `main` branch. Every push auto-deploys in ~2 minutes:

```bash
git add .
git commit -m "your change"
git push
# App Platform picks it up automatically
```

---

## Local Development

```bash
git clone https://github.com/thatdudemihir/cf-attack-sim-v2.git
cd cf-attack-sim-v2
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env — set SECRET_KEY, APP_USERNAME, APP_PASSWORD, TARGET_URL
python app.py
# Open http://localhost:5000
```

---

## Project Structure

```
cf-attack-sim-v2/
├── app.py                      # Flask app — polling, launch, stop, status
├── Procfile                    # App Platform process definition
├── runtime.txt                 # Python 3.11 for App Platform
├── requirements.txt            # flask, gunicorn, requests, urllib3
├── .env.example                # Local dev template
│
├── attacks/
│   ├── engine.py               # Core HTTP sender (shared by all scenarios)
│   ├── payloads/
│   │   ├── financial.py        # Meridian Bank payloads
│   │   ├── healthcare.py       # MedCore Health payloads
│   │   └── saas.py             # CloudMatrix SaaS payloads
│   └── scenarios/
│       ├── financial.py        # 5-phase Financial campaign
│       ├── healthcare.py       # 5-phase Healthcare campaign
│       └── saas.py             # 5-phase SaaS campaign
│
└── templates/
    ├── login.html              # Login page
    └── index.html              # v2 UI — industry selector, phase timeline, talking points
```

---

## Demo Script

### Pre-seed (night before)

1. Log in, select your industry vertical
2. Set **Pre-seed** mode, **High** volume, **All Phases**
3. Click **Launch Campaign** — ~400 requests fire in 2–3 minutes
4. Repeat for other industries if desired

### Live (during presentation)

1. Select the industry matching your prospect's vertical
2. Switch to **Live Mode**
3. Click **Start Live Demo**
4. Narrate each phase using the **talking points panel** (updates automatically)
5. Phases auto-advance every 3 minutes — enough time to show Cloudflare + SentinelOne between phases
6. Hit **Stop** at any point

### Where to look

| Tool | What to show |
|---|---|
| Cloudflare → Security → Events | WAF blocks, bot scores, CVE signature rules |
| SentinelOne AI-SIEM | Correlated campaign incident, kill chain, threat actor attribution |
| SentinelOne Hyperautomation | Automated response playbooks triggered per phase |

---

## Environment Variables

All config is read from environment variables (set in App Platform dashboard for production, `.env` file for local dev).

| Variable | Description |
|---|---|
| `SECRET_KEY` | Flask session signing key — use a random 32-char hex string |
| `APP_USERNAME` | Login username |
| `APP_PASSWORD` | Login password |
| `TARGET_URL` | Target URL (must be a domain you own) |
