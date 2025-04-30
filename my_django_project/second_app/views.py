from django.shortcuts import render
import json 
from django.http import JsonResponse 
from django.views.decorators.csrf import csrf_exempt
from .models import Product
from django.core.paginator import Paginator


def test_json_view(request): 
    data = { 
        'name': 'John Doe', 
        'age': 30, 
        'location': 'New York', 
        'is_active': True, 
    } 
    return JsonResponse(data)

@csrf_exempt
def post_json_view(request):
    if request.method == 'POST':
        if not request.body:
            return JsonResponse({'error': 'No data provided'}, status=400)
        try:
            data = json.loads(request.body)
            user_name = data.get('user', 'Unknown')
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        response_data = {
            'name': 'Alice',
            'age': 30,
            'location': 'New York',
            'is_active': True,
        }
        return JsonResponse(response_data)
    else:
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    

def get_all_products(request):
    if request.method == 'GET':
        products = Product.objects.all().values()
        return JsonResponse(list(products), safe=False)

def get_most_expensive_product(request):
    if request.method == 'GET':
        product = Product.objects.order_by('-price').first()
        if product:
            return JsonResponse({'name': product.name, 'price': str(product.price)})
        return JsonResponse({'error': 'No products found'}, status=404)

@csrf_exempt
def add_product(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        new_product = Product(
            name=body['name'],
            price=body['price'],
            description=body.get('description', '')
        )
        new_product.save()
        return JsonResponse({'message': 'Product added successfully!'})
    

@csrf_exempt
def update_product(request, product_id):
    if request.method == 'PUT':
        body = json.loads(request.body)
        try:
            product = Product.objects.get(id=product_id)
            product.name = body.get('name', product.name)
            product.price = body.get('price', product.price)
            product.description = body.get('description', product.description)
            product.save()
            return JsonResponse({'message': 'Product updated successfully!'})
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)


def get_paginated_products(request):
    page_number = request.GET.get('page', 1)
    products = Product.objects.all()
    paginator = Paginator(products, 3)

    try:
        page_obj = paginator.get_page(page_number)

        products_list = [{
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'description': product.description,
            'created_at': product.created_at,
            'updated_at': product.updated_at,
        } for product in page_obj]

        return JsonResponse({'products': products_list, 'num_pages': paginator.num_pages}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)