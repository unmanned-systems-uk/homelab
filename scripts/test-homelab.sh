#!/bin/bash

###############################################################################
# HomeLab Comprehensive Test Script
#
# Purpose: Automated testing of all HomeLab infrastructure components
# Author: HomeLab Agent
# Version: 1.0.0
# Date: 2025-12-30
#
# Tests:
#   - Network infrastructure (UDM Pro, NAS, Proxmox)
#   - Proxmox VMs (Whisper, Harbor)
#   - SCPI equipment connectivity
#   - Docker services (Harbor VM)
#   - Ollama API and models
#   - UniFi network health
#   - Workflow scripts
#
# Usage: ./scripts/test-homelab.sh [--verbose] [--json]
###############################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script options
VERBOSE=false
JSON_OUTPUT=false
OUTPUT_FILE=""

# Test results storage
declare -A TEST_RESULTS
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --json|-j)
            JSON_OUTPUT=true
            shift
            ;;
        --output|-o)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [--verbose] [--json] [--output FILE]"
            echo ""
            echo "Options:"
            echo "  --verbose, -v    Show detailed test output"
            echo "  --json, -j       Output results in JSON format"
            echo "  --output, -o     Write results to file"
            echo "  --help, -h       Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

###############################################################################
# Utility Functions
###############################################################################

log_info() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo -e "${BLUE}[INFO]${NC} $1"
    fi
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_skip() {
    echo -e "${YELLOW}[SKIP]${NC} $1"
}

# Record test result
record_test() {
    local test_name="$1"
    local status="$2"  # PASS, FAIL, SKIP
    local details="${3:-}"

    TEST_RESULTS["$test_name"]="$status|$details"
    ((TOTAL_TESTS++))

    case "$status" in
        PASS)
            ((PASSED_TESTS++))
            ;;
        FAIL)
            ((FAILED_TESTS++))
            ;;
        SKIP)
            ((SKIPPED_TESTS++))
            ;;
    esac
}

# Check if a host is reachable via ping
check_host() {
    local host="$1"
    local name="$2"

    if ping -c 1 -W 1 "$host" &>/dev/null; then
        return 0
    else
        return 1
    fi
}

# Check if a TCP port is open
check_tcp_port() {
    local host="$1"
    local port="$2"

    if timeout 2 bash -c "echo > /dev/tcp/$host/$port" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# Check HTTP endpoint
check_http() {
    local url="$1"
    local expected_code="${2:-200}"

    local response_code
    response_code=$(timeout 3 curl -k -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")

    if [[ "$response_code" == "$expected_code" ]] || [[ "$response_code" =~ ^(200|301|302)$ ]]; then
        return 0
    else
        return 1
    fi
}

###############################################################################
# Test Sections
###############################################################################

test_network_infrastructure() {
    echo ""
    echo "========================================"
    echo "  Testing Network Infrastructure"
    echo "========================================"

    # UDM Pro
    log_info "Testing UDM Pro (10.0.1.1)..."
    if check_host "10.0.1.1" "UDM Pro"; then
        log_success "UDM Pro: UP"
        record_test "network_udm_pro" "PASS" "10.0.1.1 is reachable"
    else
        log_fail "UDM Pro: DOWN"
        record_test "network_udm_pro" "FAIL" "10.0.1.1 is not reachable"
    fi

    # NAS
    log_info "Testing NAS (10.0.1.251)..."
    if check_host "10.0.1.251" "NAS"; then
        log_success "NAS: UP"
        record_test "network_nas" "PASS" "10.0.1.251 is reachable"
    else
        log_fail "NAS: DOWN"
        record_test "network_nas" "FAIL" "10.0.1.251 is not reachable"
    fi

    # Proxmox Host
    log_info "Testing Proxmox Host (10.0.1.200)..."
    if check_host "10.0.1.200" "Proxmox"; then
        log_success "Proxmox Host: UP"
        record_test "network_proxmox" "PASS" "10.0.1.200 is reachable"

        # Check Proxmox Web UI
        if check_http "https://10.0.1.200:8006"; then
            log_success "Proxmox Web UI: UP"
            record_test "proxmox_webui" "PASS" "Web UI is accessible"
        else
            log_fail "Proxmox Web UI: DOWN"
            record_test "proxmox_webui" "FAIL" "Web UI is not accessible"
        fi
    else
        log_fail "Proxmox Host: DOWN"
        record_test "network_proxmox" "FAIL" "10.0.1.200 is not reachable"
        log_skip "Proxmox Web UI: Host unreachable"
        record_test "proxmox_webui" "SKIP" "Host unreachable"
    fi
}

test_proxmox_vms() {
    echo ""
    echo "========================================"
    echo "  Testing Proxmox VMs"
    echo "========================================"

    # Whisper VM
    log_info "Testing Whisper VM (10.0.1.201)..."
    if check_host "10.0.1.201" "Whisper VM"; then
        log_success "Whisper VM: UP"
        record_test "vm_whisper" "PASS" "10.0.1.201 is reachable"
    else
        log_fail "Whisper VM: DOWN (may need to be started)"
        record_test "vm_whisper" "FAIL" "10.0.1.201 is not reachable"
    fi

    # Harbor VM
    log_info "Testing Harbor VM (10.0.1.202)..."
    if check_host "10.0.1.202" "Harbor VM"; then
        log_success "Harbor VM: UP"
        record_test "vm_harbor" "PASS" "10.0.1.202 is reachable"
    else
        log_fail "Harbor VM: DOWN"
        record_test "vm_harbor" "FAIL" "10.0.1.202 is not reachable"
    fi
}

test_scpi_equipment() {
    echo ""
    echo "========================================"
    echo "  Testing SCPI Equipment"
    echo "========================================"

    declare -A SCPI_DEVICES=(
        ["10.0.1.101:5025"]="DMM (Keithley DMM6500)"
        ["10.0.1.105:5555"]="DC Load (Rigol DL3021A)"
        ["10.0.1.106:5555"]="Scope (Rigol MSO8204)"
        ["10.0.1.111:5025"]="PSU-1 (Rigol DP932A)"
        ["10.0.1.120:5555"]="AWG (Rigol DG2052)"
        ["10.0.1.138:5025"]="PSU-2 (Rigol DP932A)"
    )

    local scpi_online=0
    local scpi_total=0

    for addr in "${!SCPI_DEVICES[@]}"; do
        IFS=':' read -r ip port <<< "$addr"
        local name="${SCPI_DEVICES[$addr]}"
        ((scpi_total++))

        log_info "Testing $name ($ip:$port)..."
        if check_tcp_port "$ip" "$port"; then
            log_success "$name: UP"
            record_test "scpi_${ip//./_}" "PASS" "$name is reachable"
            ((scpi_online++))
        else
            log_warn "$name: DOWN (expected when not in use)"
            record_test "scpi_${ip//./_}" "SKIP" "$name is offline (expected)"
            ((SKIPPED_TESTS++))
            ((TOTAL_TESTS--))  # Don't count as real test
        fi
    done

    log_info "SCPI Equipment: $scpi_online/$scpi_total online"
}

test_harbor_services() {
    echo ""
    echo "========================================"
    echo "  Testing Harbor VM Services"
    echo "========================================"

    if ! check_host "10.0.1.202" "Harbor VM"; then
        log_skip "Harbor VM services: Host unreachable"
        record_test "harbor_services" "SKIP" "Harbor VM is down"
        return
    fi

    # Open WebUI HTTP
    log_info "Testing Open WebUI HTTP (10.0.1.202:3000)..."
    if check_http "http://10.0.1.202:3000"; then
        log_success "Open WebUI (HTTP): UP"
        record_test "harbor_openwebui_http" "PASS" "HTTP endpoint accessible"
    else
        log_fail "Open WebUI (HTTP): DOWN"
        record_test "harbor_openwebui_http" "FAIL" "HTTP endpoint not accessible"
    fi

    # Open WebUI HTTPS
    log_info "Testing Open WebUI HTTPS (10.0.1.202:3443)..."
    if check_http "https://10.0.1.202:3443"; then
        log_success "Open WebUI (HTTPS): UP"
        record_test "harbor_openwebui_https" "PASS" "HTTPS endpoint accessible"
    else
        log_fail "Open WebUI (HTTPS): DOWN"
        record_test "harbor_openwebui_https" "FAIL" "HTTPS endpoint not accessible"
    fi

    # HomeLab MCP Server
    log_info "Testing HomeLab MCP Server (10.0.1.202:8080)..."
    local mcp_test
    mcp_test=$(timeout 3 curl -s -N --max-time 2 http://10.0.1.202:8080/sse 2>/dev/null | head -1 || echo "")
    if echo "$mcp_test" | grep -q "event:"; then
        log_success "HomeLab MCP Server: UP (SSE responding)"
        record_test "harbor_mcp" "PASS" "MCP SSE endpoint responding"
    else
        log_fail "HomeLab MCP Server: DOWN"
        record_test "harbor_mcp" "FAIL" "MCP SSE endpoint not responding"
    fi

    # Portainer
    log_info "Testing Portainer (10.0.1.202:9443)..."
    if check_http "https://10.0.1.202:9443"; then
        log_success "Portainer: UP"
        record_test "harbor_portainer" "PASS" "Portainer accessible"
    else
        log_fail "Portainer: DOWN"
        record_test "harbor_portainer" "FAIL" "Portainer not accessible"
    fi
}

test_ollama() {
    echo ""
    echo "========================================"
    echo "  Testing Ollama (Whisper VM)"
    echo "========================================"

    if ! check_host "10.0.1.201" "Whisper VM"; then
        log_skip "Ollama: Whisper VM unreachable"
        record_test "ollama_api" "SKIP" "Whisper VM is down"
        record_test "ollama_models" "SKIP" "Whisper VM is down"
        return
    fi

    # Ollama API
    log_info "Testing Ollama API (10.0.1.201:11434)..."
    local version
    version=$(timeout 5 curl -s http://10.0.1.201:11434/api/version 2>/dev/null | jq -r '.version // empty' 2>/dev/null || echo "")

    if [[ -n "$version" ]]; then
        log_success "Ollama API: UP (version $version)"
        record_test "ollama_api" "PASS" "API responding, version $version"

        # List models
        log_info "Checking Ollama models..."
        local models
        models=$(timeout 5 curl -s http://10.0.1.201:11434/api/tags 2>/dev/null | jq -r '.models[]?.name // empty' 2>/dev/null | wc -l)

        if [[ "$models" -gt 0 ]]; then
            log_success "Ollama Models: $models models available"
            record_test "ollama_models" "PASS" "$models models found"

            if [[ "$VERBOSE" == "true" ]]; then
                timeout 5 curl -s http://10.0.1.201:11434/api/tags 2>/dev/null | jq -r '.models[]? | "  - \(.name)"' 2>/dev/null
            fi
        else
            log_warn "Ollama Models: No models found"
            record_test "ollama_models" "FAIL" "No models found"
        fi
    else
        log_fail "Ollama API: DOWN"
        record_test "ollama_api" "FAIL" "API not responding"
        log_skip "Ollama Models: API unreachable"
        record_test "ollama_models" "SKIP" "API unreachable"
    fi
}

test_unifi_network() {
    echo ""
    echo "========================================"
    echo "  Testing UniFi Network (via MCP)"
    echo "========================================"

    # Check if MCP tools are available (this requires claude CLI with MCP configured)
    if ! command -v claude &>/dev/null; then
        log_skip "UniFi Network: Claude CLI not available for MCP testing"
        record_test "unifi_health" "SKIP" "Claude CLI not available"
        return
    fi

    log_info "UniFi network health check requires MCP integration"
    log_info "Use 'claude chat' with UniFi MCP tools for detailed network testing"
    record_test "unifi_health" "SKIP" "Manual MCP testing required"
}

test_workflow_scripts() {
    echo ""
    echo "========================================"
    echo "  Testing Workflow Scripts"
    echo "========================================"

    # Check if scripts exist
    if [[ -f "scripts/refine-prompt.sh" ]]; then
        if [[ -x "scripts/refine-prompt.sh" ]]; then
            log_success "refine-prompt.sh: EXISTS and executable"
            record_test "script_refine_prompt" "PASS" "Script exists and is executable"
        else
            log_warn "refine-prompt.sh: EXISTS but not executable"
            record_test "script_refine_prompt" "FAIL" "Script not executable"
        fi
    else
        log_fail "refine-prompt.sh: NOT FOUND"
        record_test "script_refine_prompt" "FAIL" "Script not found"
    fi

    if [[ -f "scripts/claude-workflow.sh" ]]; then
        if [[ -x "scripts/claude-workflow.sh" ]]; then
            log_success "claude-workflow.sh: EXISTS and executable"
            record_test "script_claude_workflow" "PASS" "Script exists and is executable"
        else
            log_warn "claude-workflow.sh: EXISTS but not executable"
            record_test "script_claude_workflow" "FAIL" "Script not executable"
        fi
    else
        log_fail "claude-workflow.sh: NOT FOUND"
        record_test "script_claude_workflow" "FAIL" "Script not found"
    fi
}

###############################################################################
# Report Generation
###############################################################################

generate_summary() {
    echo ""
    echo "========================================"
    echo "  Test Summary"
    echo "========================================"
    echo ""
    echo "Total Tests:   $TOTAL_TESTS"
    echo "Passed:        $PASSED_TESTS ($(( TOTAL_TESTS > 0 ? PASSED_TESTS * 100 / TOTAL_TESTS : 0 ))%)"
    echo "Failed:        $FAILED_TESTS ($(( TOTAL_TESTS > 0 ? FAILED_TESTS * 100 / TOTAL_TESTS : 0 ))%)"
    echo "Skipped:       $SKIPPED_TESTS"
    echo ""

    if [[ $FAILED_TESTS -gt 0 ]]; then
        echo "Failed Tests:"
        for test_name in "${!TEST_RESULTS[@]}"; do
            IFS='|' read -r status details <<< "${TEST_RESULTS[$test_name]}"
            if [[ "$status" == "FAIL" ]]; then
                echo "  - $test_name: $details"
            fi
        done
        echo ""
    fi

    local exit_code=0
    if [[ $FAILED_TESTS -gt 0 ]]; then
        echo -e "${RED}Status: FAILURES DETECTED${NC}"
        exit_code=1
    else
        echo -e "${GREEN}Status: ALL TESTS PASSED${NC}"
    fi
    echo ""

    return $exit_code
}

generate_json() {
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    echo "{"
    echo "  \"timestamp\": \"$timestamp\","
    echo "  \"summary\": {"
    echo "    \"total\": $TOTAL_TESTS,"
    echo "    \"passed\": $PASSED_TESTS,"
    echo "    \"failed\": $FAILED_TESTS,"
    echo "    \"skipped\": $SKIPPED_TESTS"
    echo "  },"
    echo "  \"tests\": {"

    local first=true
    for test_name in "${!TEST_RESULTS[@]}"; do
        IFS='|' read -r status details <<< "${TEST_RESULTS[$test_name]}"

        if [[ "$first" == "false" ]]; then
            echo ","
        fi
        first=false

        echo -n "    \"$test_name\": {\"status\": \"$status\", \"details\": \"$details\"}"
    done

    echo ""
    echo "  }"
    echo "}"
}

###############################################################################
# Main Execution
###############################################################################

main() {
    echo "========================================"
    echo "  HomeLab Comprehensive Test Suite"
    echo "  $(date)"
    echo "========================================"

    # Run all test sections
    test_network_infrastructure
    test_proxmox_vms
    test_scpi_equipment
    test_harbor_services
    test_ollama
    test_unifi_network
    test_workflow_scripts

    # Generate reports
    if [[ "$JSON_OUTPUT" == "true" ]]; then
        if [[ -n "$OUTPUT_FILE" ]]; then
            generate_json > "$OUTPUT_FILE"
            log_info "JSON report written to $OUTPUT_FILE"
        else
            generate_json
        fi
    fi

    generate_summary
    return $?
}

# Run main and capture exit code
main
exit $?
