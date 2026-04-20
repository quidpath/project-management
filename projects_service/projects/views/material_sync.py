"""
Project Materials Sync Views
Handles material synchronization from Inventory Service
"""
import logging
from decimal import Decimal
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime

from projects_service.projects.models.material import ProjectMaterial, MaterialUsage

logger = logging.getLogger(__name__)


@api_view(['POST'])
def create_material(request):
    """
    Create a new material from inventory sync
    
    POST /api/projects/materials/
    
    Expected payload:
    {
        "product_id": "uuid",
        "name": "Material Name",
        "description": "Description",
        "unit_cost": "50.00",
        "uom": "kg"
    }
    """
    try:
        data = request.data
        corporate_id = request.corporate_id
        
        # Validate required fields
        if not data.get('product_id'):
            return Response(
                {'error': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not data.get('name'):
            return Response(
                {'error': 'name is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if material already exists
        if ProjectMaterial.objects.filter(
            product_id=data['product_id'],
            corporate_id=corporate_id
        ).exists():
            return Response(
                {'error': 'Material already exists'},
                status=status.HTTP_409_CONFLICT
            )
        
        # Create material
        material = ProjectMaterial.objects.create(
            product_id=data['product_id'],
            name=data['name'],
            description=data.get('description', ''),
            unit_cost=Decimal(str(data.get('unit_cost', '0.00'))),
            uom=data.get('uom', 'Unit'),
            corporate_id=corporate_id,
            synced_from_inventory=True
        )
        
        logger.info(f"Created project material {material.id} from inventory sync")
        
        return Response({
            'id': material.id,
            'product_id': str(material.product_id),
            'name': material.name,
            'message': 'Material created successfully'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error creating project material: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Failed to create material: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PATCH'])
def update_material(request, product_id):
    """
    Update an existing material from inventory sync
    
    PATCH /api/projects/materials/{product_id}/
    
    Expected payload:
    {
        "name": "Updated Material Name",
        "unit_cost": "55.00"
    }
    """
    try:
        corporate_id = request.corporate_id
        
        # Get material
        material = get_object_or_404(
            ProjectMaterial,
            product_id=product_id,
            corporate_id=corporate_id
        )
        
        data = request.data
        
        # Update fields if provided
        if 'name' in data:
            material.name = data['name']
        if 'description' in data:
            material.description = data['description']
        if 'unit_cost' in data:
            material.unit_cost = Decimal(str(data['unit_cost']))
        if 'uom' in data:
            material.uom = data['uom']
        if 'is_active' in data:
            material.is_active = data['is_active']
        
        material.save()
        
        logger.info(f"Updated project material {material.id} from inventory sync")
        
        return Response({
            'id': material.id,
            'product_id': str(material.product_id),
            'name': material.name,
            'message': 'Material updated successfully'
        }, status=status.HTTP_200_OK)
        
    except ProjectMaterial.DoesNotExist:
        return Response(
            {'error': 'Material not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error updating project material: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Failed to update material: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
def delete_material(request, product_id):
    """
    Delete a material (soft delete - mark as inactive)
    
    DELETE /api/projects/materials/{product_id}/
    """
    try:
        corporate_id = request.corporate_id
        
        # Get material
        material = get_object_or_404(
            ProjectMaterial,
            product_id=product_id,
            corporate_id=corporate_id
        )
        
        # Soft delete - mark as inactive
        material.is_active = False
        material.save(update_fields=['is_active', 'updated_at'])
        
        logger.info(f"Deleted (deactivated) project material {material.id}")
        
        return Response({
            'message': 'Material deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except ProjectMaterial.DoesNotExist:
        return Response(
            {'error': 'Material not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error deleting project material: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Failed to delete material: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def record_material_usage(request):
    """
    Record material usage in a project
    
    POST /api/projects/materials/usage/
    
    Expected payload:
    {
        "project_id": 123,
        "product_id": "uuid",
        "quantity_used": "10.00",
        "unit_cost": "50.00",
        "date_used": "2024-01-15T10:30:00Z",
        "notes": "Used for foundation work"
    }
    """
    try:
        data = request.data
        corporate_id = request.corporate_id
        user_id = request.user_id
        
        # Validate required fields
        if not data.get('project_id'):
            return Response(
                {'error': 'project_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not data.get('product_id'):
            return Response(
                {'error': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not data.get('quantity_used'):
            return Response(
                {'error': 'quantity_used is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get material
        material = get_object_or_404(
            ProjectMaterial,
            product_id=data['product_id'],
            corporate_id=corporate_id
        )
        
        # Parse date
        date_used = data.get('date_used')
        if date_used:
            date_used = parse_datetime(date_used)
        if not date_used:
            date_used = datetime.now()
        
        # Create usage record
        usage = MaterialUsage.objects.create(
            project_id=data['project_id'],
            material=material,
            quantity_used=Decimal(str(data['quantity_used'])),
            unit_cost=Decimal(str(data.get('unit_cost', material.unit_cost))),
            date_used=date_used,
            recorded_by=user_id,
            notes=data.get('notes', ''),
            corporate_id=corporate_id
        )
        
        logger.info(
            f"Recorded material usage {usage.id}: "
            f"{usage.quantity_used} {material.uom} of {material.name} "
            f"for project {data['project_id']}"
        )
        
        return Response({
            'id': usage.id,
            'material_name': material.name,
            'quantity_used': str(usage.quantity_used),
            'total_cost': str(usage.total_cost),
            'message': 'Material usage recorded successfully'
        }, status=status.HTTP_201_CREATED)
        
    except ProjectMaterial.DoesNotExist:
        return Response(
            {'error': 'Material not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error recording material usage: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Failed to record material usage: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def list_materials(request):
    """
    List all materials
    
    GET /api/projects/materials/
    """
    try:
        corporate_id = request.corporate_id
        
        materials = ProjectMaterial.objects.filter(
            corporate_id=corporate_id,
            is_active=True
        ).order_by('name')
        
        data = [{
            'id': m.id,
            'product_id': str(m.product_id),
            'name': m.name,
            'description': m.description,
            'unit_cost': str(m.unit_cost),
            'uom': m.uom,
            'is_active': m.is_active,
        } for m in materials]
        
        return Response({
            'count': len(data),
            'materials': data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error listing materials: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Failed to list materials: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
