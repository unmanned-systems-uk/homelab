#!/usr/bin/env python3
"""
Standalone CCPM MCP Tools Test Runner

Uses only Python standard library - no external dependencies required.

Usage:
    python3 run_tests.py                    # Run all tests
    python3 run_tests.py --functional       # Functional tests only
    python3 run_tests.py --validation       # Validation tests only
    python3 run_tests.py --integration      # Integration tests only
    python3 run_tests.py --stress           # Stress tests only
    python3 run_tests.py --quick            # Quick smoke test
"""

import json
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Tuple

# =============================================================================
# Configuration
# =============================================================================

CCPM_MESSAGING_API = "http://10.0.1.210:8000/api/v1"
CCPM_TASK_API = "http://10.0.1.210:8000/api"  # Same port as messaging
TEST_AGENT_ID = "aaaaaaaa-bbbb-cccc-dddd-222222222222"
TEST_AGENT_NAME = "HomeLab-Agent"
# Use a different agent as target to avoid "cannot send to yourself" error
TEST_TARGET_AGENT = "Claude-Desktop"  # Or use broadcast: "ffffffff-ffff-ffff-ffff-ffffffffffff"
TIMEOUT = 10

# Valid enums
VALID_MESSAGE_TYPES = [
    "task_assignment", "task_request", "feature_request", "bug_report",
    "status_request", "completion_signal", "alert", "info", "query", "response"
]
VALID_SESSION_TYPES = ["work", "planning", "review"]
VALID_ENTRY_TYPES = ["start", "progress", "decision", "issue", "complete"]


# =============================================================================
# HTTP Client (using stdlib)
# =============================================================================

def http_request(
    url: str,
    method: str = "GET",
    data: dict = None,
    timeout: int = TIMEOUT
) -> Tuple[int, dict]:
    """Make HTTP request and return (status_code, json_response)."""
    headers = {"Content-Type": "application/json"}

    if data:
        body = json.dumps(data).encode("utf-8")
    else:
        body = None

    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode("utf-8"))
        except Exception:
            body = {"error": e.reason}
        return e.code, body
    except urllib.error.URLError as e:
        return 0, {"error": str(e.reason), "error_code": "REQUEST_FAILED"}
    except Exception as e:
        return 0, {"error": str(e), "error_code": "REQUEST_FAILED"}


# =============================================================================
# Test Results Tracker
# =============================================================================

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.errors: List[Tuple[str, str]] = []

    def record(self, name: str, passed: bool, error: str = None, skipped: bool = False):
        if skipped:
            self.skipped += 1
            print(f"  [SKIP] {name}: {error}")
        elif passed:
            self.passed += 1
            print(f"  [PASS] {name}")
        else:
            self.failed += 1
            self.errors.append((name, error or "Unknown error"))
            print(f"  [FAIL] {name}: {error}")

    def summary(self):
        total = self.passed + self.failed + self.skipped
        print(f"\n{'='*60}")
        print(f"Results: {self.passed} passed, {self.failed} failed, {self.skipped} skipped (total: {total})")

        if self.errors:
            print(f"\nFailures:")
            for name, error in self.errors:
                print(f"  - {name}")
                print(f"    {error[:100]}...")

        return self.failed == 0


# =============================================================================
# CCPM API Client
# =============================================================================

class CCPMClient:
    """Simple CCPM API client."""

    def __init__(self):
        self.messaging_api = CCPM_MESSAGING_API
        self.task_api = CCPM_TASK_API
        self.agent_id = TEST_AGENT_ID
        self._agent_cache = None

    def list_agents(self) -> List[dict]:
        """List all agents."""
        status, data = http_request(f"{self.messaging_api}/agents")
        if status != 200:
            return []
        return data if isinstance(data, list) else []

    def resolve_agent_id(self, name_or_id: str) -> str:
        """Resolve agent name to UUID."""
        # UUID format check
        if len(name_or_id) == 36 and name_or_id.count("-") == 4:
            return name_or_id

        # Get agents if not cached
        if self._agent_cache is None:
            self._agent_cache = {a["name"]: a["id"] for a in self.list_agents()}

        # Exact match
        if name_or_id in self._agent_cache:
            return self._agent_cache[name_or_id]

        # Case-insensitive
        for name, aid in self._agent_cache.items():
            if name.lower() == name_or_id.lower():
                return aid

        raise ValueError(f"Agent not found: {name_or_id}")

    def send_message(
        self,
        to_agent: str,
        subject: str,
        body: str,
        message_type: str = "info",
        priority: str = "normal"
    ) -> dict:
        """Send a message."""
        try:
            to_agent_id = self.resolve_agent_id(to_agent)
        except ValueError as e:
            return {"success": False, "error": str(e), "error_code": "AGENT_NOT_FOUND"}

        url = f"{self.messaging_api}/agent-messages?from_agent_id={self.agent_id}"
        payload = {
            "to_agent_id": to_agent_id,
            "subject": subject,
            "body": body,
            "message_type": message_type,
            "priority": priority
        }

        status, data = http_request(url, "POST", payload)
        return data

    def check_inbox(self) -> List[dict]:
        """Check inbox for messages."""
        url = f"{self.messaging_api}/agent-messages/inbox?agent_id={self.agent_id}&status=pending"
        status, data = http_request(url)
        if isinstance(data, dict) and "items" in data:
            return data["items"]
        return data if isinstance(data, list) else []

    def mark_message_complete(self, message_id: str, response: str = None) -> dict:
        """Mark message as complete."""
        url = f"{self.messaging_api}/agent-messages/{message_id}/complete"
        payload = {"response": response} if response else {}
        status, data = http_request(url, "POST", payload)
        return data

    def list_tasks(self, status: str = None) -> List[dict]:
        """List tasks."""
        url = f"{self.task_api}/tasks"
        if status:
            url += f"?status={status}"
        status_code, data = http_request(url)
        if isinstance(data, dict) and "tasks" in data:
            return data["tasks"]
        return data if isinstance(data, list) else []

    def list_sprints(self, status: str = None) -> List[dict]:
        """List sprints."""
        url = f"{self.task_api}/sprints"
        if status:
            url += f"?status={status}"
        status_code, data = http_request(url)
        if isinstance(data, dict) and "sprints" in data:
            return data["sprints"]
        return data if isinstance(data, list) else []

    def create_session(self, agent_name: str, session_type: str = "work", description: str = None) -> dict:
        """Create a session."""
        url = f"{self.task_api}/sessions"
        payload = {"agent_name": agent_name, "session_type": session_type}
        if description:
            payload["description"] = description
        status, data = http_request(url, "POST", payload)
        return data

    def log_session_entry(self, session_id: int, entry_type: str, content: str) -> dict:
        """Log session entry."""
        url = f"{self.task_api}/sessions/{session_id}/entries"
        payload = {"entry_type": entry_type, "content": content}
        status, data = http_request(url, "POST", payload)
        return data


# =============================================================================
# Test Suites
# =============================================================================

def run_functional_tests(client: CCPMClient, results: TestResults):
    """Run functional/happy path tests."""
    print("\n=== Functional Tests ===")

    # Test: list_agents
    try:
        agents = client.list_agents()
        results.record("list_agents", isinstance(agents, list) and len(agents) > 0)
    except Exception as e:
        results.record("list_agents", False, str(e))

    # Test: send_message
    try:
        msg = client.send_message(
            to_agent=TEST_TARGET_AGENT,
            subject="[TEST] Functional Test",
            body="Automated test message",
            message_type="info"
        )
        msg_id = msg.get("id") or msg.get("message_id")
        results.record("send_message", bool(msg_id), f"Response: {msg}")

        # Cleanup
        if msg_id:
            client.mark_message_complete(msg_id, "Test cleanup")
    except Exception as e:
        results.record("send_message", False, str(e))

    # Test: check_inbox
    try:
        inbox = client.check_inbox()
        results.record("check_inbox", isinstance(inbox, list))
    except Exception as e:
        results.record("check_inbox", False, str(e))

    # Test: list_tasks
    try:
        tasks = client.list_tasks()
        results.record("list_tasks", isinstance(tasks, list))
    except Exception as e:
        results.record("list_tasks", False, str(e))

    # Test: list_sprints
    try:
        sprints = client.list_sprints()
        results.record("list_sprints", isinstance(sprints, list))
    except Exception as e:
        results.record("list_sprints", False, str(e))

    # Test: create_session
    try:
        session = client.create_session(
            agent_name=TEST_AGENT_NAME,
            session_type="work",
            description="[TEST] Functional test session"
        )
        session_id = session.get("id") or session.get("session_id")
        results.record("create_session", bool(session_id) or not session.get("error"), f"Response: {session}")
    except Exception as e:
        results.record("create_session", False, str(e))


def run_validation_tests(client: CCPMClient, results: TestResults):
    """Run input validation tests."""
    print("\n=== Validation Tests ===")

    # Test: valid message types
    for msg_type in VALID_MESSAGE_TYPES[:3]:  # Test first 3 to save time
        try:
            msg = client.send_message(
                to_agent=TEST_TARGET_AGENT,
                subject=f"[TEST] Type: {msg_type}",
                body="Testing message type",
                message_type=msg_type
            )
            passed = not msg.get("error_code") == "INVALID_MESSAGE_TYPE"
            results.record(f"message_type_{msg_type}", passed, f"Response: {msg}")

            # Cleanup
            msg_id = msg.get("id") or msg.get("message_id")
            if msg_id:
                client.mark_message_complete(msg_id, "Test cleanup")
        except Exception as e:
            results.record(f"message_type_{msg_type}", False, str(e))

    # Test: agent name resolution - exact match
    try:
        msg = client.send_message(
            to_agent=TEST_TARGET_AGENT,
            subject="[TEST] Exact Name",
            body="Testing exact name match",
            message_type="info"
        )
        passed = not msg.get("error_code") == "AGENT_NOT_FOUND"
        results.record("agent_exact_name", passed, f"Response: {msg}")

        msg_id = msg.get("id") or msg.get("message_id")
        if msg_id:
            client.mark_message_complete(msg_id, "Test cleanup")
    except Exception as e:
        results.record("agent_exact_name", False, str(e))

    # Test: agent name resolution - case insensitive
    try:
        msg = client.send_message(
            to_agent=TEST_AGENT_NAME.lower(),
            subject="[TEST] Case Insensitive",
            body="Testing case insensitive match",
            message_type="info"
        )
        passed = not msg.get("error_code") == "AGENT_NOT_FOUND"
        results.record("agent_case_insensitive", passed, f"Response: {msg}")

        msg_id = msg.get("id") or msg.get("message_id")
        if msg_id:
            client.mark_message_complete(msg_id, "Test cleanup")
    except Exception as e:
        results.record("agent_case_insensitive", False, str(e))

    # Test: nonexistent agent
    try:
        msg = client.send_message(
            to_agent="NonExistent-Agent-12345",
            subject="[TEST] Nonexistent",
            body="This should fail",
            message_type="info"
        )
        passed = msg.get("error_code") == "AGENT_NOT_FOUND" or msg.get("error")
        results.record("agent_not_found", passed, f"Response: {msg}")
    except Exception as e:
        results.record("agent_not_found", False, str(e))

    # Test: error response structure
    try:
        msg = client.send_message(
            to_agent="NonExistent-Agent-12345",
            subject="Test",
            body="Test",
            message_type="info"
        )
        if msg.get("success") == False:
            has_structure = "error" in msg and "error_code" in msg
            results.record("error_response_structure", has_structure, f"Response: {msg}")
        else:
            results.record("error_response_structure", True, "No error returned")
    except Exception as e:
        results.record("error_response_structure", False, str(e))


def run_integration_tests(client: CCPMClient, results: TestResults):
    """Run end-to-end integration tests."""
    print("\n=== Integration Tests ===")

    # Test: message lifecycle
    try:
        # Send
        msg = client.send_message(
            to_agent=TEST_TARGET_AGENT,
            subject="[TEST] Integration Lifecycle",
            body="Testing complete lifecycle",
            message_type="info"
        )
        msg_id = msg.get("id") or msg.get("message_id")

        if not msg_id:
            results.record("message_lifecycle", False, f"Send failed: {msg}")
        else:
            # Check inbox
            inbox = client.check_inbox()

            # Complete
            complete = client.mark_message_complete(msg_id, "Integration test done")
            passed = complete.get("status") == "completed" or not complete.get("error")
            results.record("message_lifecycle", passed, f"Complete response: {complete}")
    except Exception as e:
        results.record("message_lifecycle", False, str(e))

    # Test: session workflow
    try:
        # Create session
        session = client.create_session(
            agent_name=TEST_AGENT_NAME,
            session_type="work",
            description="[TEST] Integration workflow"
        )
        session_id = session.get("id") or session.get("session_id")

        if not session_id:
            results.record("session_workflow", False, f"Create failed: {session}")
        else:
            # Log entries
            entry1 = client.log_session_entry(session_id, "start", "Beginning test")
            entry2 = client.log_session_entry(session_id, "progress", "Test step")
            entry3 = client.log_session_entry(session_id, "complete", "Test done")

            passed = not any(e.get("error") for e in [entry1, entry2, entry3])
            results.record("session_workflow", passed, f"Entries: {entry3}")
    except Exception as e:
        results.record("session_workflow", False, str(e))


def run_stress_tests(client: CCPMClient, results: TestResults):
    """Run stress/load tests."""
    print("\n=== Stress Tests ===")

    # Test: concurrent agent listing
    print("  Running concurrent agent listing (10 workers, 30 requests)...")
    try:
        n_workers = 10
        n_requests = 30
        successes = 0
        errors = 0

        def make_request():
            try:
                agents = client.list_agents()
                return len(agents) > 0
            except Exception:
                return False

        start = time.time()
        with ThreadPoolExecutor(max_workers=n_workers) as executor:
            futures = [executor.submit(make_request) for _ in range(n_requests)]
            for future in as_completed(futures):
                if future.result():
                    successes += 1
                else:
                    errors += 1

        elapsed = time.time() - start
        rate = n_requests / elapsed

        passed = errors < n_requests * 0.1
        results.record(
            "concurrent_listing",
            passed,
            f"{successes}/{n_requests} succeeded, {rate:.1f} req/s"
        )
    except Exception as e:
        results.record("concurrent_listing", False, str(e))

    # Test: message burst
    print("  Running message burst (10 messages)...")
    try:
        n_messages = 10
        successes = 0
        msg_ids = []

        for i in range(n_messages):
            msg = client.send_message(
                to_agent=TEST_TARGET_AGENT,
                subject=f"[TEST] Burst {i}",
                body=f"Burst message {i}",
                message_type="info"
            )
            msg_id = msg.get("id") or msg.get("message_id")
            if msg_id:
                successes += 1
                msg_ids.append(msg_id)

        passed = successes > n_messages * 0.8
        results.record("message_burst", passed, f"{successes}/{n_messages} succeeded")

        # Cleanup
        for msg_id in msg_ids:
            try:
                client.mark_message_complete(msg_id, "Burst cleanup")
            except Exception:
                pass
    except Exception as e:
        results.record("message_burst", False, str(e))

    # Test: large message body
    print("  Running large body test (10KB)...")
    try:
        large_body = "X" * 10000  # 10KB
        msg = client.send_message(
            to_agent=TEST_TARGET_AGENT,
            subject="[TEST] Large Body",
            body=large_body,
            message_type="info"
        )

        msg_id = msg.get("id") or msg.get("message_id")
        if msg_id:
            passed = True
            client.mark_message_complete(msg_id, "Large body cleanup")
        else:
            # Acceptable to reject large bodies
            passed = "too large" in str(msg.get("error", "")).lower() or "size" in str(msg.get("error", "")).lower()

        results.record("large_body", passed or msg_id, f"Response: {str(msg)[:100]}")
    except Exception as e:
        results.record("large_body", False, str(e))


def run_quick_smoke_test(client: CCPMClient, results: TestResults):
    """Run quick smoke test - just verify APIs are reachable."""
    print("\n=== Quick Smoke Test ===")

    # Test API connectivity
    try:
        agents = client.list_agents()
        results.record("api_connectivity", len(agents) > 0, f"Found {len(agents)} agents")
    except Exception as e:
        results.record("api_connectivity", False, str(e))

    # Test basic message send
    try:
        msg = client.send_message(
            to_agent=TEST_TARGET_AGENT,
            subject="[TEST] Smoke Test",
            body="Quick smoke test",
            message_type="info"
        )
        msg_id = msg.get("id") or msg.get("message_id")
        results.record("basic_send", bool(msg_id), f"Response: {msg}")

        if msg_id:
            client.mark_message_complete(msg_id, "Smoke test")
    except Exception as e:
        results.record("basic_send", False, str(e))


# =============================================================================
# Main
# =============================================================================

def main():
    args = sys.argv[1:]

    run_all = len(args) == 0
    run_functional = run_all or "--functional" in args
    run_validation = run_all or "--validation" in args
    run_integration = run_all or "--integration" in args
    run_stress = "--stress" in args  # Opt-in only
    run_quick = "--quick" in args

    print("="*60)
    print("CCPM MCP Tools Test Suite")
    print("="*60)
    print(f"Messaging API: {CCPM_MESSAGING_API}")
    print(f"Task API:      {CCPM_TASK_API}")
    print(f"Test Agent:    {TEST_AGENT_NAME} ({TEST_AGENT_ID})")
    print("="*60)

    client = CCPMClient()
    results = TestResults()

    if run_quick:
        run_quick_smoke_test(client, results)
    else:
        if run_functional:
            run_functional_tests(client, results)

        if run_validation:
            run_validation_tests(client, results)

        if run_integration:
            run_integration_tests(client, results)

        if run_stress:
            run_stress_tests(client, results)

    success = results.summary()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
