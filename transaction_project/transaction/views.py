from django.http import HttpResponse
from django.shortcuts import render

def index(requests):
     return HttpResponse("Привет, мир! Мой первый сайт на Django.")


# Create your views here.
