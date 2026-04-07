"""
Draft/Post state machine views for Issues.
Provides save-draft, post (open issue), and auto-save endpoints.
"""
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from ..models import Issue


def validate_issue_for_posting(issue):
    """Validate that an issue can be posted (opened)."""
    errors = []
    
    if not issue.title:
        errors.append("Issue title is required.")
    
    if not issue.description:
        errors.append("Issue description is required.")
    
    if not issue.severity:
        errors.append("Issue severity is required.")
    
    return errors


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_issue_draft(request):
    """
    Save an issue as draft.
    Allows creating issues before they're ready to be opened.
    """
    data = request.data
    issue_id = data.get('id')
    
    try:
        with transaction.atomic():
            if issue_id:
                # Update existing draft
                try:
                    issue = Issue.objects.get(id=issue_id)
                except Issue.DoesNotExist:
                    return JsonResponse(
                        {"error": "Issue not found"},
                        status=404
                    )
                
                # Check if editable
                if issue.status not in ['draft', 'open']:
                    return JsonResponse(
                        {"error": f"Cannot edit issue in {issue.status} status"},
                        status=403
                    )
                
                # Update fields
                if 'title' in data:
                    issue.title = data['title']
                if 'description' in data:
                    issue.description = data['description']
                if 'severity' in data:
                    issue.severity = data['severity']
                if 'steps_to_reproduce' in data:
                    issue.steps_to_reproduce = data['steps_to_reproduce']
                if 'expected_result' in data:
                    issue.expected_result = data['expected_result']
                if 'actual_result' in data:
                    issue.actual_result = data['actual_result']
                if 'environment' in data:
                    issue.environment = data['environment']
                if 'version' in data:
                    issue.version = data['version']
                
                if not issue.drafted_at:
                    issue.drafted_at = timezone.now()
                
                issue.save()
            
            else:
                # Create new draft issue
                issue = Issue.objects.create(
                    project_id=data['project_id'],
                    title=data.get('title', 'Untitled Issue'),
                    description=data.get('description', ''),
                    severity=data.get('severity', 'major'),
                    status='draft',
                    reporter_id=request.user.id,
                    steps_to_reproduce=data.get('steps_to_reproduce', ''),
                    expected_result=data.get('expected_result', ''),
                    actual_result=data.get('actual_result', ''),
                    environment=data.get('environment', ''),
                    version=data.get('version', ''),
                    drafted_at=timezone.now()
                )
            
            # Return issue data
            return JsonResponse({
                "success": True,
                "message": "Issue draft saved successfully",
                "data": {
                    "id": str(issue.id),
                    "issue_number": issue.issue_number,
                    "title": issue.title,
                    "status": issue.status,
                    "severity": issue.severity,
                    "drafted_at": issue.drafted_at.isoformat() if issue.drafted_at else None
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
def post_issue(request, issue_id):
    """
    Post an issue (open it for tracking).
    Validates required fields and transitions to open status.
    """
    data = request.data
    
    try:
        with transaction.atomic():
            try:
                issue = Issue.objects.select_for_update().get(id=issue_id)
            except Issue.DoesNotExist:
                return JsonResponse(
                    {"error": "Issue not found"},
                    status=404
                )
            
            # Check if already posted
            if issue.status != 'draft':
                return JsonResponse(
                    {"error": "Issue is already opened"},
                    status=400
                )
            
            # Assign to user if provided
            if 'assignee_id' in data:
                issue.assignee_id = data['assignee_id']
            
            # Validate
            errors = validate_issue_for_posting(issue)
            if errors:
                return JsonResponse(
                    {"errors": errors},
                    status=400
                )
            
            # Update issue
            issue.status = 'open'
            issue.posted_at = timezone.now()
            issue.posted_by = request.user.id
            issue.save()
            
            return JsonResponse({
                "success": True,
                "message": "Issue opened successfully",
                "data": {
                    "id": str(issue.id),
                    "issue_number": issue.issue_number,
                    "title": issue.title,
                    "status": issue.status,
                    "posted_at": issue.posted_at.isoformat(),
                    "posted_by": str(issue.posted_by)
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
def auto_save_issue(request, issue_id):
    """
    Auto-save issue with minimal validation.
    Used for periodic saves while editing.
    """
    data = request.data
    
    try:
        try:
            issue = Issue.objects.get(id=issue_id)
        except Issue.DoesNotExist:
            return JsonResponse(
                {"error": "Issue not found"},
                status=404
            )
        
        # Check if editable
        if issue.status not in ['draft', 'open']:
            return JsonResponse(
                {"error": "Cannot auto-save closed issue"},
                status=403
            )
        
        # Update simple fields
        if 'description' in data:
            issue.description = data['description']
        if 'steps_to_reproduce' in data:
            issue.steps_to_reproduce = data['steps_to_reproduce']
        
        issue.save()
        
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
def list_draft_issues(request):
    """List all draft issues for the current project."""
    project_id = request.GET.get('project_id')
    
    if not project_id:
        return JsonResponse(
            {"error": "project_id is required"},
            status=400
        )
    
    try:
        drafts = Issue.objects.filter(
            project_id=project_id,
            status='draft'
        ).values(
            'id', 'issue_number', 'title', 'severity', 'reporter_id',
            'drafted_at', 'created_at'
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
