from django.urls import path
from app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('question/<int:question_id>', views.question, name='question'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('ask/', views.ask, name='ask'),
    path('tag/<tag_name>', views.tag, name='tag'),
    path('settings/', views.settings, name='settings'),
    path('profile/<int:user_id>', views.profile, name='profile'),
    path('logout/', views.logout, name='logout')
]