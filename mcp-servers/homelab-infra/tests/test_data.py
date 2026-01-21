"""
Test data and constants for CCPM MCP tools testing.
"""

# API Endpoints
CCPM_MESSAGING_API = "http://10.0.1.210:8000/api/v1"
CCPM_TASK_API = "http://10.0.1.210:8080/api"
MCP_ENDPOINT = "http://10.0.1.202:8080"

# Test Agent
TEST_AGENT_ID = "aaaaaaaa-bbbb-cccc-dddd-222222222222"
TEST_AGENT_NAME = "HomeLab-Agent"

# Valid enum values
VALID_MESSAGE_TYPES = [
    "task_assignment", "task_request", "feature_request", "bug_report",
    "status_request", "completion_signal", "alert", "info", "query", "response"
]

VALID_PRIORITIES = ["low", "normal", "high"]

VALID_TASK_STATUSES = ["pending", "in-progress", "review", "blocked", "testing", "done"]

AGENT_ALLOWED_STATUSES = ["in-progress", "review", "blocked", "testing"]

VALID_SPRINT_STATUSES = ["planning", "active", "completed"]

VALID_SESSION_TYPES = ["work", "planning", "review"]

VALID_ENTRY_TYPES = ["start", "progress", "decision", "issue", "complete"]

# Invalid values for testing
INVALID_MESSAGE_TYPES = ["invalid", "INFO", "Invalid", "", "123", "task-assignment"]
INVALID_PRIORITIES = ["urgent", "LOW", "HIGH", "", "critical"]
INVALID_TASK_STATUSES = ["Invalid", "PENDING", "complete", ""]
INVALID_SESSION_TYPES = ["debug", "WORK", "test", ""]
INVALID_ENTRY_TYPES = ["end", "START", "finish", ""]

# Test UUIDs
VALID_UUID = "aaaaaaaa-bbbb-cccc-dddd-222222222222"
INVALID_UUIDS = [
    "not-a-uuid",
    "aaaa-bbbb-cccc-dddd",  # Too short
    "aaaaaaaa-bbbb-cccc-dddd-222222222222-extra",  # Too long
    "gggggggg-hhhh-iiii-jjjj-kkkkkkkkkkkk",  # Invalid chars (but valid format)
]

# Test messages
TEST_MESSAGE = {
    "to_agent": TEST_AGENT_NAME,
    "subject": "Test Message",
    "body": "This is a test message for integration testing",
    "message_type": "info",
    "priority": "normal"
}

# Test session
TEST_SESSION = {
    "agent_name": TEST_AGENT_NAME,
    "session_type": "work",
    "description": "Integration test session"
}

# Nonexistent resources
NONEXISTENT_AGENT = "NonExistent-Agent-12345"
NONEXISTENT_TASK_ID = 999999
NONEXISTENT_MESSAGE_ID = "00000000-0000-0000-0000-000000000000"
NONEXISTENT_SESSION_ID = 999999
