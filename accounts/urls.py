
from django.urls import path
from .views import CustomLoginView, CustomLogoutView

urlpatterns = [
    path('', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    # path('register-superuser/', views.register_superuser, name='register_superuser'),
]
