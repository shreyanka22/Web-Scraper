from django.shortcuts import render
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User

def signup_view(request):
    if request.method=='POST':
        uname=request.POST.get('username')
        email=request.POST.get('email')
        pass1=request.POST.get('password1')
        pass2=request.POST.get('password2')
        if pass1 != pass2:
            return HttpResponse("your password and confrim are not same")
        else:
            my_user=User.objects.create_user(uname,email,pass1)
            my_user.save()
            return redirect('login')
    return render(request,'signup.html')

def login_view(request):
    if request.method == 'POST':
        username=request.POST.get('username')
        pass1=request.POST.get('pass')
        user=authenticate(request,username=username,password=pass1)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            return HttpResponse("username and password is incorrect or not existed")
    return render(request,'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')