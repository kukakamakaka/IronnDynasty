from django.contrib import admin
from django.urls import path, include
from fitness import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- ГЛАВНЫЕ СТРАНИЦЫ ---
    path('', views.index, name='index'),
    path('schedule/', views.schedule, name='schedule'),
    path('reviews/', views.reviews_view, name='reviews'),

    # --- АВТОРИЗАЦИЯ И РЕГИСТРАЦИЯ ---
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),

    # --- ЛИЧНЫЙ КАБИНЕТ (DASHBOARD) ---
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/delete/', views.delete_profile, name='delete_profile'),

    # --- ЛОГИКА ВЫБОРА (ДЛЯ КНОПОК) ---
    path('checkout/<int:plan_id>/', views.checkout, name='checkout'),
    path('select-trainer/<int:trainer_id>/', views.select_trainer, name='select_trainer'),

    # --- ЧАТ (ВАЖНО: Добавлен слэш в конце для стабильности fetch) ---
    path('chat/send/', views.send_message, name='send_message'),
    path('chat/get/<int:user_id>/', views.get_messages, name='get_messages'),

    # --- СЛУЖЕБНЫЕ ПУТИ ---
    path("__reload__/", include("django_browser_reload.urls")),
]

# Обслуживание медиа и статики в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Добавь в urls.py
path('api/schedule/', views.get_schedule_api, name='api_schedule'),
path('api/book/<int:slot_id>/', views.book_training, name='api_book'),