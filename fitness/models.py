from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

# 1. ТАРИФЫ
class PricePlan(models.Model):
    title = models.CharField(max_length=100, verbose_name="Название тарифа")
    price = models.IntegerField(verbose_name="Цена")
    description = models.TextField(verbose_name="Описание", blank=True)
    is_featured = models.BooleanField(default=False, verbose_name="Популярный")

    def __str__(self):
        return self.title

class Feature(models.Model):
    plan = models.ForeignKey(PricePlan, related_name='features', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name="Преимущество")

# 2. ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ
class Profile(models.Model):
    class Role(models.TextChoices):
        CLIENT = 'CLIENT', 'Client'
        TRAINER = 'TRAINER', 'Trainer'
        GUEST = 'GUEST', 'Guest'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="User Account")
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.GUEST, verbose_name="System Role")
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', blank=True, verbose_name="Profile Picture")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Phone Number")

    # Physical Metrics
    height = models.FloatField(null=True, blank=True, default=0.0, verbose_name="Height (cm)")
    weight = models.FloatField(null=True, blank=True, default=0.0, verbose_name="Current Weight (kg)")

    # Relationships
    assigned_trainer = models.ForeignKey('Trainer', on_delete=models.SET_NULL, null=True, blank=True, related_name='students', verbose_name="Assigned Coach")
    active_plan = models.ForeignKey(PricePlan, on_delete=models.SET_NULL, null=True, blank=True, related_name='subscribed_profiles', verbose_name="Active Subscription Plan")

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

# 3. ТРЕНЕРЫ
class Trainer(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, limit_choices_to={'role': 'TRAINER'})
    specialization = models.CharField(max_length=100, verbose_name="Специализация")
    bio = models.TextField(verbose_name="Описание для карточки")
    rating = models.FloatField(default=5.0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    experience_years = models.IntegerField(default=0)
    tags = models.CharField(max_length=200, help_text="Powerlifting, Bio-Hacking")

    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(',')]

    def __str__(self):
        return f"Coach {self.profile.user.username}"

# 4. ГРУППЫ
class TrainingGroup(models.Model):
    name = models.CharField(max_length=100)
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='groups')
    members = models.ManyToManyField(Profile, related_name='training_groups', blank=True)
    schedule = models.CharField(max_length=200, verbose_name="Расписание")

    def __str__(self):
        return self.name

# 5. ОТЗЫВЫ
class Review(models.Model):
    # Заменяем или добавляем поле user
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    name = models.CharField(max_length=100) # Можно оставить для отображения имени
    role = models.CharField(max_length=100, default="Member")
    text = models.TextField()
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username if self.user else self.name} - {self.rating} stars"

# 6. ИСТОРИЯ ВЕСА
class WeightLog(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='weight_logs')
    weight = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.profile.user.username}: {self.weight}kg on {self.date}"

# --- СИГНАЛЫ ---
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# 7. модель сообщений
class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender} to {self.receiver}: {self.message[:20]}"


# Добавь это в models.py

class Workout(models.Model):
    """Тип тренировки (например: Yoga, Crossfit, Box)"""
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=20, default="#9d50bb", help_text="HEX color для календаря")

    def __str__(self):
        return self.title


class ScheduleSlot(models.Model):
    """Конкретный слот в календаре"""
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='slots')
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, null=True, blank=True)

    start_time = models.DateTimeField(verbose_name="Начало")
    end_time = models.DateTimeField(verbose_name="Конец")

    max_capacity = models.IntegerField(default=1, verbose_name="Макс. человек")
    is_personal = models.BooleanField(default=False, verbose_name="Персональная?")

    class Meta:
        ordering = ['start_time']
        verbose_name = "Слот расписания"

    @property
    def free_spaces(self):
        booked_count = self.bookings.filter(status='CONFIRMED').count()
        return self.max_capacity - booked_count

    def __str__(self):
        return f"{self.trainer.profile.user.username} | {self.start_time.strftime('%d.%m %H:%M')}"


class Booking(models.Model):
    """Запись клиента на слот"""
    STATUS_CHOICES = [
        ('PENDING', 'Ожидает'),
        ('CONFIRMED', 'Подтверждена'),
        ('CANCELED', 'Отменена'),
    ]
    slot = models.ForeignKey(ScheduleSlot, on_delete=models.CASCADE, related_name='bookings')
    client = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='my_bookings')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('slot', 'client')  # Запрет двойной записи на один слот