from django.contrib import admin
from .models import PricePlan, Feature, Review, Trainer, Profile

# --- Настройка Планов и Особенностей ---
class FeatureInline(admin.TabularInline):
    model = Feature
    extra = 1

@admin.register(PricePlan)
class PricePlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'is_featured')
    inlines = [FeatureInline]

# --- Настройка Отзывов ---
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating', 'created_at', 'role')
    list_filter = ('rating', 'created_at', 'role')
    search_fields = ('name', 'text')
    ordering = ('-created_at',)
    list_editable = ('rating',)

# --- Настройка Тренеров (ИСПРАВЛЕННАЯ) ---
@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    # Вместо 'name' используем наш метод 'get_name'
    list_display = ('get_name', 'specialization', 'rating', 'experience_years')
    search_fields = ('profile__user__username', 'specialization')
    list_filter = ('rating',)

    def get_name(self, obj):
        # Вытягиваем username из цепочки Trainer -> Profile -> User
        return obj.profile.user.username
    get_name.short_description = 'Coach Name' # Заголовок в админке

# --- Настройка Профилей Пользователей ---
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'active_plan', 'assigned_trainer')
    list_filter = ('role', 'active_plan')
    search_fields = ('user__username', 'user__email')
