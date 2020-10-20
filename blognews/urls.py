from django.urls import path
from . import views


urlpatterns = [
    path('', views.login, name="login"),
    path('signup/', views.signup, name='signup'),
    path('signup/register/', views.register, name='register'),
    path('loginvalidate/', views.loginvalidate, name='loginvalidate'),
    path('forgot/', views.forgot, name='forgot'),
    path('forgot/reset/', views.reset, name='reset'),
    path('forgot/reset/tokenVerification/', views.tokenVerification, name='verify'),
    path('forgot/reset/tokenVerification/resetPassword/', views.resetPassword, name='resetPassword'),
    path('success/', views.success, name='success'),
    path('success/logout/', views.logout, name="logout"),
    path('success/create/', views.create, name='create'),
    path('success/create/savenews/',views.savenews, name="savenews"),
    path('success/yourblogs/', views.yourblogs, name="yourblogs"),
    path('success/yourblogs/delete/', views.deleteblog, name="deleteblog"),
    path('success/yourblogs/viewblog/', views.viewblog, name="viewblog")

]
