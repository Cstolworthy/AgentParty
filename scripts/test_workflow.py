#!/usr/bin/env python
"""End-to-end test of the AgentParty workflow."""

import asyncio
import json
import sys
from pathlib import Path

import httpx

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

BASE_URL = "http://localhost:8000"


class WorkflowTester:
    """Test the complete workflow."""

    def __init__(self):
        """Initialize tester."""
        self.session_id = None
        self.user_id = "test-user@example.com"

    async def test_health(self):
        """Test health endpoint."""
        print("\n1. Testing health endpoint...")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health")
            result = response.json()
            print(f"   Status: {result['status']}")
            print(f"   Version: {result['version']}")
            assert result["status"] == "healthy"

    async def test_list_resources(self):
        """Test listing agents, workflows, jobs."""
        print("\n2. Testing resource listing...")

        async with httpx.AsyncClient() as client:
            # List agents
            response = await client.get(f"{BASE_URL}/api/agents")
            agents = response.json()
            print(f"   Agents available: {agents['count']}")
            for agent in agents["agents"]:
                print(f"     - {agent}")

            # List workflows
            response = await client.get(f"{BASE_URL}/api/workflows")
            workflows = response.json()
            print(f"   Workflows available: {workflows['count']}")
            for workflow in workflows["workflows"]:
                print(f"     - {workflow}")

            # List jobs
            response = await client.get(f"{BASE_URL}/api/jobs")
            jobs = response.json()
            print(f"   Jobs available: {jobs['count']}")
            for job in jobs["jobs"]:
                print(f"     - {job}")

    async def test_create_session(self):
        """Test session creation."""
        print(f"\n3. Creating session for user: {self.user_id}...")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/mcp",
                json={
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": "create_session",
                        "arguments": {"user_id": self.user_id},
                    },
                    "id": 1,
                },
            )
            result = response.json()

            if "error" in result:
                print(f"   ✗ Error: {result['error']}")
                sys.exit(1)

            # Parse MCP response format
            content = result["result"]["content"][0]["text"]
            session_data = json.loads(content)
            
            self.session_id = session_data["session_id"]
            print(f"   ✓ Session created: {self.session_id}")
            print(f"   User: {session_data['user_id']}")
            print(f"   Expires: {session_data['expires_at']}")

    async def test_get_budget(self):
        """Test budget status."""
        print("\n4. Checking budget status...")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/mcp",
                json={
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": "get_budget_status",
                        "arguments": {"session_id": self.session_id},
                    },
                    "id": 2,
                },
            )
            content = response.json()["result"]["content"][0]["text"]
            result = json.loads(content)
            print(f"   Total budget: ${result['total_budget']:.2f}")
            print(f"   Used: ${result['used_budget']:.2f}")
            print(f"   Remaining: ${result['remaining_budget']:.2f}")
            print(f"   Usage: {result['usage_percentage']:.1f}%")

    async def test_get_available_jobs(self):
        """Test getting available jobs."""
        print("\n5. Getting available jobs...")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/mcp",
                json={
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": "get_available_jobs",
                        "arguments": {"session_id": self.session_id},
                    },
                    "id": 3,
                },
            )
            content = response.json()["result"]["content"][0]["text"]
            jobs = json.loads(content)
            print(f"   Found {len(jobs)} jobs:")
            for job in jobs:
                print(f"     - {job['id']}: {job['title']} (Priority: {job['priority']})")

    async def test_start_job(self):
        """Test starting a job."""
        print("\n6. Starting job: example-feature...")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/mcp",
                json={
                    "method": "tools/call",
                    "params": {
                        "name": "start_job",
                        "arguments": {
                            "session_id": self.session_id,
                            "job_id": "example-feature",
                        },
                    },
                },
            )
            result = response.json()["result"]
            print(f"   ✓ Job started: {result['job_title']}")
            print(f"   Workflow: {result['workflow_id']}")
            print(f"   Current step: {result['current_step']}")

    async def test_get_current_task(self):
        """Test getting current task."""
        print("\n7. Getting current task...")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/mcp",
                json={
                    "method": "tools/call",
                    "params": {
                        "name": "get_current_task",
                        "arguments": {"session_id": self.session_id},
                    },
                },
            )
            task = response.json()["result"]
            print(f"   Step: {task['step_name']}")
            print(f"   Agent: {task['agent']}")
            print(f"   Description: {task['description']}")
            print(f"   Status: {task['status']}")

            if "job_context" in task:
                context = task["job_context"]
                print(f"\n   Job Context Preview:")
                lines = context.split("\n")[:5]
                for line in lines:
                    print(f"     {line}")
                if len(context.split("\n")) > 5:
                    print(f"     ... ({len(context.split('\n')) - 5} more lines)")

    async def test_ask_agent(self):
        """Test asking agent for guidance."""
        print("\n8. Asking Manager for guidance...")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/mcp",
                json={
                    "method": "tools/call",
                    "params": {
                        "name": "get_agent_guidance",
                        "arguments": {
                            "session_id": self.session_id,
                            "agent_id": "manager",
                            "question": "What are the key security considerations for this authentication system?",
                        },
                    },
                },
                timeout=30.0,
            )
            result = response.json()["result"]
            print(f"   Agent: {result['agent']}")
            print(f"   Guidance preview:")
            lines = result["guidance"].split("\n")[:8]
            for line in lines:
                print(f"     {line}")
            if len(result["guidance"].split("\n")) > 8:
                print("     ...")

    async def test_submit_work(self):
        """Test submitting work."""
        print("\n9. Submitting completed work...")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/mcp",
                json={
                    "method": "tools/call",
                    "params": {
                        "name": "submit_work",
                        "arguments": {
                            "session_id": self.session_id,
                            "work_description": (
                                "Implemented JWT-based authentication system with:\n"
                                "- User registration with email/password\n"
                                "- Login with JWT token generation\n"
                                "- Password hashing using bcrypt\n"
                                "- Token refresh mechanism\n"
                                "- Rate limiting on login endpoint\n"
                                "- Comprehensive error handling"
                            ),
                            "artifacts": [
                                "src/auth/routes.py",
                                "src/auth/models.py",
                                "src/auth/security.py",
                                "tests/test_auth.py",
                            ],
                        },
                    },
                },
            )
            result = response.json()["result"]
            print(f"   Status: {result['status']}")
            print(f"   Message: {result['message']}")

            if result["status"] == "awaiting_approval":
                print(f"   Requires approval from: {result['approval_agent']}")

    async def test_request_review(self):
        """Test requesting review."""
        print("\n10. Requesting code review from Manager...")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/mcp",
                json={
                    "method": "tools/call",
                    "params": {
                        "name": "request_review",
                        "arguments": {"session_id": self.session_id},
                    },
                },
                timeout=60.0,
            )
            result = response.json()["result"]
            print(f"   Status: {result['status']}")
            print(f"   Message: {result['message']}")

            if "review" in result:
                review = result["review"]
                print(f"\n   Review from: {review['reviewer']}")
                print(f"   Approved: {review['approved']}")
                print(f"   Cost: ${review['cost']:.4f}")
                print(f"\n   Feedback preview:")
                lines = review["feedback"].split("\n")[:10]
                for line in lines:
                    print(f"     {line}")
                if len(review["feedback"].split("\n")) > 10:
                    print("     ...")

    async def test_workflow_status(self):
        """Test getting workflow status."""
        print("\n11. Checking workflow status...")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/mcp",
                json={
                    "method": "tools/call",
                    "params": {
                        "name": "get_workflow_status",
                        "arguments": {"session_id": self.session_id},
                    },
                },
            )
            status = response.json()["result"]
            print(f"   Workflow: {status['workflow_id']}")
            print(f"   Job: {status['job_id']}")
            print(f"   Current step: {status['current_step']}")
            print(f"   Completed: {status['is_completed']}")
            print(f"   Started: {status['started_at']}")

            if status["step_statuses"]:
                print(f"\n   Step statuses:")
                for step_id, step_status in status["step_statuses"].items():
                    print(f"     - {step_id}: {step_status}")

    async def test_final_budget(self):
        """Test final budget after workflow."""
        print("\n12. Final budget check...")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/mcp",
                json={
                    "method": "tools/call",
                    "params": {
                        "name": "get_budget_status",
                        "arguments": {"session_id": self.session_id},
                    },
                },
            )
            result = response.json()["result"]
            print(f"   Total budget: ${result['total_budget']:.2f}")
            print(f"   Used: ${result['used_budget']:.4f}")
            print(f"   Remaining: ${result['remaining_budget']:.4f}")
            print(f"   Usage: {result['usage_percentage']:.2f}%")

    async def run_all_tests(self):
        """Run all tests in sequence."""
        print("=" * 70)
        print("AgentParty Workflow End-to-End Test")
        print("=" * 70)

        try:
            await self.test_health()
            await self.test_list_resources()
            await self.test_create_session()
            await self.test_get_budget()
            await self.test_get_available_jobs()
            await self.test_start_job()
            await self.test_get_current_task()
            await self.test_ask_agent()
            await self.test_submit_work()
            await self.test_request_review()
            await self.test_workflow_status()
            await self.test_final_budget()

            print("\n" + "=" * 70)
            print("✓ ALL TESTS PASSED!")
            print("=" * 70)

        except Exception as e:
            print(f"\n✗ TEST FAILED: {e}")
            import traceback

            traceback.print_exc()
            sys.exit(1)


async def main():
    """Main entry point."""
    tester = WorkflowTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
