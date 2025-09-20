# Task Workflow System

This document explains the custom task workflow system implemented in SprintSync, which allows organizations to create their own task statuses and workflow transitions.

## Overview

The workflow system is designed to be:

- **Organization-specific**: Each organization can define its own statuses and workflows
- **Flexible**: Support any workflow (linear, branching, with loops)
- **Auditable**: Complete history of all status changes
- **User-friendly**: Rich status information for UI display

## Database Schema

### Core Tables

#### `task_statuses`

Stores organization-specific task statuses.

| Column            | Type    | Description                                      |
| ----------------- | ------- | ------------------------------------------------ |
| `id`              | Integer | Primary key                                      |
| `organization_id` | Integer | Foreign key to organizations table               |
| `name`            | String  | Internal status name (e.g., "in_progress")       |
| `display_name`    | String  | User-friendly name (e.g., "In Progress")         |
| `color`           | String  | Hex color code for UI display                    |
| `order_index`     | Integer | Sorting order for status display                 |
| `is_active`       | Boolean | Whether status is currently active               |
| `is_default`      | Boolean | Whether this is the default status for new tasks |

#### `task_workflow_transitions`

Defines allowed status transitions for each organization.

| Column            | Type    | Description                             |
| ----------------- | ------- | --------------------------------------- |
| `id`              | Integer | Primary key                             |
| `organization_id` | Integer | Foreign key to organizations table      |
| `from_status_id`  | Integer | Source status ID                        |
| `to_status_id`    | Integer | Target status ID                        |
| `is_active`       | Boolean | Whether transition is currently allowed |

#### `task_status_transitions`

Audit log of all task status changes.

| Column           | Type     | Description                               |
| ---------------- | -------- | ----------------------------------------- |
| `id`             | Integer  | Primary key                               |
| `task_id`        | Integer  | Foreign key to tasks table                |
| `from_status_id` | Integer  | Previous status (null for initial status) |
| `to_status_id`   | Integer  | New status                                |
| `changed_by`     | Integer  | User who made the change                  |
| `changed_at`     | DateTime | When the change occurred                  |
| `notes`          | String   | Optional notes about the change           |

#### Updated `tasks` table

The tasks table now references statuses by ID instead of string.

| Changed Column    | Type    | Description                        |
| ----------------- | ------- | ---------------------------------- |
| `status_id`       | Integer | Foreign key to task_statuses table |
| `organization_id` | Integer | Foreign key to organizations table |

## Example Workflows

### Simple Linear Workflow

```
New → In Progress → Done
```

### Agile Workflow

```
Backlog → In Progress → Code Review → QA → Done
    ↑         ↓            ↓         ↓
    └─────────┴────────────┴─────────┘
```

### Complex Branching Workflow

```
New → Analysis → Development → Testing → Staging → Production
 ↑       ↓           ↓          ↓         ↓         ↓
 └───────┴───────────┴──────────┴─────────┴─────────┘
```

## Usage Examples

### Setting Up an Organization Workflow

```python
# 1. Create statuses for your organization
statuses = [
    TaskStatusCreate(
        organization_id=1,
        name="new",
        display_name="New",
        color="#94A3B8",
        order_index=1,
        is_default=True
    ),
    TaskStatusCreate(
        organization_id=1,
        name="in_progress",
        display_name="In Progress",
        color="#3B82F6",
        order_index=2
    ),
    # ... more statuses
]

# 2. Define allowed transitions
transitions = [
    TaskWorkflowTransitionCreate(
        organization_id=1,
        from_status_id=1,  # New
        to_status_id=2     # In Progress
    ),
    # ... more transitions
]
```

### Moving a Task Through Workflow

```python
# Update task status
task_update = TaskStatusUpdateRequest(
    to_status_id=3,  # Moving to "Code Review"
    notes="Implementation completed, ready for review"
)

# This will:
# 1. Validate the transition is allowed
# 2. Update the task status
# 3. Create audit log entry
```

### Querying Workflow Data

```sql
-- Get all active statuses for an organization
SELECT * FROM task_statuses
WHERE organization_id = 1 AND is_active = true
ORDER BY order_index;

-- Get allowed transitions from current status
SELECT ts.* FROM task_workflow_transitions twt
JOIN task_statuses ts ON twt.to_status_id = ts.id
WHERE twt.organization_id = 1
  AND twt.from_status_id = 2  -- Current status
  AND twt.is_active = true;

-- Get task history
SELECT tst.*, u.first_name || ' ' || u.last_name as changed_by_name,
       fs.display_name as from_status, ts.display_name as to_status
FROM task_status_transitions tst
JOIN users u ON tst.changed_by = u.id
LEFT JOIN task_statuses fs ON tst.from_status_id = fs.id
JOIN task_statuses ts ON tst.to_status_id = ts.id
WHERE tst.task_id = 123
ORDER BY tst.changed_at;
```

## API Models

The system includes comprehensive Pydantic models for:

- `TaskStatusCreate/Update/Response` - Managing task statuses
- `TaskWorkflowTransitionCreate/Response` - Managing workflow transitions
- `TaskStatusTransitionCreate/Response` - Managing status changes
- `OrganizationWorkflowResponse` - Complete workflow view
- `WorkflowSetupRequest` - Bulk workflow setup

## Benefits

### For Organizations

- **Flexibility**: Define workflows that match your process
- **Scalability**: Support multiple organizations with different workflows
- **Control**: Manage which status transitions are allowed
- **Branding**: Custom colors and names for statuses

### For Users

- **Clarity**: Clear understanding of task status and next steps
- **History**: Complete audit trail of task progression
- **Validation**: Prevented from making invalid status transitions
- **Efficiency**: Quick access to allowed next statuses

### For Developers

- **Type Safety**: Strong typing with Pydantic models
- **Flexibility**: Easy to extend with new features
- **Performance**: Efficient database queries with proper indexes
- **Maintainability**: Clean separation of concerns

## Migration

The system includes an Alembic migration that:

1. Creates the new workflow tables
2. Adds organization_id and status_id to tasks
3. Removes the old string-based status column
4. Sets up proper foreign key constraints

Run the migration with:

```bash
alembic upgrade head
```

## Next Steps

To complete the implementation, you would typically:

1. **Run the migration** to create the database tables
2. **Create API endpoints** for managing workflows
3. **Add business logic** for status transition validation
4. **Update the UI** to use the new workflow system
5. **Create default workflows** for new organizations
6. **Add workflow analytics** and reporting features
