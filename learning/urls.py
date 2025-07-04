from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('lesson/', views.lesson, name='lesson'),
    path('quiz/', views.quiz, name='quiz'),
    path('quiz/solar_basics/', views.quiz_solar_basics, name='quiz_solar_basics'),
    path('quiz/energy_storage/', views.quiz_energy_storage, name='quiz_energy_storage'),
    path('quiz/home_solar_systems/', views.quiz_home_systems, name='quiz_home_systems'),
    path('save/', views.save_kenya, name='save'),
    path('calculator/', views.calculator, name='calculator'),
    path('save/', views.save_kenya, name='save'),

    path('api/courses/', views.CourseListView.as_view(), name='api_course_list'),
    path('api/courses/<uuid:pk>/', views.CourseDetailView.as_view(), name='api_course_detail'),
    path('api/courses/<uuid:course_id>/start/', views.start_course, name='api_start_course'),

    path('api/lessons/<uuid:pk>/', views.LessonDetailView.as_view(), name='api_lesson_detail'),
    path('api/lessons/<uuid:lesson_id>/complete/', views.complete_lesson, name='api_complete_lesson'),

    path('api/quizzes/<uuid:pk>/', views.QuizDetailView.as_view(), name='api_quiz_detail'),
    path('api/quizzes/submit/', views.submit_quiz, name='api_submit_quiz'),

    path('api/progress/', views.UserProgressView.as_view(), name='api_user_progress'),
    path('api/chatbot/', views.chatbot, name='api_chatbot'),
    path('api/profile/', views.UserProfileView.as_view(), name='api_user_profile'),
]
