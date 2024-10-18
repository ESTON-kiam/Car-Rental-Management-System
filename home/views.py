from django.shortcuts import render


def home_page(request):
    return render(request, 'home/index.html')


def car_dealer(request):
    return render(request, 'home/index1.html')



