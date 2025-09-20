"""
Example script showing how to use the new task workflow system.

This demonstrates how organizations can create custom status workflows
and how tasks can transition through these statuses.
"""

from app.db.entities import (
    Organization, TaskStatus, TaskWorkflowTransition, 
    Task, TaskStatusTransition
)
from app.models.workflow import (
    TaskStatusCreate, TaskWorkflowTransitionCreate,
    OrganizationCreate
)

def setup_example_workflow():
    """
    Example of how to set up a custom workflow for an organization.
    
    This creates the workflow: New -> In Progress -> Done -> QA -> Done
    """
    
    # 1. Create an organization
    org_data = OrganizationCreate(
        name="Acme Software",
        description="Software development company"
    )
    
    # 2. Define custom statuses for this organization
    statuses = [
        TaskStatusCreate(
            organization_id=1,  # Assuming org ID 1
            name="new",
            display_name="New",
            color="#94A3B8",  # Gray
            order_index=1,
            is_default=True  # Default status for new tasks
        ),
        TaskStatusCreate(
            organization_id=1,
            name="in_progress",
            display_name="In Progress",
            color="#3B82F6",  # Blue
            order_index=2
        ),
        TaskStatusCreate(
            organization_id=1,
            name="code_review",
            display_name="Code Review",
            color="#F59E0B",  # Yellow
            order_index=3
        ),
        TaskStatusCreate(
            organization_id=1,
            name="qa_testing",
            display_name="QA Testing",
            color="#8B5CF6",  # Purple
            order_index=4
        ),
        TaskStatusCreate(
            organization_id=1,
            name="done",
            display_name="Done",
            color="#10B981",  # Green
            order_index=5
        )
    ]
    
    # 3. Define allowed workflow transitions
    transitions = [
        # From New
        TaskWorkflowTransitionCreate(
            organization_id=1,
            from_status_id=1,  # New
            to_status_id=2     # In Progress
        ),
        
        # From In Progress
        TaskWorkflowTransitionCreate(
            organization_id=1,
            from_status_id=2,  # In Progress
            to_status_id=3     # Code Review
        ),
        TaskWorkflowTransitionCreate(
            organization_id=1,
            from_status_id=2,  # In Progress
            to_status_id=1     # Back to New (if needed)
        ),
        
        # From Code Review
        TaskWorkflowTransitionCreate(
            organization_id=1,
            from_status_id=3,  # Code Review
            to_status_id=4     # QA Testing
        ),
        TaskWorkflowTransitionCreate(
            organization_id=1,
            from_status_id=3,  # Code Review
            to_status_id=2     # Back to In Progress
        ),
        
        # From QA Testing
        TaskWorkflowTransitionCreate(
            organization_id=1,
            from_status_id=4,  # QA Testing
            to_status_id=5     # Done
        ),
        TaskWorkflowTransitionCreate(
            organization_id=1,
            from_status_id=4,  # QA Testing
            to_status_id=2     # Back to In Progress
        ),
        
        # From Done (allow reopening if needed)
        TaskWorkflowTransitionCreate(
            organization_id=1,
            from_status_id=5,  # Done
            to_status_id=2     # In Progress
        )
    ]
    
    return {
        "organization": org_data,
        "statuses": statuses,
        "transitions": transitions
    }


def example_task_workflow():
    """
    Example of how a task would flow through the workflow system.
    """
    
    # 1. Create a task (automatically gets default status "New")
    task_data = {
        "title": "Implement user authentication",
        "description": "Add JWT-based authentication system",
        "organization_id": 1,
        "created_by": 42,
        "assigned_to": 43,
        "priority": "high",
        "status_id": 1  # New (default status)
    }
    
    # 2. Simulate task status transitions with audit trail
    transitions = [
        # Developer starts working
        {
            "from_status_id": 1,  # New
            "to_status_id": 2,    # In Progress
            "changed_by": 43,     # Assigned developer
            "notes": "Started working on authentication implementation"
        },
        
        # Code is ready for review
        {
            "from_status_id": 2,  # In Progress
            "to_status_id": 3,    # Code Review
            "changed_by": 43,     # Developer
            "notes": "Implementation complete, ready for code review"
        },
        
        # Code review passed, moving to QA
        {
            "from_status_id": 3,  # Code Review
            "to_status_id": 4,    # QA Testing
            "changed_by": 44,     # Code reviewer
            "notes": "Code review passed, approved for QA testing"
        },
        
        # QA found issues, back to development
        {
            "from_status_id": 4,  # QA Testing
            "to_status_id": 2,    # In Progress
            "changed_by": 45,     # QA tester
            "notes": "Found authentication bypass vulnerability, needs fixing"
        },
        
        # Developer fixes issues
        {
            "from_status_id": 2,  # In Progress
            "to_status_id": 3,    # Code Review
            "changed_by": 43,     # Developer
            "notes": "Fixed security vulnerability, ready for re-review"
        },
        
        # Re-review passed, back to QA
        {
            "from_status_id": 3,  # Code Review
            "to_status_id": 4,    # QA Testing
            "changed_by": 44,     # Code reviewer
            "notes": "Security fix verified, approved for QA re-testing"
        },
        
        # QA passes, task complete
        {
            "from_status_id": 4,  # QA Testing
            "to_status_id": 5,    # Done
            "changed_by": 45,     # QA tester
            "notes": "All tests passed, authentication system working correctly"
        }
    ]
    
    return {
        "task": task_data,
        "transitions": transitions
    }


def query_examples():
    """
    Example queries to demonstrate how to use the workflow system.
    """
    
    queries = {
        "get_organization_statuses": """
        SELECT ts.* FROM task_statuses ts
        WHERE ts.organization_id = :org_id
        AND ts.is_active = true
        ORDER BY ts.order_index;
        """,
        
        "get_allowed_transitions": """
        SELECT twt.*, 
               fs.display_name as from_status_name,
               ts.display_name as to_status_name
        FROM task_workflow_transitions twt
        JOIN task_statuses fs ON twt.from_status_id = fs.id
        JOIN task_statuses ts ON twt.to_status_id = ts.id
        WHERE twt.organization_id = :org_id
        AND twt.is_active = true;
        """,
        
        "get_task_history": """
        SELECT tst.*, 
               u.first_name || ' ' || u.last_name as changed_by_name,
               fs.display_name as from_status_name,
               ts.display_name as to_status_name
        FROM task_status_transitions tst
        JOIN users u ON tst.changed_by = u.id
        LEFT JOIN task_statuses fs ON tst.from_status_id = fs.id
        JOIN task_statuses ts ON tst.to_status_id = ts.id
        WHERE tst.task_id = :task_id
        ORDER BY tst.changed_at;
        """,
        
        "get_tasks_by_status": """
        SELECT t.*, ts.display_name as status_name, ts.color as status_color
        FROM tasks t
        JOIN task_statuses ts ON t.status_id = ts.id
        WHERE t.organization_id = :org_id
        AND ts.name = :status_name;
        """
    }
    
    return queries


if __name__ == "__main__":
    print("=== Task Workflow System Example ===")
    print()
    
    print("1. Setting up custom workflow...")
    workflow = setup_example_workflow()
    print(f"Created workflow with {len(workflow['statuses'])} statuses and {len(workflow['transitions'])} transitions")
    print()
    
    print("2. Example task lifecycle...")
    task_example = example_task_workflow()
    print(f"Task will go through {len(task_example['transitions'])} status transitions")
    print()
    
    print("3. Available SQL queries for workflow operations:")
    queries = query_examples()
    for name, query in queries.items():
        print(f"  - {name}")
    print()
    
    print("This workflow system supports:")
    print("  ✓ Organization-specific custom statuses")
    print("  ✓ Configurable workflow transitions") 
    print("  ✓ Status validation (only allowed transitions)")
    print("  ✓ Complete audit trail of status changes")
    print("  ✓ Flexible status properties (colors, ordering, etc.)")
    print("  ✓ Default status assignment for new tasks")