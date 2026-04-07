"""
Draft/Post state machine views for Tasks.
Provides save-draft, post (assign to sprint), and auto-save endpoints.
"""
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from ..models import Task, Sprint


def validate_task_for_posting(task):
    """Validate that a task can be posted (assigned to sprint)."""
    errors = []
    
    if not task.title:
        errors.append("Task title is required.")
    
    if not task.sprint:
        errors.append("Task must be assigned to a sprint before posting.")
    
    if not task.assignee_id:
        errors.append("Task must have an assignee before posting.")
    
    if not task.estimated_hours or task.estimated_hours <= 0:
        errors.append("Estimated hours must be greater than zero.")
    
    return errors


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_task_draft(request):
    """
    Save a task as draft.
    Allows creating tasks not yet assigned to a sprint.
    """
    data = request.data
    task_id = data.get('id')
    
    try:
        with transaction.atomic():
            if task_id:
                # Update existing draft
                try:
                    task = Task.objects.get(id=task_id)
                except Task.DoesNotExist:
                    return JsonResponse(
                        {"error": "Task not found"},
                        status=404
                    )
                
                # Check if editable
                if task.status not in ['draft', 'backlog']:
                    return JsonResponse(
                        {"error": f"Cannot edit task in {task.status} status"},
                        status=403
                    )
                
                # Update fields
                if 'title' in data:
                    task.title = data['title']
                if 'description' in data:
                    task.description = data['description']
                if 'task_type' in data:
                    task.task_type = data['task_type']
                if 'priority' in data:
                    task.priority = data['priority']
                if 'estimated_hours' in data:
                    task.estimated_hours = data['estimated_hours']
                if 'story_points' in data:
                    task.story_points = data['story_points']
                
                if not task.drafted_at:
                    task.drafted_at = timezone.now()
                
                task.save()
            
            else:
                # Create new draft task
                task = Task.objects.create(
                    project_id=data['project_id'],
                    title=data.get('title', 'Untitled Task'),
                    description=data.get('description', ''),
                    task_type=data.get('task_type', 'task'),
                    priority=data.get('priority', 'medium'),
                    status='draft',
                    reporter_id=request.user.id,
                    estimated_hours=data.get('estimated_hours', 0),
                    story_points=data.get('story_points', 0),
                    drafted_at=timezone.now()
                )
            
            # Return task data
            return JsonResponse({
                "success": True,
                "message": "Task draft saved successfully",
                "data": {
                    "id": str(task.id),
                    "task_number": task.task_number,
                    "title": task.title,
                    "status": task.status,
                    "priority": task.priority,
                    "drafted_at": task.drafted_at.isoformat() if task.drafted_at else None
                }
            })
    
    except Exception as e:
        return JsonResponse(
            {"error": str(e)},
            status=500
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_task(request, task_id):
    """
    Post a task (assign to sprint and make active).
    Validates required fields and transitions to backlog/todo.
    """
    data = request.data
    
    try:
        with transaction.atomic():
            try:
                task = Task.objects.select_for_update().get(id=task_id)
            except Task.DoesNotExist:
                return JsonResponse(
                    {"error": "Task not found"},
                    status=404
                )
            
            # Check if already posted
            if task.status not in ['draft', 'backlog']:
                return JsonResponse(
                    {"error": "Task is already active"},
                    status=400
                )
            
            # Assign sprint if provided
            if 'sprint_id' in data:
                try:
                    sprint = Sprint.objects.get(id=data['sprint_id'])
                    task.sprint = sprint
                except Sprint.DoesNotExist:
                    return JsonResponse(
                        {"error": "Sprint not found"},
                        status=404
                    )
            
            # Assign to user if provided
            if 'assignee_id' in data:
                task.assignee_id = data['assignee_id']
            
            # Validate
            errors = validate_task_for_posting(task)
            if errors:
                return JsonResponse(
                    {"errors": errors},
                    status=400
                )
            
            # Update task
            task.status = 'todo'  # or 'backlog' if no sprint
            task.posted_at = timezone.now()
            task.posted_by = request.user.id
            task.save()
            
            return JsonResponse({
                "success": True,
                "message": "Task posted successfully",
                "data": {
                    "id": str(task.id),
                    "task_number": task.task_number,
                    "title": task.title,
                    "status": task.status,
                    "posted_at": task.posted_at.isoformat(),
                    "posted_by": str(task.posted_by)
                }
            })
    
    except Exception as e:
        return JsonResponse(
            {"error": str(e)},
            status=500
        )


@csrf_exempt
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def auto_save_task(request, task_id):
    """
    Auto-save task with minimal validation.
    Used for periodic saves while editing.
    """
    data = request.data
    
    try:
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return JsonResponse(
                {"error": "Task not found"},
                status=404
            )
        
        # Check if editable
        if task.status not in ['draft', 'backlog', 'todo']:
            return JsonResponse(
                {"error": "Cannot auto-save task in current status"},
                status=403
            )
        
        # Update simple fields
        if 'description' in data:
            task.description = data['description']
        if 'estimated_hours' in data:
            task.estimated_hours = data['estimated_hours']
        
        task.save()
        
        return JsonResponse({
            "success": True,
            "message": "Auto-save successful"
        })
    
    except Exception as e:
        return JsonResponse(
            {"error": str(e)},
            status=500
        )


@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_draft_tasks(request):
    """List all draft tasks for the current project."""
    project_id = request.GET.get('project_id')
    
    if not project_id:
        return JsonResponse(
            {"error": "project_id is required"},
            status=400
        )
    
    try:
        drafts = Task.objects.filter(
            project_id=project_id,
            status='draft'
        ).values(
            'id', 'task_number', 'title', 'priority', 'task_type',
            'estimated_hours', 'drafted_at', 'created_at'
        )
        
        return JsonResponse({
            "success": True,
            "data": list(drafts)
        })
    
    except Exception as e:
        return JsonResponse(
            {"error": str(e)},
            status=500
        )
