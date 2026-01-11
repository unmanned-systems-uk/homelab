# Check Agent Messages

Check for pending messages from other agents in the CCPM system.

## Instructions

1. Query your inbox:
```bash
curl -s "http://10.0.1.210:8000/api/v1/agent-messages/inbox?agent_id=aaaaaaaa-bbbb-cccc-dddd-222222222222" | python3 -m json.tool
```

2. For each pending message:
   - Read the message content
   - Take appropriate action based on message_type
   - Mark as read: `POST /api/v1/agent-messages/{id}/read`
   - When done: `POST /api/v1/agent-messages/{id}/complete`

3. If the message requires a response, include it when marking complete:
```bash
curl -X POST "http://10.0.1.210:8000/api/v1/agent-messages/{MESSAGE_ID}/complete" \
  -H "Content-Type: application/json" \
  -d '{"response": "Your response here"}'
```

## Message Types
- `task_assignment` - You have been assigned work
- `status_request` - Someone is asking for your status
- `query` - A question requiring your response
- `alert` - Urgent notification
- `info` - Informational (acknowledge with read)

## Quick Check
```bash
# Just count pending messages
curl -s "http://10.0.1.210:8000/api/v1/agent-messages/inbox?agent_id=aaaaaaaa-bbbb-cccc-dddd-222222222222&status=pending" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"📬 {len(d)} pending message(s)\" if isinstance(d, list) else \"📭 No messages\")"
```
