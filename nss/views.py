from django.shortcuts import render, redirect


def college(request):
    return render(request, 'dashboard/college.html')

