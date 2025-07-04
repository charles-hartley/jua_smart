from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Course, Lesson, Quiz, QuizQuestion, QuizOption,
    UserProgress, QuizAttempt, QuizAnswer, ChatMessage, UserProfile
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['user', 'phone_number', 'location', 'bio', 'avatar', 'date_of_birth']

class CourseSerializer(serializers.ModelSerializer):
    total_lessons = serializers.ReadOnlyField()
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'image', 'total_lessons', 'order', 'created_at']

class LessonSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    has_quiz = serializers.ReadOnlyField()
    
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'content', 'image', 'video_url', 'course_title', 'has_quiz', 'order']

class QuizOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizOption
        fields = ['id', 'option_text', 'order']

class QuizQuestionSerializer(serializers.ModelSerializer):
    options = QuizOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = QuizQuestion
        fields = ['id', 'question_text', 'question_type', 'points', 'options', 'explanation', 'order']

class QuizSerializer(serializers.ModelSerializer):
    questions = QuizQuestionSerializer(many=True, read_only=True)
    total_questions = serializers.ReadOnlyField()
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'passing_score', 'max_attempts', 'time_limit', 
                 'total_questions', 'lesson_title', 'questions']

class UserProgressSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    completed_lessons_count = serializers.SerializerMethodField()
    current_lesson_title = serializers.CharField(source='current_lesson.title', read_only=True)
    
    class Meta:
        model = UserProgress
        fields = ['id', 'course', 'course_title', 'completion_percentage', 'is_completed', 
                 'completed_lessons_count', 'current_lesson_title', 'last_accessed']
    
    def get_completed_lessons_count(self, obj):
        return obj.completed_lessons.count()

class QuizAttemptSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = ['id', 'quiz', 'quiz_title', 'user_name', 'score', 'total_questions', 
                 'correct_answers', 'is_passed', 'attempt_number', 'time_taken', 'started_at']

class ChatMessageSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'message', 'response', 'user_name', 'lesson_title', 'created_at']

class QuizSubmissionSerializer(serializers.Serializer):
    quiz_id = serializers.UUIDField()
    answers = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )
    time_taken = serializers.IntegerField(required=False)

class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=1000)
    lesson_id = serializers.UUIDField(required=False)