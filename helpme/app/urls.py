from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static

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
    path('logout/', views.logout, name='logout'),
    path('like/', views.like, name='like'),
    path('dislike/', views.dislike, name='dislike'),
    path('correct_answer/', views.correct_answer, name='correct_answer')
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + \
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
