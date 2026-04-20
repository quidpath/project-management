"""
Product/Material Views for Projects
Queries inventory service for product information
"""
import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from projects_service.services.inventory_client import InventoryClient

logger = logging.getLogger(__name__)


@api_view(['GET'])
def search_materials(request):
    """
    Search materials/products from inventory
    
    GET /api/projects/materials/search/?q=query
    """
    try:
        query = request.GET.get('q', '').strip()
        if not query:
            return Response({'error': 'Query parameter "q" is required'}, status=400)
        
        inventory = InventoryClient()
        products = inventory.search_products(query, request.corporate_id)
        
        return Response({
            'count': len(products),
            'materials': products
        })
        
    except Exception as e:
        logger.error(f"Error searching materials: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
def get_material(request, product_id):
    """
    Get single material/product from inventory
    
    GET /api/projects/materials/{product_id}/
    """
    try:
        inventory = InventoryClient()
        product = inventory.get_product(product_id, request.corporate_id)
        
        if not product:
            return Response({'error': 'Material not found'}, status=404)
        
        return Response(product)
        
    except Exception as e:
        logger.error(f"Error getting material: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
def list_materials(request):
    """
    List all materials/products
    
    GET /api/projects/materials/
    """
    try:
        inventory = InventoryClient()
        products = inventory.list_products_for_sale(request.corporate_id)
        
        return Response({
            'count': len(products),
            'materials': products
        })
        
    except Exception as e:
        logger.error(f"Error listing materials: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def get_materials_bulk(request):
    """
    Get multiple materials at once
    
    POST /api/projects/materials/bulk/
    Body: {"product_ids": ["uuid1", "uuid2"]}
    """
    try:
        product_ids = request.data.get('product_ids', [])
        if not product_ids:
            return Response({'error': 'product_ids is required'}, status=400)
        
        inventory = InventoryClient()
        products = inventory.get_products_bulk(product_ids, request.corporate_id)
        
        return Response({
            'count': len(products),
            'materials': products
        })
        
    except Exception as e:
        logger.error(f"Error getting materials bulk: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
def check_material_stock(request, product_id):
    """
    Check stock level for a material
    
    GET /api/projects/materials/{product_id}/stock/
    """
    try:
        inventory = InventoryClient()
        stock = inventory.get_stock_level(product_id, request.corporate_id)
        
        if not stock:
            return Response({'error': 'Stock information not available'}, status=404)
        
        return Response(stock)
        
    except Exception as e:
        logger.error(f"Error checking stock: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=500)
