from django.shortcuts import render, redirect
from django.http import Http404, JsonResponse
from .models import Product, Category, Order
from django.core.exceptions import ObjectDoesNotExist
from .forms import FeedbackForm
from django.conf import settings
from django.core.mail import send_mail

# pdf generation
from io import BytesIO
from django.template.loader import get_template
from django.http import HttpResponse
from datetime import datetime
from xhtml2pdf import pisa


def index(request):
    data = dict()

    filtered_categories = request.GET.getlist('category')
    filtered_categories = list(map(int, filtered_categories))
    all_orders = Order.objects.filter(customer=request.user)
    all_categories = Category.objects.all()
    if filtered_categories:
        all_products = Product.objects.filter(category__id__in=filtered_categories)
    else:
        all_products = Product.objects.all()
    print(filtered_categories)

    data['products'] = all_products
    data['categories'] = all_categories
    data['orders'] = all_orders
    return render(request, 'mainsite/index.html', context=data)


def details(request, slug):
    try:
        product = Product.objects.get(slug=slug)
        data = dict()
        data['product'] = product
        return render(request, 'mainsite/single-product.html', context=data)
    except ObjectDoesNotExist:
        raise Http404


def feedback(request):
    data = {}
    form = FeedbackForm(request.POST or None)
    if form.is_valid():
        form_email = form.cleaned_data.get('email')
        form_text = form.cleaned_data.get('text')
        header = 'Website feedback'
        email_admin = settings.DEFAULT_TO_EMAIL

        text = f"""
        {form_email} 
        
        Message:
            {form_text}
        """
        html_file = get_template('mainsite/mail.html')

        data['form_text'] = form_text
        data['form_email'] = form_email
        html_content = html_file.render(context=data)

        send_mail(header, text, email_admin,  [email_admin, 'rudyk.iurii@gmail.com'], fail_silently=False, html_message=html_content)
    data['form'] = form
    return render(request, 'mainsite/feedback.html', context=data)


def add_to_card(request, slug):
    if not request.user.is_authenticated:
        return redirect('/')

    try:
        product = Product.objects.get(slug=slug)
        new_order = Order(customer=request.user, product=product, count=0)
        my_orders_with_products = Order.objects.filter(customer=request.user, product=product)
        if my_orders_with_products.exists():
            new_order = my_orders_with_products.first()
        new_order.count += 1
        new_order.save()
        return redirect('home_page')
    except ObjectDoesNotExist:
        raise Http404

def delete_from_card(request, slug):
    result = {}
    result['status'] = 'error'

    if not request.user.is_authenticated:
        return JsonResponse(result)

    try:
        product = Product.objects.get(slug=slug)
        order = Order.objects.get(customer=request.user, product=product)
        order.delete()
        result['status'] = 'ok'
        return JsonResponse(result)
    except ObjectDoesNotExist:
        return JsonResponse(result)


def change_order_count(request, order_id):
    result = {}
    result['status'] = 'error'
    if Order.objects.filter(id=order_id, customer=request.user).exists():
        order = Order.objects.get(id=order_id, customer=request.user)
        action = request.GET.get('action')
        current_order_number = order.count
        if action == 'increase':
            current_order_number += 1
        elif action == 'decrease' and current_order_number > 1:
            current_order_number -= 1

        order.count = current_order_number
        order.save()

        result['status'] = 'ok'
        result['new_number'] = current_order_number
    return JsonResponse(result)

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


def get_pdf(request):
    orders = Order.objects.filter(customer=request.user)
    total_price = 0
    for order in orders:
        total_price += order.count * order.product.price

    context = {
        'orders': orders,
        'total_price': total_price
    }

    pdf = render_to_pdf('mainsite/invoice.html', context_dict=context)
    return HttpResponse(pdf, content_type='application/pdf')
