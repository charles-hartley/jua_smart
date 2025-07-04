from django.contrib import admin

# Register your models here.

## learning/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    Course, Lesson, Quiz, QuizQuestion, QuizOption, 
    UserProgress, QuizAttempt, QuizAnswer, ChatMessage, UserProfile
)

# Inline admin classes
class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ['title', 'order', 'is_active']

class QuizQuestionInline(admin.TabularInline):
    model = QuizQuestion
    extra = 1
    fields = ['question_text', 'question_type', 'points', 'order']

class QuizOptionInline(admin.TabularInline):
    model = QuizOption
    extra = 4
    fields = ['option_text', 'is_correct', 'order']

class QuizAnswerInline(admin.TabularInline):
    model = QuizAnswer
    extra = 0
    readonly_fields = ['question', 'selected_option', 'text_answer', 'is_correct', 'points_earned']

# Main admin classes
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'total_lessons', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['is_active', 'order']
    inlines = [LessonInline]
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'has_quiz', 'is_active', 'created_at']
    list_filter = ['course', 'is_active', 'created_at']
    search_fields = ['title', 'content', 'course__title']
    list_editable = ['order', 'is_active']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'total_questions', 'passing_score', 'max_attempts', 'is_active']
    list_filter = ['lesson__course', 'is_active', 'created_at']
    search_fields = ['title', 'lesson__title']
    inlines = [QuizQuestionInline]
    readonly_fields = ['created_at', 'updated_at']

@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'question_text', 'question_type', 'points', 'order']
    list_filter = ['quiz', 'question_type']
    search_fields = ['question_text', 'quiz__title']
    inlines = [QuizOptionInline]

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'completion_percentage', 'is_completed', 'last_accessed']
    list_filter = ['course', 'is_completed', 'started_at']
    search_fields = ['user__username', 'course__title']
    readonly_fields = ['started_at', 'last_accessed']

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'score', 'is_passed', 'attempt_number', 'started_at']
    list_filter = ['quiz', 'is_passed', 'started_at']
    search_fields = ['user__username', 'quiz__title']
    readonly_fields = ['started_at', 'completed_at']
    inlines = [QuizAnswerInline]

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'lesson', 'created_at']
    list_filter = ['lesson', 'created_at']
    search_fields = ['user__username', 'message', 'response']
    readonly_fields = ['created_at']

# Extend User admin to include profile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline]

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Customize admin site
admin.site.site_header = "JuaSmart Admin"
admin.site.site_title = "JuaSmart Admin Portal"
admin.site.index_title = "Welcome to JuaSmart Administration"