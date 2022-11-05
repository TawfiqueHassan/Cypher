from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, "index.html")

def FaceCheck(request):
    return render(request, "check.html")