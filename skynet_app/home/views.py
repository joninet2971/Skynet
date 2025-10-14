from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.translation import activate, get_language
from django.views import View
from home.forms import LoginForm, RegisterForm, CarouselImageForm
from reservations.forms import SearchRouteForm 
from home.models import CarouselImage

import logging

logger = logging.getLogger(__name__)

def home_view(request):
    lang = request.GET.get('lang')
    if lang in ['es', 'en', 'pt']:
        activate(lang)

    current_lang = get_language()
    form = SearchRouteForm()
    images = CarouselImage.objects.all()
<<<<<<< HEAD
<<<<<<< HEAD

    languages = [l for l in ['es', 'en', 'pt'] if l != current_lang]

=======
=======
>>>>>>> main-api
    logger.error(
        "Ingresando a view",
        exc_info=True,
        extra={"Contenido del error"}
        )
<<<<<<< HEAD
>>>>>>> 1cd4108 (iniciar proyecto con api)
=======
>>>>>>> main-api
    return render(request, "home/index.html", {
        "form": form,
        "images": images,
        "current_lang": current_lang,
        "languages": languages
    })

def manage_carousel_view(request):
    images = CarouselImage.objects.all()

    if request.method == 'POST':
        form = CarouselImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('manage_carousel')
    else:
        form = CarouselImageForm()

    return render(request, "home/manage_carousel.html", {
        "form": form,
        "images": images
    })

def delete_carousel_image_view(request, image_id):
    image = get_object_or_404(CarouselImage, id=image_id)
    image.delete()
    return redirect('manage_carousel')
        
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

