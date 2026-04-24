#!/usr/bin/env bash
# Diagnostic script for zerosrp Hetzner GMod RP server lockout.
# Read-only: this script does NOT modify anything.
# Run on the server console as root: bash diagnose-zerosrp.sh

set +e
export LC_ALL=C

line() { printf '=%.0s' {1..60}; echo; }
hdr()  { echo; line; echo "== $1"; line; }

hdr "HOST IDENTITY"
hostname
date -u
uptime
echo "public IPv4:"
curl -sS -m 5 ifconfig.me || echo "(curl failed)"
echo

hdr "OUTBOUND CONNECTIVITY (TCP 443, bypassing DNS)"
# Cloudflare 1.1.1.1, Google 8.8.8.8, GitHub 140.82.121.4
for ip in 1.1.1.1 8.8.8.8 140.82.121.4; do
    if timeout 5 bash -c ">/dev/tcp/${ip}/443" 2>/dev/null; then
        echo "TCP 443 -> ${ip}: OK"
    else
        echo "TCP 443 -> ${ip}: FAIL"
    fi
done
echo
echo "TCP 80 -> 1.1.1.1:"
timeout 5 bash -c ">/dev/tcp/1.1.1.1/80" 2>/dev/null && echo "OK" || echo "FAIL"
echo "TCP 53 -> 1.1.1.1:"
timeout 5 bash -c ">/dev/tcp/1.1.1.1/53" 2>/dev/null && echo "OK" || echo "FAIL"

hdr "DNS"
cat /etc/resolv.conf
echo
echo "Lookup claude.ai:"
getent hosts claude.ai || echo "FAIL"
echo "Lookup github.com:"
getent hosts github.com || echo "FAIL"

hdr "SSHD STATUS (why is port 22 refused?)"
systemctl is-active ssh 2>/dev/null
systemctl is-active sshd 2>/dev/null
ss -tlnp 2>/dev/null | grep -E ":(22|2022|2222)\b" || echo "(no ssh-like ports listening)"
echo
echo "-- sshd_config effective values --"
sshd -T 2>/dev/null | grep -iE "^(port|listenaddress|permitrootlogin|passwordauthentication|pubkeyauthentication|allowusers|allowgroups|denyusers|denygroups|maxauthtries)" | sort

hdr "PORT 2022 OWNER (the Go SSH banner)"
ss -tlnp '( sport = :2022 )' 2>/dev/null
echo
echo "-- Wings / Pterodactyl service status --"
systemctl status wings --no-pager 2>/dev/null | head -15 || echo "(no wings service)"

hdr "FAIL2BAN"
command -v fail2ban-client >/dev/null && {
    fail2ban-client status 2>/dev/null
    echo
    for jail in sshd sshd-ddos recidive pterodactyl wings; do
        if fail2ban-client status "$jail" >/dev/null 2>&1; then
            echo "-- jail: $jail --"
            fail2ban-client status "$jail" 2>/dev/null
            echo
        fi
    done
} || echo "(fail2ban not installed)"

hdr "HOMELAB PUBLIC IP IN BAN LISTS?"
TARGET=90.200.217.232
echo "Searching for ${TARGET} in firewall / ban sources..."
iptables-save 2>/dev/null | grep -- "${TARGET}" || echo "  iptables: not found"
ip6tables-save 2>/dev/null | grep -- "${TARGET}" || echo "  ip6tables: not found"
[ -f /etc/fail2ban/ip.blocklist ] && grep -- "${TARGET}" /etc/fail2ban/ip.blocklist
grep -rl -- "${TARGET}" /etc/fail2ban/ 2>/dev/null | head -5 || echo "  fail2ban configs: not found"

hdr "IPTABLES RAW RULES (all chains)"
iptables -S 2>/dev/null | head -100
echo
echo "-- nftables (if used) --"
nft list ruleset 2>/dev/null | head -60

hdr "RECENT SSH AUTH ATTEMPTS (last 30 lines)"
journalctl -u ssh -u sshd --since "24 hours ago" --no-pager 2>/dev/null | tail -30
echo
echo "-- auth.log (last 20 lines) --"
tail -20 /var/log/auth.log 2>/dev/null

hdr "RECENT WINGS LOGS (if present)"
journalctl -u wings --since "6 hours ago" --no-pager 2>/dev/null | tail -30

hdr "SUMMARY HINTS"
echo "- If OUTBOUND 443 -> 1.1.1.1 failed: host-level egress filter; check iptables OUTPUT."
echo "- If SSH config shows Port 2022 (not 22): the port moved; update agent connection config."
echo "- If sshd is not listening on 22: same conclusion, port moved or service stopped."
echo "- If 90.200.217.232 appears in a fail2ban jail: unban with 'fail2ban-client set <jail> unbanip 90.200.217.232'."
echo "- If nothing points at 90.200.217.232 and port 22 refuses: sshd legitimately isn't on 22."
echo
echo "DONE."
