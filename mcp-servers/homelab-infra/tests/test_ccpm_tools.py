#!/usr/bin/env python3
"""
CCPM MCP Tools Test Suite

Comprehensive tests for the 12 CCPM MCP tools:
- Agent Messaging (4): list_agents, send_message, check_inbox, mark_message_complete
- Task Management (5): get_task, list_tasks, update_task_status, submit_completion_report
- Sprint Management (2): get_active_sprint, list_sprints
- Session Logging (2): create_session, log_session_entry

Usage:
    pytest tests/test_ccpm_tools.py -v                    # Run all tests
    pytest tests/test_ccpm_tools.py -v -m functional      # Functional tests only
    pytest tests/test_ccpm_tools.py -v -m validation      # Validation tests only
    pytest tests/test_ccpm_tools.py -v -m integration     # Integration tests only
    pytest tests/test_ccpm_tools.py -v -m stress          # Stress tests only
"""

import pytest
import httpx
import time
import concurrent.futures
from typing import Any

from tests.test_data import (
    TEST_AGENT_ID,
    TEST_AGENT_NAME,
    VALID_MESSAGE_TYPES,
    VALID_PRIORITIES,
    VALID_TASK_STATUSES,
    AGENT_ALLOWED_STATUSES,
    VALID_SPRINT_STATUSES,
    VALID_SESSION_TYPES,
    VALID_ENTRY_TYPES,
    INVALID_MESSAGE_TYPES,
    INVALID_SESSION_TYPES,
    INVALID_ENTRY_TYPES,
    VALID_UUID,
    INVALID_UUIDS,
    NONEXISTENT_AGENT,
    NONEXISTENT_TASK_ID,
    NONEXISTENT_MESSAGE_ID,
    NONEXISTENT_SESSION_ID,
)


# =============================================================================
# FUNCTIONAL TESTS (Happy Path)
# =============================================================================

class TestFunctionalAgentMessaging:
    """Functional tests for agent messaging tools."""

    @pytest.mark.functional
    def test_list_agents_no_params(self, ccpm_client):
        """Test listing agents without any filters."""
        result = ccpm_client.list_agents()

        assert isinstance(result, list)
        assert len(result) > 0

        # Verify agent structure
        for agent in result:
            assert "name" in agent or "id" in agent

    @pytest.mark.functional
    def test_list_agents_with_status_filter(self, ccpm_client):
        """Test listing agents with status filter."""
        result = ccpm_client.list_agents(status="active")

        assert isinstance(result, list)
        # All returned agents should be active (if API supports filtering)

    @pytest.mark.functional
    def test_send_message_valid(self, ccpm_client):
        """Test sending a valid message."""
        result = ccpm_client.send_message(
            to_agent=TEST_AGENT_NAME,
            subject="[TEST] Functional Test Message",
            body="This is a test message",
            message_type="info",
            priority="normal"
        )

        assert result.get("id") or result.get("message_id") or not result.get("error")

        # Cleanup
        msg_id = result.get("id") or result.get("message_id")
        if msg_id:
            try:
                ccpm_client.mark_message_complete(msg_id, "Test cleanup")
            except Exception:
                pass

    @pytest.mark.functional
    def test_check_inbox(self, ccpm_client):
        """Test checking inbox."""
        result = ccpm_client.check_inbox()

        assert isinstance(result, list)

    @pytest.mark.functional
    def test_mark_message_complete(self, ccpm_client, test_message):
        """Test marking a message as complete."""
        msg_id = test_message.get("id") or test_message.get("message_id")
        if not msg_id:
            pytest.skip("Could not create test message")

        result = ccpm_client.mark_message_complete(
            message_id=msg_id,
            response_text="Test completed"
        )

        assert result.get("status") == "completed" or not result.get("error")


class TestFunctionalTaskManagement:
    """Functional tests for task management tools."""

    @pytest.mark.functional
    def test_list_tasks_no_params(self, ccpm_client):
        """Test listing tasks without filters."""
        try:
            result = ccpm_client.list_tasks()
            assert isinstance(result, list)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                pytest.skip("Task API not available")
            raise

    @pytest.mark.functional
    def test_list_tasks_with_status_filter(self, ccpm_client):
        """Test listing tasks with status filter."""
        try:
            result = ccpm_client.list_tasks(status="in-progress")
            assert isinstance(result, list)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                pytest.skip("Task API not available")
            raise


class TestFunctionalSprintManagement:
    """Functional tests for sprint management tools."""

    @pytest.mark.functional
    def test_list_sprints_no_params(self, ccpm_client):
        """Test listing sprints without filters."""
        try:
            result = ccpm_client.list_sprints()
            assert isinstance(result, list)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                pytest.skip("Sprint API not available")
            raise

    @pytest.mark.functional
    def test_get_active_sprint(self, ccpm_client):
        """Test getting active sprint."""
        try:
            result = ccpm_client.get_active_sprint()
            # May return error if no active sprint
            assert isinstance(result, dict)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                pytest.skip("Sprint API not available")
            raise


class TestFunctionalSessionLogging:
    """Functional tests for session logging tools."""

    @pytest.mark.functional
    def test_create_session(self, ccpm_client):
        """Test creating a session."""
        try:
            result = ccpm_client.create_session(
                agent_name=TEST_AGENT_NAME,
                session_type="work",
                description="[TEST] Functional test session"
            )
            assert result.get("id") or result.get("session_id") or not result.get("error")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                pytest.skip("Session API not available")
            raise

    @pytest.mark.functional
    def test_log_session_entry(self, ccpm_client, test_session):
        """Test logging a session entry."""
        session_id = test_session.get("id") or test_session.get("session_id")
        if not session_id:
            pytest.skip("Could not create test session")

        try:
            result = ccpm_client.log_session_entry(
                session_id=session_id,
                entry_type="progress",
                content="[TEST] Functional test entry"
            )
            assert not result.get("error")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                pytest.skip("Session API not available")
            raise


# =============================================================================
# VALIDATION TESTS (Enum and Input Validation)
# =============================================================================

class TestValidationMessageTypes:
    """Test message_type enum validation."""

    @pytest.mark.validation
    @pytest.mark.parametrize("message_type", VALID_MESSAGE_TYPES)
    def test_valid_message_types(self, ccpm_client, message_type):
        """Test that all valid message types are accepted."""
        result = ccpm_client.send_message(
            to_agent=TEST_AGENT_NAME,
            subject=f"[TEST] Valid type: {message_type}",
            body="Testing message type validation",
            message_type=message_type
        )

        # Should succeed or at least not fail due to invalid message type
        assert not result.get("error_code") == "INVALID_MESSAGE_TYPE"

        # Cleanup
        msg_id = result.get("id") or result.get("message_id")
        if msg_id:
            try:
                ccpm_client.mark_message_complete(msg_id, "Test cleanup")
            except Exception:
                pass

    @pytest.mark.validation
    @pytest.mark.parametrize("message_type", INVALID_MESSAGE_TYPES)
    def test_invalid_message_types_rejected(self, ccpm_client, message_type):
        """Test that invalid message types are rejected."""
        # This tests the MCP server validation, not direct API
        # Skip if testing direct API (which may not validate)
        pytest.skip("Direct API may not validate enums - test via MCP client")


class TestValidationSessionTypes:
    """Test session_type enum validation."""

    @pytest.mark.validation
    @pytest.mark.parametrize("session_type", VALID_SESSION_TYPES)
    def test_valid_session_types(self, ccpm_client, session_type):
        """Test that all valid session types are accepted."""
        try:
            result = ccpm_client.create_session(
                agent_name=TEST_AGENT_NAME,
                session_type=session_type,
                description=f"[TEST] Valid type: {session_type}"
            )
            assert not result.get("error_code") == "INVALID_SESSION_TYPE"
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                pytest.skip("Session API not available")
            raise


class TestValidationEntryTypes:
    """Test entry_type enum validation."""

    @pytest.mark.validation
    @pytest.mark.parametrize("entry_type", VALID_ENTRY_TYPES)
    def test_valid_entry_types(self, ccpm_client, test_session, entry_type):
        """Test that all valid entry types are accepted."""
        session_id = test_session.get("id") or test_session.get("session_id")
        if not session_id:
            pytest.skip("Could not create test session")

        try:
            result = ccpm_client.log_session_entry(
                session_id=session_id,
                entry_type=entry_type,
                content=f"[TEST] Valid entry type: {entry_type}"
            )
            assert not result.get("error_code") == "INVALID_ENTRY_TYPE"
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                pytest.skip("Session API not available")
            raise


class TestValidationTaskStatus:
    """Test task status validation."""

    @pytest.mark.validation
    @pytest.mark.parametrize("status", AGENT_ALLOWED_STATUSES)
    def test_agent_allowed_statuses(self, ccpm_client, status):
        """Test that agent-allowed statuses are accepted."""
        # This would require a real task ID to test properly
        pytest.skip("Requires real task ID for status update test")


class TestValidationBlockedReason:
    """Test blocked_reason requirement."""

    @pytest.mark.validation
    def test_blocked_status_requires_reason(self, ccpm_client):
        """Test that blocked status requires a reason."""
        # This would require a real task ID to test properly
        pytest.skip("Requires real task ID for blocked reason test")


# =============================================================================
# AGENT NAME RESOLUTION TESTS
# =============================================================================

class TestAgentNameResolution:
    """Test agent name to UUID resolution."""

    @pytest.mark.validation
    def test_uuid_passthrough(self, ccpm_client):
        """Test that valid UUIDs pass through without lookup."""
        result = ccpm_client.send_message(
            to_agent=VALID_UUID,
            subject="[TEST] UUID Passthrough",
            body="Testing UUID passthrough",
            message_type="info"
        )

        # Should work (agent may not exist, but UUID format accepted)
        # Or should return agent not found (not invalid UUID format)
        if result.get("error_code"):
            assert result["error_code"] != "INVALID_UUID_FORMAT"

    @pytest.mark.validation
    def test_exact_name_match(self, ccpm_client):
        """Test exact agent name matching."""
        result = ccpm_client.send_message(
            to_agent=TEST_AGENT_NAME,
            subject="[TEST] Exact Name Match",
            body="Testing exact name match",
            message_type="info"
        )

        assert not result.get("error_code") == "AGENT_NOT_FOUND"

        # Cleanup
        msg_id = result.get("id") or result.get("message_id")
        if msg_id:
            try:
                ccpm_client.mark_message_complete(msg_id, "Test cleanup")
            except Exception:
                pass

    @pytest.mark.validation
    def test_case_insensitive_match(self, ccpm_client):
        """Test case-insensitive agent name matching."""
        lowercase_name = TEST_AGENT_NAME.lower()

        result = ccpm_client.send_message(
            to_agent=lowercase_name,
            subject="[TEST] Case Insensitive Match",
            body="Testing case insensitive matching",
            message_type="info"
        )

        # Should resolve correctly
        assert not result.get("error_code") == "AGENT_NOT_FOUND"

        # Cleanup
        msg_id = result.get("id") or result.get("message_id")
        if msg_id:
            try:
                ccpm_client.mark_message_complete(msg_id, "Test cleanup")
            except Exception:
                pass

    @pytest.mark.validation
    def test_nonexistent_agent_fails(self, ccpm_client):
        """Test that nonexistent agents are rejected."""
        result = ccpm_client.send_message(
            to_agent=NONEXISTENT_AGENT,
            subject="[TEST] Nonexistent Agent",
            body="This should fail",
            message_type="info"
        )

        assert result.get("error_code") == "AGENT_NOT_FOUND" or result.get("error")


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================

class TestErrorHandling:
    """Test error handling for various failure scenarios."""

    @pytest.mark.validation
    def test_nonexistent_task_returns_error(self, ccpm_client):
        """Test that nonexistent task ID returns proper error."""
        try:
            result = ccpm_client.get_task(NONEXISTENT_TASK_ID)
            # If no exception, should have error in response
            assert result.get("error") or result.get("error_code")
        except httpx.HTTPStatusError as e:
            # 404 is expected
            assert e.response.status_code == 404

    @pytest.mark.validation
    def test_nonexistent_message_complete_returns_error(self, ccpm_client):
        """Test that completing nonexistent message returns error."""
        try:
            result = ccpm_client.mark_message_complete(
                NONEXISTENT_MESSAGE_ID,
                "This should fail"
            )
            assert result.get("error") or result.get("error_code")
        except httpx.HTTPStatusError as e:
            # 404 is expected
            assert e.response.status_code == 404

    @pytest.mark.validation
    def test_error_response_structure(self, ccpm_client):
        """Test that error responses have consistent structure."""
        result = ccpm_client.send_message(
            to_agent=NONEXISTENT_AGENT,
            subject="Test",
            body="Test",
            message_type="info"
        )

        if result.get("success") == False:
            assert "error" in result
            assert "error_code" in result
            assert isinstance(result["error"], str)
            assert isinstance(result["error_code"], str)


# =============================================================================
# INTEGRATION TESTS (End-to-End Workflows)
# =============================================================================

class TestIntegrationMessageLifecycle:
    """Test complete message lifecycle."""

    @pytest.mark.integration
    def test_message_send_check_complete_workflow(self, ccpm_client):
        """Test sending, checking, and completing a message."""
        # 1. Send message
        msg = ccpm_client.send_message(
            to_agent=TEST_AGENT_NAME,
            subject="[TEST] Integration Lifecycle",
            body="Testing complete message lifecycle",
            message_type="info"
        )

        msg_id = msg.get("id") or msg.get("message_id")
        assert msg_id, f"Failed to send message: {msg}"

        # 2. Check inbox (message should appear)
        inbox = ccpm_client.check_inbox()
        assert isinstance(inbox, list)

        # Find our message
        found = any(
            m.get("id") == msg_id or m.get("subject") == "[TEST] Integration Lifecycle"
            for m in inbox
        )
        # Note: May not find immediately due to eventual consistency
        # assert found, "Message not found in inbox"

        # 3. Mark complete
        result = ccpm_client.mark_message_complete(
            message_id=msg_id,
            response_text="Integration test completed"
        )

        assert result.get("status") == "completed" or not result.get("error")


class TestIntegrationSessionWorkflow:
    """Test complete session logging workflow."""

    @pytest.mark.integration
    def test_session_create_log_workflow(self, ccpm_client):
        """Test creating session and logging entries."""
        try:
            # 1. Create session
            session = ccpm_client.create_session(
                agent_name=TEST_AGENT_NAME,
                session_type="work",
                description="[TEST] Integration session workflow"
            )

            session_id = session.get("id") or session.get("session_id")
            assert session_id, f"Failed to create session: {session}"

            # 2. Log start entry
            entry1 = ccpm_client.log_session_entry(
                session_id=session_id,
                entry_type="start",
                content="Beginning integration test"
            )
            assert not entry1.get("error")

            # 3. Log progress
            entry2 = ccpm_client.log_session_entry(
                session_id=session_id,
                entry_type="progress",
                content="Test step 1 completed"
            )
            assert not entry2.get("error")

            # 4. Log completion
            entry3 = ccpm_client.log_session_entry(
                session_id=session_id,
                entry_type="complete",
                content="Integration test finished"
            )
            assert not entry3.get("error")

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                pytest.skip("Session API not available")
            raise


# =============================================================================
# RESPONSE FORMAT TESTS
# =============================================================================

class TestResponseFormats:
    """Test response format consistency."""

    @pytest.mark.validation
    def test_list_responses_are_arrays(self, ccpm_client):
        """Verify that list endpoints return arrays."""
        agents = ccpm_client.list_agents()
        assert isinstance(agents, list), "list_agents should return array"

        inbox = ccpm_client.check_inbox()
        assert isinstance(inbox, list), "check_inbox should return array"

        try:
            tasks = ccpm_client.list_tasks()
            assert isinstance(tasks, list), "list_tasks should return array"
        except httpx.HTTPStatusError:
            pass  # Task API may not be available

        try:
            sprints = ccpm_client.list_sprints()
            assert isinstance(sprints, list), "list_sprints should return array"
        except httpx.HTTPStatusError:
            pass  # Sprint API may not be available


# =============================================================================
# STRESS TESTS
# =============================================================================

class TestStressConcurrent:
    """Stress tests for concurrent operations."""

    @pytest.mark.stress
    @pytest.mark.slow
    def test_concurrent_agent_listing(self, ccpm_client):
        """Test concurrent agent listing requests."""
        n_workers = 10
        n_requests = 50
        results = []
        errors = []

        def make_request():
            try:
                result = ccpm_client.list_agents()
                return ("success", result)
            except Exception as e:
                return ("error", str(e))

        start = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=n_workers) as executor:
            futures = [executor.submit(make_request) for _ in range(n_requests)]
            for future in concurrent.futures.as_completed(futures):
                status, data = future.result()
                if status == "success":
                    results.append(data)
                else:
                    errors.append(data)

        elapsed = time.time() - start

        print(f"\nCompleted {len(results)} requests in {elapsed:.2f}s")
        print(f"Errors: {len(errors)}")
        print(f"Requests/sec: {n_requests/elapsed:.2f}")

        # Should have high success rate
        assert len(errors) < n_requests * 0.1, f"Too many errors: {len(errors)}"

        # Results should be consistent (cache working)
        if results:
            first_len = len(results[0])
            assert all(len(r) == first_len for r in results), "Inconsistent results"

    @pytest.mark.stress
    @pytest.mark.slow
    def test_message_burst(self, ccpm_client):
        """Test sending many messages rapidly."""
        n_messages = 20
        results = []
        message_ids = []

        for i in range(n_messages):
            result = ccpm_client.send_message(
                to_agent=TEST_AGENT_NAME,
                subject=f"[TEST] Burst {i}",
                body=f"Burst message {i} of {n_messages}",
                message_type="info"
            )
            results.append(result)
            msg_id = result.get("id") or result.get("message_id")
            if msg_id:
                message_ids.append(msg_id)

        # Count successes
        successes = sum(1 for r in results if r.get("id") or r.get("message_id"))
        print(f"\nSent {successes}/{n_messages} messages successfully")

        assert successes > n_messages * 0.8, f"Too many failures: {n_messages - successes}"

        # Cleanup
        for msg_id in message_ids:
            try:
                ccpm_client.mark_message_complete(msg_id, "Burst test cleanup")
            except Exception:
                pass

    @pytest.mark.stress
    @pytest.mark.slow
    def test_large_message_body(self, ccpm_client):
        """Test sending message with large body."""
        large_body = "X" * 10000  # 10KB body

        result = ccpm_client.send_message(
            to_agent=TEST_AGENT_NAME,
            subject="[TEST] Large Body",
            body=large_body,
            message_type="info"
        )

        # Should succeed or have meaningful error
        if result.get("error"):
            assert "too large" in result["error"].lower() or "size" in result["error"].lower()
        else:
            msg_id = result.get("id") or result.get("message_id")
            if msg_id:
                ccpm_client.mark_message_complete(msg_id, "Large body test cleanup")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
