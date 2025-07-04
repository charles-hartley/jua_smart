import json
import openai
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import (
    Course, Lesson, Quiz, QuizQuestion, QuizOption,
    UserProgress, QuizAttempt, QuizAnswer, ChatMessage, UserProfile
)
from .serializers import (
    CourseSerializer, LessonSerializer, QuizSerializer,
    UserProgressSerializer, QuizAttemptSerializer, ChatMessageSerializer,
    QuizSubmissionSerializer, ChatRequestSerializer, UserProfileSerializer
)

# Initialize OpenAI client with proper syntax
openai.api_key = settings.OPENAI_API_KEY

class ChatBotService:
    """Enhanced ChatBot Service with OpenAI Integration"""
    
    def __init__(self, user=None):
        self.user = user
        self.openai_client = openai
        
    def get_user_context(self):
        """Build dynamic context based on user's learning journey"""
        if not self.user or not self.user.is_authenticated:
            return {
                'learning_level': 'beginner',
                'completed_courses': [],
                'current_progress': 'Not logged in'
            }
        
        try:
            profile = UserProfile.objects.get(user=self.user)
            user_progress = UserProgress.objects.filter(user=self.user)
            completed_courses = [up.course.title for up in user_progress if up.is_completed]
            
            context = {
                'learning_level': profile.learning_level,
                'completed_courses': completed_courses,
                'current_progress': self.get_current_progress(),
                'username': self.user.username
            }
            return context
        except UserProfile.DoesNotExist:
            # Create profile if it doesn't exist
            UserProfile.objects.create(user=self.user)
            return {
                'learning_level': 'beginner',
                'completed_courses': [],
                'current_progress': 'Just started learning'
            }
    
    def get_current_progress(self):
        """Get user's current lesson/module progress"""
        if not self.user:
            return "Not logged in"
        
        try:
            current_progress = UserProgress.objects.filter(
                user=self.user, 
                is_completed=False
            ).first()
            
            if current_progress and current_progress.current_lesson:
                return f"Currently in: {current_progress.current_lesson.title}"
            return "Ready to start learning"
        except:
            return "Ready to start learning"
    
    def build_dynamic_prompt(self, user_message, context):
        """Create context-aware system prompt"""
        base_prompt = f"""You are JuaBot, a friendly and knowledgeable solar energy assistant specifically designed for Kenyan learners. 

USER CONTEXT:
- Learning Level: {context['learning_level']}
- Completed Courses: {', '.join(context['completed_courses']) if context['completed_courses'] else 'None yet'}
- Current Progress: {context['current_progress']}
- Username: {context.get('username', 'Friend')}

INSTRUCTIONS:
1. ONLY answer questions about solar energy, renewable energy, sustainability, and Kenya's green economy
2. Adapt your language complexity to their learning level:
   - Beginner: Use simple terms, explain basics
   - Intermediate: Use more technical terms but explain complex concepts
   - Advanced: Use technical language freely
3. Reference their completed courses when relevant
4. Provide practical examples relevant to Kenya's climate, economy, and context
5. Use friendly greetings like "Habari!" and include relevant emojis
6. If they ask about topics outside solar/renewable energy, politely redirect them back to solar topics
7. Keep responses concise but informative (under 300 words)
8. Always be encouraging and supportive of their learning journey

KENYA CONTEXT:
- Kenya receives 4-6 kWh/m² of solar energy daily
- Solar systems range from KES 100,000 to KES 500,000 for homes
- Kenya has excellent solar potential year-round
- Focus on practical benefits: reduced electricity bills, energy independence, environmental protection

If asked about non-solar topics, respond with: "I'm specialized in solar energy topics! Let me help you with solar panels, costs, installation, or Kenya's solar potential instead. What would you like to know?" """
        
        return base_prompt
    
    def get_chat_response(self, user_message, session_id=None):
        """Generate dynamic response using OpenAI"""
        
        # Get user context
        context = self.get_user_context()
        
        # Build context-aware prompt
        system_prompt = self.build_dynamic_prompt(user_message, context)
        
        # Get recent conversation history if session exists
        messages = [{"role": "system", "content": system_prompt}]
        
        if self.user and self.user.is_authenticated:
            # Get recent chat history for context
            recent_messages = ChatMessage.objects.filter(
                user=self.user
            ).order_by('-created_at')[:6]  # Last 3 exchanges
            
            # Add conversation history
            for msg in reversed(recent_messages):
                messages.append({"role": "user", "content": msg.message})
                messages.append({"role": "assistant", "content": msg.response})
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        try:
            # Use updated OpenAI API syntax
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=400,
                temperature=0.7
            )
            
            bot_response = response.choices[0].message.content
            
            # Save to database if user is authenticated
            if self.user and self.user.is_authenticated:
                ChatMessage.objects.create(
                    user=self.user,
                    message=user_message,
                    response=bot_response
                )
            
            return {
                'response': bot_response,
                'session_id': session_id or 'default',
                'context': context
            }
            
        except Exception as e:
            # Fallback response if OpenAI fails
            fallback_response = self.get_fallback_response(user_message)
            return {
                'response': fallback_response,
                'session_id': session_id or 'default',
                'error': f"OpenAI Error: {str(e)}"
            }
    
    def get_fallback_response(self, message):
        """Fallback responses when OpenAI is unavailable"""
        message_lower = message.lower()
        
        responses = {
            'solar': 'Solar energy is perfect for Kenya! We have 4-6 kWh/m² daily solar potential. Would you like to know about solar panels, costs, or installation? 🌞',
            'panel': 'Solar panels convert sunlight to electricity using photovoltaic cells. They last 25+ years and can cut your electricity bills significantly! 💡',
            'cost': 'Solar systems in Kenya range from KES 100,000 to KES 500,000 for homes. The investment pays off through electricity savings! 💰',
            'benefit': 'Solar benefits: reduced bills, environmental protection, energy independence, and supporting Kenya\'s green economy! 🌱',
            'kenya': 'Kenya has amazing solar potential! Abundant sunshine year-round makes solar perfect for homes and businesses. 🇰🇪',
            'installation': 'Solar installation involves site assessment, system design, mounting, and electrical connections. Use certified installers! 🔧',
            'hello': 'Habari! I\'m JuaBot, your solar energy assistant. How can I help you learn about solar power today? 🌞',
            'hi': 'Habari! Ready to learn about solar energy in Kenya? What interests you most? 😊'
        }
        
        for keyword, response in responses.items():
            if keyword in message_lower:
                return response
        
        return 'Great question about solar energy! I can help with solar panels, costs, benefits, installation, and Kenya\'s solar potential. What would you like to know? 🤔'

# CONSOLIDATED CHATBOT VIEW
@csrf_exempt
def chatbot(request):
    """Main chatbot endpoint with OpenAI integration"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            session_id = data.get('session_id')
            
            if not message:
                return JsonResponse({'error': 'No message provided'}, status=400)
            
            # Initialize chatbot service
            # Pass user if authenticated, None if not
            user = request.user if request.user.is_authenticated else None
            chatbot_service = ChatBotService(user)
            
            # Get response
            result = chatbot_service.get_chat_response(message, session_id)
            
            return JsonResponse(result)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

# REST API VIEWS (keeping your existing API structure)
class CourseListView(generics.ListAPIView):
    """List all active courses"""
    queryset = Course.objects.filter(is_active=True)
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

class CourseDetailView(generics.RetrieveAPIView):
    """Get course details with lessons"""
    queryset = Course.objects.filter(is_active=True)
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

class LessonDetailView(generics.RetrieveAPIView):
    """Get lesson details"""
    queryset = Lesson.objects.filter(is_active=True)
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]

class QuizDetailView(generics.RetrieveAPIView):
    """Get quiz details with questions"""
    queryset = Quiz.objects.filter(is_active=True)
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

class UserProgressView(generics.ListAPIView):
    """Get user's progress across all courses"""
    serializer_class = UserProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserProgress.objects.filter(user=self.request.user)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get and update user profile"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def start_course(request, course_id):
    """Start a course for the user"""
    try:
        course = get_object_or_404(Course, id=course_id, is_active=True)
        user_progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            course=course
        )
        
        if created:
            first_lesson = course.lessons.filter(is_active=True).first()
            if first_lesson:
                user_progress.current_lesson = first_lesson
                user_progress.save()
        
        serializer = UserProgressSerializer(user_progress)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {"error": "Failed to start course", "details": str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def complete_lesson(request, lesson_id):
    """Mark a lesson as completed"""
    try:
        lesson = get_object_or_404(Lesson, id=lesson_id, is_active=True)
        user_progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            course=lesson.course
        )
        
        user_progress.completed_lessons.add(lesson)
        
        next_lesson = lesson.course.lessons.filter(
            is_active=True, 
            order__gt=lesson.order
        ).first()
        
        if next_lesson:
            user_progress.current_lesson = next_lesson
        
        user_progress.update_progress()
        
        serializer = UserProgressSerializer(user_progress)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {"error": "Failed to complete lesson", "details": str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_quiz(request):
    """Submit quiz answers and calculate score"""
    serializer = QuizSubmissionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        quiz_id = serializer.validated_data['quiz_id']
        answers = serializer.validated_data['answers']
        time_taken = serializer.validated_data.get('time_taken', 0)
        
        quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
        
        previous_attempts = QuizAttempt.objects.filter(
            user=request.user, 
            quiz=quiz
        ).count()
        
        if previous_attempts >= quiz.max_attempts:
            return Response(
                {"error": "Maximum attempts exceeded"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        attempt = QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            attempt_number=previous_attempts + 1,
            time_taken=time_taken,
            total_questions=quiz.questions.count(),
            started_at=timezone.now()
        )
        
        correct_count = 0
        total_points = 0
        earned_points = 0
        
        for answer_data in answers:
            question_id = answer_data.get('question_id')
            selected_option_id = answer_data.get('selected_option_id')
            text_answer = answer_data.get('text_answer', '')
            
            try:
                question = QuizQuestion.objects.get(id=question_id, quiz=quiz)
                total_points += question.points
                
                is_correct = False
                points_earned = 0
                
                if question.question_type in ['multiple_choice', 'true_false']:
                    if selected_option_id:
                        selected_option = QuizOption.objects.get(id=selected_option_id, question=question)
                        is_correct = selected_option.is_correct
                        if is_correct:
                            correct_count += 1
                            points_earned = question.points
                            earned_points += points_earned
                        
                        QuizAnswer.objects.create(
                            attempt=attempt,
                            question=question,
                            selected_option=selected_option,
                            is_correct=is_correct,
                            points_earned=points_earned
                        )
                
                elif question.question_type == 'short_answer':
                    QuizAnswer.objects.create(
                        attempt=attempt,
                        question=question,
                        text_answer=text_answer,
                        is_correct=False,
                        points_earned=0
                    )
            
            except (QuizQuestion.DoesNotExist, QuizOption.DoesNotExist):
                continue
        
        if total_points > 0:
            score = int((earned_points / total_points) * 100)
        else:
            score = 0
        
        attempt.score = score
        attempt.correct_answers = correct_count
        attempt.is_passed = score >= quiz.passing_score
        attempt.completed_at = timezone.now()
        attempt.save()
        
        if attempt.is_passed:
            user_progress, created = UserProgress.objects.get_or_create(
                user=request.user,
                course=quiz.lesson.course
            )
            user_progress.completed_lessons.add(quiz.lesson)
            user_progress.update_progress()
        
        result_data = {
            "attempt_id": attempt.id,
            "score": score,
            "correct_answers": correct_count,
            "total_questions": attempt.total_questions,
            "is_passed": attempt.is_passed,
            "passing_score": quiz.passing_score,
            "time_taken": time_taken
        }
        
        return Response(result_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {"error": "Failed to submit quiz", "details": str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

# Keep all your other existing views (login, register, dashboard, etc.)
def home(request):
    """Home page view"""
    return render(request, 'home.html')

def user_login(request):
    if request.method == 'POST':
        email_or_username = request.POST.get('email')
        password = request.POST.get('password')

        # Try both username and email
        user = authenticate(request, username=email_or_username, password=password)
        if user is None:
            try:
                user_obj = User.objects.get(email=email_or_username)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass

        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful! Welcome to JuaSmart.')
            return redirect('dashboard')  # change this if your dashboard URL is different
        else:
            messages.error(request, 'Invalid credentials. Please try again.')

    return render(request, 'login.html')

def user_register(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'register.html')

        if User.objects.filter(username=email).exists():
            messages.error(request, 'A user with this email already exists.')
            return render(request, 'register.html')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password1,
            first_name=full_name  # Or split into first/last if needed
        )
        login(request, user)
        messages.success(request, 'Registration successful! You are now logged in.')
        return redirect('dashboard')

    return render(request, 'register.html')

def user_logout(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

#@login_required
def dashboard(request):
    """Dashboard view - requires login"""
    return render(request, 'dashboard.html')

def lesson(request):
    """Lesson view"""
    return render(request, 'lesson.html')

def quiz(request):
    """Quiz view"""
    return render(request, 'quiz.html')

def quiz_solar_basics(request):
    """Solar Basics quiz page"""
    return render(request, 'quiz_solar_basics.html')

def quiz_energy_storage(request):
    """Energy Storage quiz page"""
    return render(request, 'quiz_energy_storage.html')

def quiz_home_systems(request):
    """Home Solar Systems quiz page"""
    return render(request, 'quiz_home_systems.html')


def save_kenya(request):
    """Save Kenya page view"""
    return render(request, 'save.html')


def calculator(request):
    """
    Solar calculator view - calculates solar panel requirements
    based on user's energy needs and location
    """
    if request.method == 'POST':
        # Handle calculator form submission
        try:
            monthly_bill = float(request.POST.get('monthly_bill', 0))
            roof_area = float(request.POST.get('roof_area', 0))
            location = request.POST.get('location', '')
            
            # Basic solar calculation logic
            # This is a simplified calculation - you'd want more sophisticated logic
            estimated_kwh = monthly_bill * 12 / 0.12  # Assuming $0.12 per kWh
            panels_needed = estimated_kwh / 1500  # Assuming 1500 kWh per panel per year
            system_cost = panels_needed * 300  # Assuming $300 per panel
            
            context = {
                'calculation_result': {
                    'monthly_bill': monthly_bill,
                    'estimated_kwh': estimated_kwh,
                    'panels_needed': int(panels_needed),
                    'system_cost': system_cost,
                    'payback_period': system_cost / (monthly_bill * 12),
                }
            }
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(context['calculation_result'])
            
            return render(request, 'calculator.html', context)
            
        except (ValueError, TypeError):
            error_message = "Please enter valid numbers for all fields."
            return render(request, 'calculator.html', {'error': error_message})
    
    # GET request - show the calculator form
    return render(request, 'calculator.html')