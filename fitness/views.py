from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Q  # ОШИБКА 1: Ты использовал models.Q, но не импортировал Q напрямую или не использовал django.db.models
import json

# Импорт твоих моделей
from .models import PricePlan, Review, Trainer, Profile, WeightLog, ChatMessage, Workout, ScheduleSlot, Booking
from .forms import RegistrationForm, ProfileUpdateForm

# --- ГЛАВНАЯ СТРАНИЦА ---
def index(request):
    plans = PricePlan.objects.all().prefetch_related('features')
    reviews = Review.objects.all().order_by('-created_at')
    trainers = Trainer.objects.all().select_related('profile__user')

    profile = None
    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)

    # Добавляем эти данные и сюда тоже!
    # Без них index.html выдаст ошибку, если там есть календарь
    hours_list = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
    days_list = [
        {'id': 1, 'name': 'Mon'}, {'id': 2, 'name': 'Tue'},
        {'id': 3, 'name': 'Wed'}, {'id': 4, 'name': 'Thu'},
        {'id': 5, 'name': 'Fri'}, {'id': 6, 'name': 'Sat'},
        {'id': 7, 'name': 'Sun'},
    ]

    return render(request, 'index.html', {
        'plans': plans,
        'reviews': reviews,
        'trainers': trainers,
        'profile': profile,
        'hours_list': hours_list,
        'days_list': days_list,
    })

@login_required
def dashboard(request):
    # 1. Получаем профиль текущего пользователя
    user_profile, created = Profile.objects.get_or_create(user=request.user)
    form = ProfileUpdateForm(instance=user_profile)

    # 2. ЛОГИКА ГРАФИКА
    # Берем ПОСЛЕДНИЕ 7 записей (сортировка от новых к старым)
    weight_history_qs = WeightLog.objects.filter(profile=user_profile).order_by('-date')[:7]

    # Переворачиваем их обратно (.reverse() или [::-1]), чтобы на графике они шли по порядку времени
    weight_history = list(weight_history_qs)[::-1]

    if weight_history:
        # Извлекаем даты и значения веса
        labels = [log.date.strftime("%d.%m") for log in weight_history]
        values = [float(log.weight) for log in weight_history]
    else:
        # Если истории нет, показываем текущий вес из профиля как единственную точку
        labels = ["Start"]
        current_weight = float(user_profile.weight) if user_profile.weight else 0
        values = [current_weight]

    context = {
        'profile': user_profile,
        'form': form,
        'labels': labels,
        'values': values,
    }

    # 3. ЛОГИКА ДЛЯ ТРЕНЕРА
    if user_profile.role == 'TRAINER':
        try:
            trainer_instance = Trainer.objects.get(profile=user_profile)
            context['students'] = Profile.objects.filter(assigned_trainer=trainer_instance).select_related('user',
                                                                                                           'active_plan')
        except Trainer.DoesNotExist:
            context['students'] = []
            messages.warning(request, "Профиль тренера не найден.")

    # 4. ЛОГИКА ДЛЯ КЛИЕНТА
    else:
        context['all_trainers'] = Trainer.objects.all().select_related('profile__user')
        context['all_plans'] = PricePlan.objects.all()

    return render(request, 'dashboard.html', context)
# --- ВЫБОР ТРЕНЕРА ---
@login_required
def select_trainer(request, trainer_id):
    if request.method == 'POST':
        trainer = get_object_or_404(Trainer, id=trainer_id)
        profile = request.user.profile
        profile.assigned_trainer = trainer
        if profile.role == 'GUEST':
            profile.role = 'CLIENT'
        profile.save()
        messages.success(request, f"Trainer {trainer.profile.user.username} successfully assigned!")
    return redirect('dashboard')

# --- ВЫБОР ТАРИФА ---
@login_required
def checkout(request, plan_id):
    if request.method == 'POST':
        plan = get_object_or_404(PricePlan, id=plan_id)
        profile = request.user.profile
        profile.active_plan = plan
        profile.save()
        messages.success(request, f"Plan '{plan.title}' successfully activated!")
    return redirect('dashboard')



def edit_profile(request):
    user_profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)

        if form.is_valid():
            profile = form.save()

            new_weight = form.cleaned_data.get('weight')
            if new_weight:
                from .models import WeightLog
                from django.utils import timezone

                today = timezone.now().date()

                # ИСПРАВЛЕНО: Фильтруем просто по полю date.
                # Если в модели это DateField, используем date=today.
                # Если в модели это DateTimeField, используем date__date=today.
                # Самый универсальный способ для DateField:
                existing_log = WeightLog.objects.filter(
                    profile=user_profile,
                    date=today
                ).first()

                if existing_log:
                    existing_log.weight = new_weight
                    existing_log.save()
                else:
                    WeightLog.objects.create(
                        profile=user_profile,
                        weight=new_weight,
                        date=today # Явно указываем дату
                    )

            messages.success(request, "Success! Your progress has been updated.")
            return redirect('dashboard')
    else:
        form = ProfileUpdateForm(instance=user_profile)

    return render(request, 'edit_profile.html', {'form': form, 'profile': user_profile})

# --- УДАЛЕНИЕ АККАУНТА ---
@login_required
def delete_profile(request):
    # ОШИБКА 2: Этой функции у тебя не было, а в шаблоне ссылка была
    user = request.user
    user.delete()
    messages.success(request, "Account deleted successfully.")
    return redirect('index')

# --- РЕГИСТРАЦИЯ ---
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"{user.username}, welcome to Dynasty!")
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

# --- ОТЗЫВЫ ---
def reviews_view(request):
    if request.method == 'POST':
        rating = request.POST.get('rating')
        text = request.POST.get('text')
        if rating and text:
            Review.objects.create(user=request.user, rating=rating, text=text)
            messages.success(request, "Your review has been published!")
        else:
            messages.error(request, "Please fill in all fields.")
    return redirect('/#reviews-section')

# --- ЧАТ: ОТПРАВКА ---
@login_required
def send_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            receiver_id = data.get('receiver_id')
            message_text = data.get('message')

            if receiver_id and message_text:
                receiver = get_object_or_404(User, id=receiver_id)
                msg = ChatMessage.objects.create(
                    sender=request.user,
                    receiver=receiver,
                    message=message_text
                )
                return JsonResponse({
                    'status': 'ok',
                    'message': msg.message,
                    'timestamp': msg.timestamp.strftime('%H:%M')
                })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=400)

# --- ЧАТ: ПОЛУЧЕНИЕ ---
@login_required
def get_messages(request, user_id):
    # ОШИБКА 3: Исправлено обращение к Q и аргументы фильтрации
    messages_list = ChatMessage.objects.filter(
        Q(sender=request.user, receiver_id=user_id) |
        Q(sender_id=user_id, receiver=request.user)
    ).order_by('timestamp')

    results = []
    for m in messages_list:
        results.append({
            'sender_id': m.sender.id,
            'message': m.message,
            'timestamp': m.timestamp.strftime('%H:%M'),
            'is_mine': m.sender == request.user
        })
    return JsonResponse({'messages': results})


# --- СТРАНИЦА РАСПИСАНИЯ ---
def schedule(request):
    """
    Отображает страницу календаря.
    Передает тренеров, типы тренировок и часы для сетки.
    """
    # 1. Получаем всех тренеров и типы тренировок для фильтров
    trainers = Trainer.objects.all().select_related('profile__user')
    workouts = Workout.objects.all()

    # 2. Создаем список часов (от 8 утра до 9 вечера)
    # Это заменит проблемный фильтр |split в шаблоне
    hours_list = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]

    # 3. Список дней недели
    days_list = [
        {'id': 1, 'name': 'Mon'}, {'id': 2, 'name': 'Tue'},
        {'id': 3, 'name': 'Wed'}, {'id': 4, 'name': 'Thu'},
        {'id': 5, 'name': 'Fri'}, {'id': 6, 'name': 'Sat'},
        {'id': 7, 'name': 'Sun'},
    ]

    return render(request, 'schedule.html', {
        'trainers': trainers,
        'workouts': workouts,
        'days_list': days_list,
        'hours_list': hours_list,  # Теперь это доступно в шаблоне как список
    })

# --- API ДАННЫХ (ДЛЯ JS КАЛЕНДАРЯ) ---
def get_schedule_api(request):
    """
    Возвращает JSON с занятиями.
    Поддерживает фильтры по тренеру, дате и типу тренировки.
    """
    trainer_id = request.GET.get('trainer_id')
    workout_id = request.GET.get('workout_id')
    date_str = request.GET.get('date')

    # Оптимизируем запросы через select_related
    slots = ScheduleSlot.objects.select_related('trainer__profile__user', 'workout').all()

    if trainer_id:
        slots = slots.filter(trainer_id=trainer_id)
    if workout_id:
        slots = slots.filter(workout_id=workout_id)
    if date_str:
        slots = slots.filter(start_time__date=date_str)

    data = []
    for s in slots:
        data.append({
            'id': s.id,
            'title': s.workout.title if s.workout else "Individual Session",
            'trainer_name': s.trainer.profile.user.username,
            'start': s.start_time.strftime("%Y-%m-%dT%H:%M"),
            'end': s.end_time.strftime("%Y-%m-%dT%H:%M"),
            'free_spaces': s.free_spaces,
            'is_personal': s.is_personal,
            'color': s.workout.color if s.workout else "#9d50bb",  # Твой фиолетовый
        })

    return JsonResponse(data, safe=False)


# --- ЛОГИКА ЗАПИСИ (AJAX) ---
@login_required
def book_training(request, slot_id):
    """
    Безопасное бронирование места через POST запрос.
    """
    if request.method == 'POST':
        slot = get_object_or_404(ScheduleSlot, id=slot_id)

        # Проверка: не записывается ли тренер на свой же слот
        if request.user.profile.role == 'TRAINER' and slot.trainer.profile.user == request.user:
            return JsonResponse({'status': 'error', 'message': 'You cannot book your own class!'}, status=400)

        # Проверка наличия мест
        if slot.free_spaces > 0:
            booking, created = Booking.objects.get_or_create(
                slot=slot,
                client=request.user.profile
            )
            if created:
                return JsonResponse({'status': 'success', 'message': 'Successfully booked!'})
            else:
                return JsonResponse({'status': 'error', 'message': 'You are already in the list.'})

        return JsonResponse({'status': 'error', 'message': 'No free spaces left.'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid method.'}, status=405)
