#!/usr/bin/env bash
# diagnose_wifi.sh - Captive Portal & Wi-Fi Triage Diagnostic for macOS
# Based on Karl Weinmeister's Captive Portal Wisdom

set -euo pipefail

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
BLUE="\033[0;34m"
RESET="\033[0m"

echo -e "${BOLD}${BLUE}=== 🏨 Captive Portal & Wi-Fi Diagnostic for macOS ===${RESET}\n"

# 1. Detect Wi-Fi interface (usually en0)
WIFI_DEV=$(networksetup -listallhardwareports 2>/dev/null | awk '/Wi-Fi|AirPort/{getline; print $2}' || echo "en0")
if [ -z "$WIFI_DEV" ]; then
  WIFI_DEV="en0"
fi
echo -e "📡 Wi-Fi Interface: ${BOLD}${WIFI_DEV}${RESET}"

# 2. Check Wi-Fi Power and SSID
SSID=$(networksetup -getairportnetwork "$WIFI_DEV" 2>/dev/null | sed -e 's/^Current Wi-Fi Network: //' || echo "Not connected")
echo -e "📶 Network SSID:    ${BOLD}${SSID}${RESET}"

if [[ "$SSID" == *"You are not associated"* ]] || [[ "$SSID" == "Not connected" ]]; then
  echo -e "${RED}❌ You are not connected to any Wi-Fi network.${RESET}"
  exit 1
fi

# 3. Check IP Address
IP=$(ipconfig getifaddr "$WIFI_DEV" 2>/dev/null || echo "")
if [ -z "$IP" ]; then
  echo -e "${RED}⚠️  No IP address assigned! DHCP lease negotiation failed.${RESET}"
  echo -e "   👉 ${YELLOW}Action: Details > Forget This Network, toggle Wi-Fi off/on, and reconnect.${RESET}\n"
elif [[ "$IP" =~ ^169\.254\. ]]; then
  echo -e "${RED}⚠️  Self-Assigned IP detected: ${IP} (APIPA)!${RESET}"
  echo -e "   The Mac could not obtain a valid DHCP lease from the hotel gateway."
  echo -e "   👉 ${YELLOW}Action: Details > Forget This Network, toggle Wi-Fi off/on, and reconnect.${RESET}\n"
else
  echo -e "🌐 Assigned IP:     ${GREEN}${IP}${RESET}"
fi

# 4. Check Router Gateway
GATEWAY=$(netstat -rn -f inet 2>/dev/null | awk '/default/{print $2}' | head -n1 || echo "")
if [ -n "$GATEWAY" ]; then
  echo -e "🚪 Default Gateway: ${GREEN}${GATEWAY}${RESET}"
else
  echo -e "${RED}⚠️  No default gateway found in routing table!${RESET}"
fi

# 5. Check Custom DNS
DNS_SERVERS=$(networksetup -getdnsservers Wi-Fi 2>/dev/null || echo "")
if [[ "$DNS_SERVERS" == *"There aren't any DNS Servers set"* ]]; then
  echo -e "📖 DNS Servers:     ${GREEN}Automatic (DHCP)${RESET}"
else
  echo -e "${YELLOW}⚠️  Manual DNS configured: ${DNS_SERVERS}${RESET}"
  echo -e "   Hotel captive portals often BLOCK custom external DNS (like 8.8.8.8, 1.1.1.1) before authentication."
  echo -e "   👉 ${YELLOW}Fix: Run 'networksetup -setdnsservers Wi-Fi empty' to switch back to DHCP.${RESET}"
fi

echo ""

# 6. Probe Captive Portal via Plain HTTP
echo -e "${BOLD}🔍 Probing Captive Portal redirect via plain HTTP (neverssl.com)...${RESET}"
HTTP_PROBE=$(curl -s -I -m 4 http://neverssl.com 2>/dev/null || echo "")

if [ -z "$HTTP_PROBE" ]; then
  echo -e "${RED}❌ HTTP probe timed out or connection failed.${RESET}"
  echo -e "   👉 ${YELLOW}Possible culprits:${RESET}"
  echo -e "      1. Active VPN kill-switch blocking local portal traffic (Pause VPN!)"
  echo -e "      2. Stale DHCP lease or gateway firewall block"
else
  STATUS_CODE=$(echo "$HTTP_PROBE" | awk '/^HTTP/{print $2}' | head -n1 || echo "unknown")
  LOCATION=$(echo "$HTTP_PROBE" | awk -F': ' '/^[Ll]ocation:/{print $2}' | tr -d '\r' | head -n1 || echo "")
  
  if [[ "$STATUS_CODE" =~ ^30[127] ]] && [ -n "$LOCATION" ]; then
    echo -e "${GREEN}🎯 Captive Portal detected!${RESET} Router redirected to:"
    echo -e "   ${BOLD}${LOCATION}${RESET}"
    echo -e "\n👉 Run: ${BOLD}open \"${LOCATION}\"${RESET} or ${BOLD}open http://neverssl.com${RESET} to finish login."
  else
    # Check Apple hotspot detect
    APPLE_PROBE=$(curl -s -m 3 http://captive.apple.com/hotspot-detect.html 2>/dev/null || echo "")
    if [[ "$APPLE_PROBE" == *"<HTML><HEAD><TITLE>Success</TITLE></HEAD>"* ]]; then
      echo -e "${GREEN}✅ Internet connection is active! Captive portal is already satisfied.${RESET}"
    else
      echo -e "${YELLOW}ℹ️  HTTP Status: ${STATUS_CODE}.${RESET}"
      echo -e "👉 Try opening ${BOLD}http://neverssl.com${RESET} in your browser to trigger portal login."
    fi
  fi
fi

echo -e "\n${BOLD}${BLUE}=== End of Diagnostic ===${RESET}"
