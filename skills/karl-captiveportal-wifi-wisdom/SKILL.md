---
name: karl-captiveportal-wifi-wisdom
description: "(💛) Use when troubleshooting hotel, airport, conference, or public captive portal Wi-Fi connection failures on macOS, including login pages not opening, constant disconnections on sleep/wake, self-assigned IP addresses (169.254.x.x), or SSL certificate redirect errors."
compatibility: Gemini CLI, Antigravity, Claude Code, macOS
metadata:
  version: "0.1.0"
  author: "Karl Weinmeister (provenance: LinkedIn), packaged by Riccardo Carlesso"
  tags: "wifi, macos, captive-portal, networking, troubleshooting, hotel-wifi"
---

# 💛 Karl's Captive Portal Wi-Fi Wisdom (macOS)

> *"I spent 15 minutes trying to get hotel Wi-Fi working on my MacBook last week.*
> *This felt like the 3rd time in a row this has happened to me while on the road.*
> *After way too much trial and error, I want to share what worked for me to save you all time."*
> — **Karl Weinmeister** ([LinkedIn](https://www.linkedin.com/in/kweinmeister/))

A battle-tested troubleshooting guide for surviving hotel, airport, cafe, and conference Wi-Fi captive portals on macOS.

---

## When to Use This Skill

Activate when ANY of the following symptoms occur on macOS while connecting to a public or hospitality Wi-Fi network:

- **Login page never appears**: Connecting to Wi-Fi shows a checkmark or connected icon, but the captive portal splash screen never opens.
- **SSL / Certificate errors on redirect**: Opening a browser (e.g. Chrome, Safari) shows `NET::ERR_CERT_COMMON_NAME_INVALID`, HSTS blocks, or "Your connection is not private".
- **Constant dropouts after sleep**: Wi-Fi works for a few minutes, but as soon as the MacBook sleeps, locks, or changes access points, the session is dropped and you are asked to re-login or blocked completely.
- **Self-assigned IP address**: Network settings show IP `169.254.x.x` (APIPA), indicating failure to obtain a valid DHCP lease from the gateway router.
- **Works on smartphone but not MacBook**: iPhone or Android device connects and authenticates fine, while macOS fails or hangs indefinitely.

---

## The 3 Core Fixes (Karl's Playbook)

Follow these three steps in order. They resolve 95% of captive portal failures on macOS.

```
┌────────────────────────────────────────────────────────┐
│  1. Set Private Wi-Fi Address to "Fixed" (or "Off")   │
│     → Stops MAC rotation breaking gateway session      │
└──────────────────────────┬─────────────────────────────┘
                           │ Still stuck?
                           ▼
┌────────────────────────────────────────────────────────┐
│  2. Navigate to http://neverssl.com in Browser        │
│     → Plain HTTP allows clean router interception      │
└──────────────────────────┬─────────────────────────────┘
                           │ Still stuck?
                           ▼
┌────────────────────────────────────────────────────────┐
│  3. Forget Network, Toggle Wi-Fi, and Rejoin          │
│     → Clears stale DHCP leases & resets login helper   │
└──────────────────────────┬─────────────────────────────┘
                           │ Still stuck?
                           ▼
┌────────────────────────────────────────────────────────┐
│  Fallbacks: Pause VPN & Restore Automatic DNS          │
└────────────────────────────────────────────────────────┘
```

---

### 1. Set Private Wi-Fi to "Fixed" (or "Off")

**The Mechanism:**
Recent macOS updates (macOS Sequoia and Sonoma) default open/public Wi-Fi networks to rotate your MAC address (hardware address) periodically or upon reconnecting. Hotel captive gateways track room login, payment, bandwidth throttling, and device limits by this exact MAC address. When macOS rotates the address or wakes from sleep, the gateway treats the MacBook as an entirely unknown device and drops access.

**The Fix:**
1. Open **System Settings** > **Wi-Fi**.
2. Click **Details…** next to the connected network.
3. Find **Private Wi-Fi Address**.
4. Change from **Rotating** to **Fixed** (or **Off** for older macOS versions).
5. Click **OK**.

> **Why "Fixed"?**
> "Fixed" keeps a consistent private MAC address for that specific network so your login session persists across sleep/wake cycles, without broadcasting your machine's true factory hardware MAC.

---

### 2. Navigate to `neverssl.com` in Your Browser

**The Mechanism:**
When you open a browser, it typically tries to load HTTPS sites (e.g., Google, Apple, default start pages) with strict HSTS (HTTP Strict Transport Security). The hotel router attempts to hijack and redirect the connection to its captive login portal. Because the router cannot forge a valid SSL/TLS certificate for `google.com`, the browser's security layer immediately halts the request with certificate warnings before the redirect can execute.

**The Fix:**
In Safari or Chrome, open an explicit, unencrypted HTTP URL:
```text
http://neverssl.com
```

Because `neverssl.com` uses plain unencrypted HTTP with no TLS certificates and never enforces HSTS, the hotel router easily intercepts the connection and forwards your browser directly to the captive portal login splash page.

**Alternative Unencrypted Triggers:**
- `http://captive.apple.com/hotspot-detect.html` (Apple's native captive probe)
- `http://detectportal.firefox.com/canonical.html` (Mozilla's captive probe)
- `http://1.1.1.1` (plain HTTP to Cloudflare IP)
- `http://httpforever.com`

---

### 3. Forget the Network and Rejoin

**The Mechanism:**
If your Mac gets stuck with a self-assigned IP address (`169.254.x.x`), the DHCP client negotiation timed out or cached a stale lease from a previous session or previous access point. This breaks DNS and routing, leaving the Mac unable to reach the gateway.

**The Fix:**
1. Open **System Settings** > **Wi-Fi**.
2. Click **Details…** next to the network.
3. Click **Forget This Network…** and confirm.
4. Turn **Wi-Fi OFF** for 5–10 seconds.
5. Turn **Wi-Fi ON** and reconnect to the network.

This flushes stale DHCP leases, resets the ARP cache, and triggers macOS's built-in background login assistant (`Captive Network Assistant.app`).

---

## Fallback Checks: If You Are Still Stuck

If the top 3 steps did not solve it, check these two silent blockers:

### A. Pause Your VPN
- **Problem:** Many VPN clients (GlobalProtect, Cisco AnyConnect, WireGuard, Tailscale, Mullvad, ProtonVPN) employ "kill-switches" or attempt to establish tunnels immediately upon interface up.
- **Result:** Encrypted tunnel attempts block local LAN traffic to the hotel gateway's captive portal IP (typically `10.x.x.x`, `172.16.x.x`, or `192.168.x.x`).
- **Fix:** Pause, disconnect, or temporarily disable your VPN until the captive portal login is fully completed and internet access is verified. Once authenticated, re-enable the VPN.

### B. Restore DNS to Automatic (DHCP)
- **Problem:** If you manually configured external DNS servers (e.g. `1.1.1.1`, `8.8.8.8`, `9.9.9.9`, NextDNS) in macOS Network Settings, captive portal firewalls actively drop outbound DNS queries to public servers before you authenticate.
- **Result:** You cannot resolve the hotel portal's local domain name (e.g. `login.hotelwifi.com`), so the browser shows `DNS_PROBE_FINISHED_BAD_CONFIG`.
- **Fix:**
  1. Go to **System Settings** > **Wi-Fi** > **Details…** > **DNS**.
  2. Remove custom DNS entries so it defaults to the router-provided DHCP DNS.
  3. Or run the terminal command below.

---

## macOS Terminal Quick Reference (CLI Superpowers)

Run these diagnostic commands directly from the macOS terminal:

### 1. Fast Diagnostics
```bash
# Check current Wi-Fi SSID
networksetup -getairportnetwork en0

# Check assigned IP and router/gateway IP
ipconfig getifaddr en0
netstat -rn | grep default

# Check DNS servers currently configured for Wi-Fi
networksetup -getdnsservers Wi-Fi
```

### 2. Reset DNS to Automatic (DHCP)
```bash
# Reverts Wi-Fi DNS back to automatic router-assigned DNS
networksetup -setdnsservers Wi-Fi empty
```

### 3. Flush macOS DNS Cache
```bash
sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder
```

### 4. Cycle Wi-Fi Interface
```bash
# Power cycle Wi-Fi to force DHCP renegotiation
networksetup -setairportpower en0 off && sleep 2 && networksetup -setairportpower en0 on
```

### 5. Force-Open Captive Portal Assistant
```bash
# Trigger the built-in macOS Captive Portal WebSheet
open "/System/Library/CoreServices/Captive Network Assistant.app" 2>/dev/null || open http://neverssl.com
```

### 6. Probe HTTP Redirection via Curl
```bash
# Inspect if the gateway returns a 302/307 redirect
curl -v -s -o /dev/null http://neverssl.com
```

---

## Diagnostic Script

This skill includes an automated diagnostic helper script:

```bash
$SKILL_DIR/scripts/diagnose_wifi.sh
```

It inspects the active network interface, validates IP lease ranges (detecting `169.254.x.x`), inspects DNS overrides, and probes unencrypted HTTP captive portal redirection.

---

## Summary Checklist

| Priority | Action | Why |
|---|---|---|
| **#1** | Set Private Wi-Fi to **Fixed** | Prevents MAC rotation from dropping gateway session |
| **#2** | Open **`http://neverssl.com`** | Unencrypted HTTP allows clean 302 captive portal redirection without HTTPS cert blocks |
| **#3** | **Forget Network & Rejoin** | Resets stale DHCP leases & recovers from self-assigned `169.254.x.x` |
| **#4** | **Pause VPN** | Prevents VPN kill-switch from blocking local LAN portal traffic |
| **#5** | **Reset DNS to Automatic** | Allows gateway to resolve local portal hostname before login |

---

## Provenance

- **Originator:** Karl Weinmeister ([LinkedIn Post](https://www.linkedin.com/in/kweinmeister/))
- **Packaging & macOS CLI tooling:** Riccardo Carlesso (`gemini-cli-palladius-public-goodies`)
