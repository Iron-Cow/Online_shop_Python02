from django.shortcuts import render
from django.http import Http404
from .models import Product, Category
from django.core.exceptions import ObjectDoesNotExist


def index(request):
    data = dict()

    filtered_categories = request.GET.getlist('category')
    filtered_categories = list(map(int, filtered_categories))
    all_categories = Category.objects.all()
    if filtered_categories:
        all_products = Product.objects.filter(category__id__in=filtered_categories)
    else:
        all_products = Product.objects.all()
    print(filtered_categories)

    data['products'] = all_products
    data['categories'] = all_categories
    return render(request, 'mainsite/index.html', context=data)


def details(request, slug):
    try:
        product = Product.objects.get(slug=slug)
        data = dict()
        data['product'] = product
        return render(request, 'mainsite/single-product.html', context=data)
    except ObjectDoesNotExist:
        raise Http404

