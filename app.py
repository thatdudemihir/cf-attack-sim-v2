"""
CF Attack Simulator v2
----------------------
Industry-specific attack campaigns for Cloudflare WAF + SentinelOne AI-SIEM demos.
Three verticals: Financial Services, Healthcare, SaaS/Tech.
Two modes: Pre-seed (fast, night before) and Live (slow drip, during presentation).

AUTHORIZED USE ONLY — only target systems you own or have permission to test.
"""

import collections
import os
import random
import threading
import time

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, session, url_for

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-before-deploying")

APP_USERNAME          = os.environ.get("APP_USERNAME", "admin")
APP_PASSWORD          = os.environ.get("APP_PASSWORD", "changeme")
TARGET_URL            = os.environ.get("TARGET_URL", "https://mihirkansagra.com")
NOVAMIND_TARGET_URL   = os.environ.get("NOVAMIND_TARGET_URL", "https://novamind.mihirkansagra.com")
NOVAMIND_INCIDENT_KEY = os.environ.get("NOVAMIND_INCIDENT_KEY", "")

# ── Global state — one attack at a time ─────────────────────────────────────

log_buffer    = collections.deque(maxlen=500)
log_counter   = [0]   # mutable list so threads share the same counter object
attack_running = False
current_phase  = 0
current_industry = None
stop_flag      = threading.Event()

# ── Live mode constants ──────────────────────────────────────────────────────

LIVE_INTERVAL_SECONDS  = 30
LIVE_PHASE_DURATION_SECONDS = 180
CTF_LIVE_PHASE_DURATION_SECONDS = 90   # 1.5 min per box for CTF live mode
LIVE_BATCH_SIZE = 5

# ── Pre-seed volume config ───────────────────────────────────────────────────

PRESEED_VOLUME = {
    "low":    {"count": 40,  "delay": (0.1, 0.4)},
    "medium": {"count": 150, "delay": (0.05, 0.2)},
    "high":   {"count": 400, "delay": (0.02, 0.1)},
}


# ── Scenario loader ──────────────────────────────────────────────────────────

def get_scenario(industry):
    if industry == "financial":
        from attacks.scenarios import financial
        return financial
    elif industry == "healthcare":
        from attacks.scenarios import healthcare
        return healthcare
    elif industry == "saas":
        from attacks.scenarios import saas
        return saas
    elif industry == "ctf":
        from attacks.scenarios import ctf
        return ctf
    raise ValueError(f"Unknown industry: {industry}")


def _signal_novamind_incident(active, title="", message="", severity="critical",
                               affected_services=None, started_at=None):
    """
    POST to NovaMind /api/incident to flip the status page during the CTF run.
    Called in a daemon thread so it never blocks the main attack loop.
    Silently fails if NOVAMIND_INCIDENT_KEY is not configured.
    """
    if not NOVAMIND_INCIDENT_KEY:
        return

    import requests as _req
    payload = {
        "key":               NOVAMIND_INCIDENT_KEY,
        "active":            active,
        "title":             title,
        "message":           message,
        "severity":          severity,
        "affected_services": affected_services or [],
        "started_at":        started_at,
    }
    try:
        _req.post(
            f"{NOVAMIND_TARGET_URL}/api/incident",
            json=payload,
            timeout=5,
            verify=False,
        )
    except Exception:
        pass


# ── Background workers ───────────────────────────────────────────────────────

def _target_url_for(industry):
    """Returns the correct target URL for the given industry/mode."""
    return NOVAMIND_TARGET_URL if industry == "ctf" else TARGET_URL


def run_preseed(industry, phases, volume):
    global attack_running, current_phase, current_industry
    scenario   = get_scenario(industry)
    cfg        = PRESEED_VOLUME.get(volume, PRESEED_VOLUME["low"])
    count_per_phase = max(cfg["count"] // len(phases), 10)
    target     = _target_url_for(industry)

    if industry == "ctf":
        threading.Thread(
            target=_signal_novamind_incident,
            args=(True,),
            kwargs={
                "title": "Elevated API Error Rate",
                "message": "We are investigating unusual traffic patterns affecting the Chat API and training data endpoints.",
                "severity": "critical",
                "affected_services": ["Chat API", "Model Inference", "DataVault"],
            },
            daemon=True,
        ).start()

    for phase_num in phases:
        if stop_flag.is_set():
            break
        current_phase = phase_num
        phase = scenario.PHASES[phase_num - 1]
        phase["fire_many"](count_per_phase, cfg["delay"], target,
                           log_buffer, log_counter, stop_flag)

    _finish_campaign()


def run_live_mode(industry):
    global attack_running, current_phase, current_industry
    from attacks.engine import log_phase_event

    scenario   = get_scenario(industry)
    num_phases = len(scenario.PHASES)
    target     = _target_url_for(industry)

    if industry == "ctf":
        threading.Thread(
            target=_signal_novamind_incident,
            args=(True,),
            kwargs={
                "title": "Active Security Incident",
                "message": "Our security team is investigating a sophisticated attack campaign targeting multiple services.",
                "severity": "critical",
                "affected_services": ["Chat API", "Model Inference", "API Gateway", "DataVault"],
            },
            daemon=True,
        ).start()

    for phase_num in range(1, num_phases + 1):
        if stop_flag.is_set():
            break

        current_phase = phase_num
        phase = scenario.PHASES[phase_num - 1]
        phase_start = time.time()

        log_phase_event(
            f"Phase {phase_num}: {phase['name']}",
            phase_num, industry, log_buffer, log_counter,
        )

        phase_duration = CTF_LIVE_PHASE_DURATION_SECONDS if industry == "ctf" else LIVE_PHASE_DURATION_SECONDS
        while not stop_flag.is_set():
            elapsed = time.time() - phase_start
            if elapsed >= phase_duration:
                break

            for _ in range(LIVE_BATCH_SIZE):
                if stop_flag.is_set():
                    break
                phase["fire_one"](target, log_buffer, log_counter, stop_flag)
                if not stop_flag.is_set():
                    time.sleep(random.uniform(3, 8))

            # Wait for next batch window
            batch_wait = 0
            while batch_wait < LIVE_INTERVAL_SECONDS and not stop_flag.is_set():
                time.sleep(1)
                batch_wait += 1

    _finish_campaign()


def _finish_campaign():
    global attack_running, current_phase
    attack_running = False
    from attacks.engine import log_phase_event
    log_phase_event(
        "Campaign complete. Check Cloudflare Security Events + SentinelOne AI-SIEM.",
        current_phase, current_industry, log_buffer, log_counter, entry_type="info",
    )
    if current_industry == "ctf":
        threading.Thread(
            target=_signal_novamind_incident, args=(False,), daemon=True
        ).start()


# ── Auth routes ──────────────────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == APP_USERNAME and password == APP_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("index"))
        return render_template("login.html", error="Invalid credentials. Try again.")
    return render_template("login.html", error=None)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ── Main UI ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("index.html", target=TARGET_URL, novamind_target=NOVAMIND_TARGET_URL)


# ── API: launch attack ───────────────────────────────────────────────────────

@app.route("/launch", methods=["POST"])
def launch():
    global attack_running, current_phase, current_industry, stop_flag

    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 401

    if attack_running:
        return jsonify({"error": "A campaign is already running. Use Stop first."}), 400

    data = request.get_json(silent=True) or {}
    industry = data.get("industry", "financial")
    mode = data.get("mode", "preseed")
    phase_param = data.get("phase", "full")
    volume = data.get("volume", "medium")

    if industry not in ("financial", "healthcare", "saas", "ctf"):
        return jsonify({"error": f"Unknown industry: {industry}"}), 400

    # Reset state
    log_buffer.clear()
    log_counter[0] = 0
    stop_flag.clear()
    attack_running = True
    current_industry = industry
    current_phase = 0

    if mode == "live":
        thread = threading.Thread(target=run_live_mode, args=(industry,), daemon=True)
    else:
        scenario = get_scenario(industry)
        num_phases = len(scenario.PHASES)
        if phase_param == "full":
            phases = list(range(1, num_phases + 1))
        else:
            phases = [int(phase_param)]
        thread = threading.Thread(target=run_preseed, args=(industry, phases, volume), daemon=True)

    thread.start()
    return jsonify({"status": "started", "industry": industry, "mode": mode})


# ── API: stop attack ─────────────────────────────────────────────────────────

@app.route("/stop", methods=["POST"])
def stop():
    global attack_running
    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 401
    stop_flag.set()
    attack_running = False
    if current_industry == "ctf":
        threading.Thread(
            target=_signal_novamind_incident, args=(False,), daemon=True
        ).start()
    return jsonify({"status": "stopped"})


# ── API: polling endpoint ─────────────────────────────────────────────────────

@app.route("/logs")
def get_logs():
    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 401
    since = request.args.get("since", 0, type=int)
    entries = [e for e in log_buffer if e["id"] > since]
    return jsonify({
        "entries": entries,
        "running": attack_running,
        "phase": current_phase,
        "industry": current_industry,
    })


# ── API: status ───────────────────────────────────────────────────────────────

@app.route("/status")
def status():
    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({
        "running": attack_running,
        "phase": current_phase,
        "industry": current_industry,
    })


# ── API: scenario metadata ────────────────────────────────────────────────────

@app.route("/scenarios")
def scenarios():
    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 401
    result = {}
    for key in ("financial", "healthcare", "saas", "ctf"):
        mod = get_scenario(key)
        result[key] = {
            "name": mod.INDUSTRY_NAME,
            "campaign": mod.CAMPAIGN_NAME,
            "color": mod.INDUSTRY_COLOR,
            "icon": mod.INDUSTRY_ICON,
            "phases": [
                {
                    "number": p["number"],
                    "name": p["name"],
                    "description": p["description"],
                    "what_fires": p["what_fires"],
                    "cloudflare_story": p["cloudflare_story"],
                    "sentinelone_story": p["sentinelone_story"],
                    "hyperautomation": p["hyperautomation"],
                }
                for p in mod.PHASES
            ],
        }
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
