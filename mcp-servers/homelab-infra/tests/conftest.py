"""
Pytest fixtures for CCPM MCP tools testing.
"""

import pytest
import httpx
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_data import (
    CCPM_MESSAGING_API,
    CCPM_TASK_API,
    TEST_AGENT_ID,
    TEST_AGENT_NAME,
)


class CCPMClient:
    """Client for making direct CCPM API calls (bypassing MCP for testing)."""

    def __init__(self, messaging_api: str, task_api: str, agent_id: str):
        self.messaging_api = messaging_api
        self.task_api = task_api
        self.agent_id = agent_id
        self.timeout = 10.0

    # Agent Messaging Tools

    def list_agents(self, status: str = None, agent_type: str = None) -> dict:
        """List all registered agents."""
        params = {}
        if status:
            params["status"] = status
        if agent_type:
            params["agent_type"] = agent_type

        response = httpx.get(
            f"{self.messaging_api}/agents",
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def send_message(
        self,
        to_agent: str,
        subject: str,
        body: str,
        message_type: str = "info",
        priority: str = "normal",
        from_agent_id: str = None
    ) -> dict:
        """Send a message to another agent."""
        sender_id = from_agent_id or self.agent_id

        # Resolve agent name to UUID if needed
        if len(to_agent) != 36 or to_agent.count('-') != 4:
            agents = self.list_agents()
            agent_map = {a["name"]: a for a in agents}
            if to_agent in agent_map:
                to_agent_id = agent_map[to_agent]["id"]
            else:
                # Try case-insensitive
                for name, agent in agent_map.items():
                    if name.lower() == to_agent.lower():
                        to_agent_id = agent["id"]
                        break
                else:
                    return {
                        "success": False,
                        "error": f"Agent not found: {to_agent}",
                        "error_code": "AGENT_NOT_FOUND"
                    }
        else:
            to_agent_id = to_agent

        response = httpx.post(
            f"{self.messaging_api}/agent-messages",
            params={"from_agent_id": sender_id},
            json={
                "to_agent_id": to_agent_id,
                "subject": subject,
                "body": body,
                "message_type": message_type,
                "priority": priority
            },
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def check_inbox(self, agent_id: str = None, include_read: bool = False) -> list:
        """Check inbox for pending messages."""
        aid = agent_id or self.agent_id
        params = {"agent_id": aid}
        if not include_read:
            params["status"] = "pending"

        response = httpx.get(
            f"{self.messaging_api}/agent-messages/inbox",
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()
        data = response.json()

        # Handle paginated response
        if isinstance(data, dict) and "items" in data:
            return data["items"]
        return data

    def mark_message_complete(self, message_id: str, response_text: str = None) -> dict:
        """Mark a message as complete."""
        payload = {}
        if response_text:
            payload["response"] = response_text

        response = httpx.post(
            f"{self.messaging_api}/agent-messages/{message_id}/complete",
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    # Task Management Tools

    def get_task(self, task_id: int) -> dict:
        """Get task details."""
        response = httpx.get(
            f"{self.task_api}/tasks/{task_id}",
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def list_tasks(
        self,
        sprint_id: int = None,
        status: str = None,
        assignee: str = None
    ) -> list:
        """List tasks with optional filters."""
        params = {}
        if sprint_id:
            params["sprint_id"] = sprint_id
        if status:
            params["status"] = status
        if assignee:
            params["assigned_to"] = assignee

        response = httpx.get(
            f"{self.task_api}/tasks",
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()
        data = response.json()

        if isinstance(data, dict) and "tasks" in data:
            return data["tasks"]
        return data

    def update_task_status(
        self,
        task_id: int,
        status: str,
        blocked_reason: str = None
    ) -> dict:
        """Update task status."""
        payload = {"status": status}
        if blocked_reason:
            payload["blocked_reason"] = blocked_reason

        response = httpx.put(
            f"{self.task_api}/agent/tasks/{task_id}/status",
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def submit_completion_report(
        self,
        task_id: int,
        report: str,
        submitted_by: str
    ) -> dict:
        """Submit completion report for a task."""
        response = httpx.post(
            f"{self.task_api}/tasks/{task_id}/report",
            json={"report": report, "submitted_by": submitted_by},
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    # Sprint Management Tools

    def get_active_sprint(self) -> dict:
        """Get the currently active sprint."""
        response = httpx.get(
            f"{self.task_api}/sprints",
            params={"status": "active"},
            timeout=self.timeout
        )
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list) and data:
            return data[0]
        if isinstance(data, dict) and "sprints" in data and data["sprints"]:
            return data["sprints"][0]
        return {"success": False, "error": "No active sprint", "error_code": "NO_ACTIVE_SPRINT"}

    def list_sprints(self, status: str = None) -> list:
        """List sprints with optional filter."""
        params = {}
        if status:
            params["status"] = status

        response = httpx.get(
            f"{self.task_api}/sprints",
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()
        data = response.json()

        if isinstance(data, dict) and "sprints" in data:
            return data["sprints"]
        return data

    # Session Logging Tools

    def create_session(
        self,
        agent_name: str,
        session_type: str = "work",
        description: str = None
    ) -> dict:
        """Create a new session."""
        payload = {
            "agent_name": agent_name,
            "session_type": session_type
        }
        if description:
            payload["description"] = description

        response = httpx.post(
            f"{self.task_api}/sessions",
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def log_session_entry(
        self,
        session_id: int,
        entry_type: str,
        content: str
    ) -> dict:
        """Add an entry to a session."""
        response = httpx.post(
            f"{self.task_api}/sessions/{session_id}/entries",
            json={"entry_type": entry_type, "content": content},
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()


@pytest.fixture(scope="session")
def ccpm_client():
    """Create a CCPM client for testing."""
    return CCPMClient(
        messaging_api=CCPM_MESSAGING_API,
        task_api=CCPM_TASK_API,
        agent_id=TEST_AGENT_ID
    )


@pytest.fixture(scope="function")
def test_message(ccpm_client):
    """Create a test message and clean up after."""
    msg = ccpm_client.send_message(
        to_agent=TEST_AGENT_NAME,
        subject="[TEST] Fixture Message",
        body="This message was created by a test fixture",
        message_type="info"
    )
    yield msg

    # Cleanup: mark as complete
    if msg.get("id"):
        try:
            ccpm_client.mark_message_complete(msg["id"], "Test cleanup")
        except Exception:
            pass


@pytest.fixture(scope="function")
def test_session(ccpm_client):
    """Create a test session."""
    session = ccpm_client.create_session(
        agent_name=TEST_AGENT_NAME,
        session_type="work",
        description="[TEST] Fixture Session"
    )
    yield session
    # Sessions don't need cleanup - they're append-only logs


@pytest.fixture(scope="session")
def api_available():
    """Check if CCPM APIs are available."""
    try:
        httpx.get(f"{CCPM_MESSAGING_API}/agents", timeout=5.0)
        return True
    except Exception:
        return False


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "functional: Functional/happy path tests")
    config.addinivalue_line("markers", "validation: Input validation tests")
    config.addinivalue_line("markers", "integration: End-to-end integration tests")
    config.addinivalue_line("markers", "stress: Stress and load tests")
    config.addinivalue_line("markers", "slow: Tests that take a long time")
