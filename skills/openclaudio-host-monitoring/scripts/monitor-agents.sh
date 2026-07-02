#!/bin/bash
LOG_FILE="$HOME/.hermes/logs/agent_metrics.csv"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
if [ ! -f "$LOG_FILE" ]; then echo "timestamp,ermete_cpu,ermete_mem,lobby_cpu,lobby_mem,tailscale_cpu,tailscale_mem,other_cpu,other_mem,total_cpu,total_mem" > "$LOG_FILE"; fi
get_metrics() {
ps -A -o %cpu,%mem,command | grep "$1" | grep -v grep | awk '{cpu+=$1; mem+=$2} END {print (cpu?cpu:0) "," (mem?mem:0)}'
}
E=$(get_metrics "hermes_cli.main gateway")
L=$(get_metrics "openclaw/dist/index.js")
TS=$(get_metrics "Tailscale")
T=$(ps -A -o %cpu,%mem | awk '{cpu+=$1; mem+=$2} END {print cpu "," mem}')
ec=$(echo $E | cut -d, -f1); em=$(echo $E | cut -d, -f2)
lc=$(echo $L | cut -d, -f1); lm=$(echo $L | cut -d, -f2)
tsc=$(echo $TS | cut -d, -f1); tsm=$(echo $TS | cut -d, -f2)
tc=$(echo $T | cut -d, -f1); tm=$(echo $T | cut -d, -f2)
oc=$(awk "BEGIN {print $tc - $ec - $lc - $tsc}"); om=$(awk "BEGIN {print $tm - $em - $lm - $tsm}")
echo "$TIMESTAMP,$ec,$em,$lc,$lm,$tsc,$tsm,$oc,$om,$tc,$tm" >> "$LOG_FILE"
