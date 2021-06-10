from django.urls import path, include
from django.contrib.auth import views as auth_views

from .views import signup, activate, activation_sent, activation_not_sent, UserDetail
from .forms import UserLoginForm

app_name = 'user'

urlpatterns = [
    path('detail/<int:pk>/', UserDetail.as_view(), name='detail'),
    path('login/', auth_views.LoginView.as_view(authentication_form=UserLoginForm, template_name='user/login.html'), name='login'),

    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('signup/', signup, name='signup'),

    path('activate/<uidb64>/<token>/', activate, name='activate'),

    path('activation_unsuccessful/', activation_not_sent, name='activation_unsuccessful'),

    path('account_activation_sent/', activation_sent, name='activation_sent'),
]
