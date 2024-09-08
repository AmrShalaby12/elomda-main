from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, F

from .models import Size, Category, Topping, Price_List, Item_List, Cart_List, Extra, Order

def index(request):
    if not request.user.is_authenticated:
        return render(request, "orders/login.html", {"message": None})
    context = {
        "categories": Category.objects.exclude(name="Topping").all(),
        "items": Item_List.objects.all(),
        "toppings": Topping.objects.all(),
        "extras": Extra.objects.all(),
        "sizes": Size.objects.all(),
        "user": request.user
    }
    return render(request, "orders/index.html", context)

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "orders/login.html", {"message": "Invalid credentials."})
    return render(request, "orders/login.html")

def logout_view(request):
    logout(request)
    return render(request, "orders/login.html", {"message": "Logged out."})

def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "orders/signup.html", {"form": form})
    form = UserCreationForm()
    return render(request, "orders/signup.html", {"form": form})


from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from .models import Size, Category, Topping, Price_List, Item_List, Cart_List, Extra, Order

from django.http import Http404

def cart_view(request):
    if request.method == "POST":
        card_id = request.POST.get("card_id")
        item_id = request.POST.get("item_id")
        toppings = request.POST.getlist("topping_id")
        extras = request.POST.getlist("extra_id")
        size = request.POST.get("size_id")
        quantity = int(request.POST.get("quantity", 1))  # احصل على quantity من النموذج
        user = request.user

        # تحقق من وجود العنصر المحدد
        try:
            p = Item_List.objects.get(pk=item_id)
        except Item_List.DoesNotExist:
            messages.error(request, "The selected item does not exist.")
            return HttpResponseRedirect(reverse("index"))

        # إزالة الحسابات المتعلقة بالأسعار
        total_price = 0  # لا يوجد سعر، ولكن يمكن الاحتفاظ بهذا الحساب إذا كنت تحتاج حسابات أخرى

        # إضافة العنصر إلى العربة
        if size is None:
            new_item = Cart_List(user_id=user, item_id=p, size=None, calculated_price=total_price, quantity=quantity)
        else:
            new_item = Cart_List(user_id=user, item_id=p, size=Size.objects.get(pk=size), calculated_price=total_price, quantity=quantity)

        new_item.save()

        # إضافة التوابل والإضافات إلى العنصر
        for topping in toppings:
            new_item.toppings.add(topping)
        for extra in extras:
            new_item.extra.add(extra)
        
        messages.success(request, "Meal added to cart!")
        return HttpResponseRedirect(reverse("index") + f"#card-{card_id}")

    else:
        try:
            cart = Cart_List.objects.filter(user_id=request.user, is_current=True)
        except Cart_List.DoesNotExist:
            raise Http404("Cart does not exist")

        # إزالة حساب السعر الإجمالي
        total_price = 0  # ليس له أي قيمة إذا لم يكن هناك سعر

        cart_ordered = Cart_List.objects.filter(user_id=request.user, is_current=False)

        context = {
            "cart_items": cart,
            "total_price": total_price,
            "cart_items_ordered": cart_ordered,
        }

        return render(request, "orders/cart.html", context)

@login_required
def topping_view(request, cart_id):
    try:
        pizza = Cart_List.objects.get(pk=cart_id)
    except Cart_List.DoesNotExist:
        raise Http404("Pizza not in Cart or does not include topping")
    context = {
        "toppings": pizza.toppings.all()
    }
    return render(request, "orders/topping.html", context)
from django.shortcuts import get_object_or_404

@login_required

def order_view(request):
    if request.method == "POST":
        user = request.user
        items = request.POST.getlist("cart_id")

        if not items:
            messages.error(request, "No items selected in the cart.")
            return HttpResponseRedirect(reverse("cart_view"))

        new_order = Order(user_id=user)
        new_order.save()

        for item_id in items:
            # تحقق من وجود العنصر في العربة
            cart_item = get_object_or_404(Cart_List, pk=item_id, user_id=user)
            new_order.cart_id.add(cart_item)

        # تحديث حالة العناصر في العربة
        Cart_List.objects.filter(user_id=user, is_current=True).update(is_current=False)

        messages.success(request, "Thank you for shopping with us, your order has been placed.")
        return HttpResponseRedirect(reverse("index"))
    
    return HttpResponseRedirect(reverse("index"))

@login_required
def removefromcart_view(request, cart_id):
    item_toremove = Cart_List.objects.get(pk=cart_id)
    item_toremove.delete()
    messages.info(request, "This item has been removed from your cart.")
    return HttpResponseRedirect(reverse("cart"))

@login_required
def cart_count(request):
    cart = Cart_List.objects.filter(user_id=request.user, is_current=True)
    count = cart.count()
    return JsonResponse({'count': count})

def add_to_cart(request):
    if request.method == "POST":
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        cart = get_cart(request)
        item = Item.objects.get(id=item_id)

        cart.add(item, quantity)
        return redirect('cart')
    
    
from .models import Size, Category, Topping, Price_List, Item_List, Cart_List, Extra, Order, ImageSlider  # Import ImageSlider

def index(request):
    if not request.user.is_authenticated:
        return render(request, "orders/login.html", {"message": None})
    context = {
        "categories": Category.objects.exclude(name="Topping").all(),
        "items": Item_List.objects.all(),
        "toppings": Topping.objects.all(),
        "extras": Extra.objects.all(),
        "sizes": Size.objects.all(),
        "user": request.user,
        "sliders": ImageSlider.objects.all(),  # Add this line
    }
    return render(request, "orders/index.html", context)
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Feedback  # تأكد من استيراد نموذج Feedback

def submit_feedback(request):
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comments = request.POST.get('comments')
        feedback = Feedback(user=request.user, rating=rating, comments=comments)
        feedback.save()
        messages.success(request, 'تم إرسال الشكاوي والاقتراحات بنجاح.')
        return redirect('index')
    return redirect('index')

# views.py

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt  # Use this decorator to allow POST requests from the frontend
def process_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            token = data.get('token')

            # Create a charge: this will charge the user's card
            charge = stripe.Charge.create(
                amount=2000,  # Amount in cents (e.g., $20.00)
                currency="usd",
                source=token,
                description="Charge for service"
            )

            return JsonResponse({'status': 'success', 'charge': charge})

        except stripe.error.CardError as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


import base64
from io import BytesIO
from PIL import Image
import numpy as np
import cv2
from pyzbar import pyzbar
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Item_List

def scan_qr(request):
    if request.method == 'POST':
        image_data = request.POST.get('image', None)
        if image_data:
            # فك ترميز الصورة base64
            image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
            image_np = np.array(image)

            # تحويل الصورة إلى RGB لاستخدام OpenCV
            gray_image = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
            decoded_qrs = pyzbar.decode(gray_image)

            if decoded_qrs:
                # استخراج البيانات من QR
                qr_data = decoded_qrs[0].data.decode('utf-8')
                # استخدم البيانات لإيجاد الكائن المناسب من قاعدة البيانات
                item_id = qr_data.split(',')[0].split(':')[-1].strip()
                item = get_object_or_404(Item_List, id=item_id)

                # إرجاع البيانات إلى الواجهة
                response_data = {
                    'id': item.id,
                    'name': item.name,
                    'category': item.category.name,
                    'subscription_start_date': item.subscription_start_date,
                    'subscription_end_date': item.subscription_end_date,
                    'image_url': item.image.url if item.image else None  # Adding image URL

                }
                return JsonResponse(response_data)
            else:
                return JsonResponse({'error': 'QR code not recognized'})
    elif request.method == 'GET':
        # عرض صفحة HTML مع الكاميرا
        return render(request, 'scan_qr.html')

    return JsonResponse({'error': 'Invalid request'})


from django.contrib import messages
from django.shortcuts import render
from .models import Attendance
from datetime import date
import json

from datetime import date
from django.contrib import messages
from django.shortcuts import render
import json
from .models import Attendance

from datetime import date
from django.contrib import messages
from django.shortcuts import render
import json
from .models import Attendance

def attendance_view(request):
    if request.method == 'POST':
        attendance_data = request.POST.get('attendance_data', None)
        attendance_status = request.POST.get('attendance_status', None)
        
        if attendance_data:
            try:
                data = json.loads(attendance_data)
                
                # البحث عن تسجيلات الطالب في اليوم الحالي
                existing_record = Attendance.objects.filter(
                    user_id=data['id'], 
                    attendance_date=date.today()
                ).first()
                
                if existing_record:
                    # إذا كان هناك سجل، تحقق إذا كان الحضور أو الانصراف تم تسجيله مسبقًا
                    if attendance_status == 'حضور':
                        if existing_record.attendance_status == 'حضور':
                            messages.error(request, f"{data['name']} has already been marked as present today!")
                        else:
                            existing_record.attendance_status = 'حضور'
                            existing_record.save()
                            messages.success(request, f"{data['name']} marked as present successfully!")
                    
                    elif attendance_status == 'انصراف':
                        if existing_record.departure_status == 'انصراف':
                            messages.error(request, f"{data['name']} has already been marked as departed today!")
                        else:
                            existing_record.departure_status = 'انصراف'
                            existing_record.save()
                            messages.success(request, f"{data['name']} marked as departed successfully!")
                
                else:
                    # إذا لم يكن هناك سجل، قم بإنشاء سجل جديد
                    Attendance.objects.create(
                        user_id=data['id'],
                        name=data['name'],
                        category=data['category'],
                        subscription_start_date=data['subscription_start_date'],
                        subscription_end_date=data['subscription_end_date'],
                        attendance_status='حضور' if attendance_status == 'حضور' else 'غياب',
                        departure_status='انصراف' if attendance_status == 'انصراف' else 'غياب',
                        attendance_date=date.today()
                    )
                    messages.success(request, f"{data['name']} Attendance ({attendance_status}) recorded successfully!")

            except Exception as e:
                messages.error(request, f"Error: {e}")
    
    return render(request, 'scan_qr.html')


from datetime import date, timedelta
from django.utils import timezone
from .models import Attendance, Item_List

def attendance_reset_view(request):
    # الحصول على تاريخ اليوم
    today = timezone.now().date()
    
    # التحقق من آخر تاريخ تم تحديث فيه الحضور
    last_recorded_date = Attendance.objects.latest('attendance_date').attendance_date if Attendance.objects.exists() else None
    
    # إذا لم يكن هناك بيانات لليوم أو كان التاريخ قد تغير
    if not last_recorded_date or last_recorded_date < today:
        # مسح حالة الطلاب وإضافة سجلات غياب جديدة
        for item in Item_List.objects.all():
            Attendance.objects.create(
                user_id=item.id,
                name=item.name,
                category=item.category.name,
                subscription_start_date=item.subscription_start_date,
                subscription_end_date=item.subscription_end_date,
                attendance_status='غياب',  # تعيين حالة غياب للحضور
                attendance_date=today
            )

    # الآن يمكنك إظهار السجلات أو الانتقال لجزء آخر من الكود كما تريد
    return render(request, 'attendance_page.html', {'attendance_list': Attendance.objects.filter(attendance_date=today)})
