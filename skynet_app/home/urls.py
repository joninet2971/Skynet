from django.urls import path
from home.views import (
    home_view,
    LoginView,
    LogoutView,
    RegisterView,
    manage_carousel_view,
    delete_carousel_image_view
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('carousel/manage/', manage_carousel_view, name='manage_carousel'),
    path('carousel/delete/<int:image_id>/', delete_carousel_image_view, name='delete_carousel_image'),

    path("", home_view, name="home"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)