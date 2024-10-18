from collections import Counter

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate
from django.contrib import auth
from django.contrib import messages

from car_dealer_portal.forms import VehicleForm
from customer_portal.models import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect


# Create your views here.
def contact(request):
    return render(request, 'contact.html')
def index(request):
    if not request.user.is_authenticated:
        return render(request, 'car_dealer/login.html')
    else:
        return render(request, 'car_dealer/home_page.html')


def login(request):
    return render(request, 'car_dealer/login.html')
def updated(request):
    return render(request,'car_dealer/updated.html')


def auth_view(request):
    if request.user.is_authenticated:
        return render(request, 'car_dealer/home_page.html')
    else:
        username = request.POST['username']
        password = request.POST['password']
        car_dealer_user = authenticate(request, username=username, password=password)
        try:
            car_dealer = CarDealer.objects.get(car_dealer=car_dealer_user)
        except:
            car_dealer = None
        if car_dealer is not None:
            auth.login(request, car_dealer_user)
            return render(request, 'car_dealer/home_page.html')
        else:
            return render(request, 'car_dealer/login_failed.html')


def logout_view(request):
    auth.logout(request)
    return render(request, 'car_dealer/login.html')


def register(request):
    return render(request, 'car_dealer/register.html')


def registration(request):
    username = request.POST['username']
    password = request.POST['password']
    mobile = request.POST['mobile']
    firstname = request.POST['firstname']
    lastname = request.POST['lastname']
    email = request.POST['email']
    city = request.POST['city']
    city = city.lower()
    pincode = request.POST['pincode']

    try:
        user = User.objects.create_user(username=username, password=password, email=email)
        user.first_name = firstname
        user.last_name = lastname
        user.save()
    except:
        return render(request, 'car_dealer/registration_error.html')
    try:
        area = Area.objects.get(city=city, pincode=pincode)
    except:
        area = None
    if area is not None:
        car_dealer = CarDealer(car_dealer=user, mobile=mobile, area=area)
    else:
        area = Area(city=city, pincode=pincode)
        area.save()
        area = Area.objects.get(city=city, pincode=pincode)
        car_dealer = CarDealer(car_dealer=user, mobile=mobile, area=area)
    car_dealer.save()
    return render(request, 'car_dealer/registered.html')


@login_required
def add_vehicle(request):
    car_name = request.POST['car_name']
    color = request.POST['color']
    cd = CarDealer.objects.get(car_dealer=request.user)
    city = request.POST['city']
    city = city.lower()
    pincode = request.POST['pincode']
    description = request.POST['description']
    capacity = request.POST['capacity']
    try:
        area = Area.objects.get(city=city, pincode=pincode)
    except:
        area = None
    if area is not None:
        car = Vehicles(car_name=car_name, color=color, dealer=cd, area=area, description=description, capacity=capacity)
    else:
        area = Area(city=city, pincode=pincode)
        area.save()
        area = Area.objects.get(city=city, pincode=pincode)
        car = Vehicles(car_name=car_name, color=color, dealer=cd, area=area, description=description, capacity=capacity)
    car.save()
    return render(request, 'car_dealer/vehicle_added.html')


@login_required
def manage_vehicles(request):
    username = request.user
    user = User.objects.get(username=username)
    car_dealer = CarDealer.objects.get(car_dealer=user)
    vehicle_list = []
    vehicles = Vehicles.objects.filter(dealer=car_dealer)
    for v in vehicles:
        vehicle_list.append(v)
    return render(request, 'car_dealer/manage.html', {'vehicle_list': vehicle_list})


@login_required
def order_list(request):
    username = request.user
    user = User.objects.get(username=username)
    car_dealer = CarDealer.objects.get(car_dealer=user)
    orders = Orders.objects.filter(car_dealer=car_dealer)
    order_list = []
    for o in orders:
        if o.is_complete == False:
            order_list.append(o)
    return render(request, 'car_dealer/order_list.html', {'order_list': order_list})


@login_required
def complete(request):
    order_id = request.POST['id']
    order = Orders.objects.get(id=order_id)
    vehicle = order.vehicle
    order.is_complete = True
    order.save()
    vehicle.is_available = True
    vehicle.save()
    return HttpResponseRedirect('/car_dealer_portal/order_list/')


@login_required
def history(request):
    user = User.objects.get(username=request.user)
    car_dealer = CarDealer.objects.get(car_dealer=user)
    orders = Orders.objects.filter(car_dealer=car_dealer)
    order_list = []
    for o in orders:
        order_list.append(o)
    return render(request, 'car_dealer/history.html', {'wallet': car_dealer.wallet, 'order_list': order_list})


@login_required
def delete(request):
    veh_id = request.POST['id']
    vehicle = Vehicles.objects.get(id=veh_id)
    vehicle.delete()
    return HttpResponseRedirect('/car_dealer_portal/manage_vehicles/')


@login_required
def edit_profile(request):
    user = request.user
    try:
        car_dealer = CarDealer.objects.get(car_dealer=user)
    except CarDealer.DoesNotExist:
        car_dealer = None

    if request.method == 'POST':
        try:
            firstname = request.POST.get('firstname')
            lastname = request.POST.get('lastname')
            username = request.POST.get('username')
            email = request.POST.get('email')
            mobile = request.POST.get('mobile')
            city = request.POST.get('city').lower()
            pincode = request.POST.get('pincode')

            user.first_name = firstname
            user.last_name = lastname
            user.username = username
            user.email = email
            user.save()

            if car_dealer:
                try:
                    area = Area.objects.get(city=city, pincode=pincode)
                except Area.DoesNotExist:
                    area = Area(city=city, pincode=pincode)
                    area.save()

                car_dealer.mobile = mobile
                car_dealer.area = area
                car_dealer.save()

            messages.success(request, 'Your profile was successfully updated!')
            return redirect('/car_dealer_portal/updated/')
        except Exception as e:
            return render(request, 'car_dealer/error.html', {'error_message': str(e)})

    context = {
        'user': user,
        'car_dealer': car_dealer,
    }
    return render(request, 'car_dealer/edit_profile.html', context)

@login_required
def view_profile(request):
    user = request.user
    try:
        car_dealer = CarDealer.objects.get(car_dealer=user)
    except CarDealer.DoesNotExist:
        car_dealer = None

    context = {
        'user': user,
        'car_dealer': car_dealer,
    }
    return render(request, 'car_dealer/view_profile.html', context)

@login_required
def update_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicles, id=vehicle_id, dealer__car_dealer=request.user)

    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehicle updated successfully.')
            return redirect('/car_dealer_portal/manage_vehicles/')
    else:
        form = VehicleForm(instance=vehicle)

    return render(request, 'car_dealer/edit_car.html', {'form': form, 'vehicle': vehicle})


@login_required
def vehicle_chart(request):
    vehicle_counts = Counter(Vehicles.objects.values_list('area__city', flat=True))
    labels = list(vehicle_counts.keys())
    data = list(vehicle_counts.values())

    return render(request, 'car_dealer/vehicle_chart.html', {'labels': labels, 'data': data})