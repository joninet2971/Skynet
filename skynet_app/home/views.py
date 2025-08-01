from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.views import View
from home.forms import LoginForm, RegisterForm
from reservations.forms import SearchRouteForm 

def home_view(request):
    form = SearchRouteForm()
    return render(request, "home/index.html", {"form": form})
        
class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('home')
    

class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        return render(
            request,
            'home/auth/register.html',
            {"form" : form }
        )

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data["username"])
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email']
            )

            messages.success(
                request,
                "Usuario registrado correctamente"
            )
        return redirect('login')
        


class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(
            request,
            'home/auth/login.html',
            {"form": form}
        )

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(
                request, 
                username=username, 
                password=password
            )

            if user is not None: 
                login(request, user)
                messages.success(request, "Sesion iniciada")
                return redirect("home")
            else:
                messages.error(request, "El usuario o contraseña no coinciden")
                
        return render(
            request, 
            "home/auth/login.html", 
            {'form': form}
        ) 
