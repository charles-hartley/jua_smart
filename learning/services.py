from openai import OpenAI
from django.conf import settings
from .models import ChatSession, ChatMessage, UserProfile, Course

class ChatBotService:
    def __init__(self, user):
        self.user = user
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
    def get_user_context(self):
        """Build dynamic context based on user's learning journey"""
        try:
            profile = UserProfile.objects.get(user=self.user)
            completed_courses = profile.completed_courses.all()
            
            context = {
                'learning_level': profile.learning_level,
                'completed_courses': [course.title for course in completed_courses],
                'current_progress': self.get_current_progress()
            }
            return context
        except UserProfile.DoesNotExist:
            return {'learning_level': 'beginner', 'completed_courses': []}
    
    def get_current_progress(self):
        """Get user's current lesson/module progress"""
        # This would integrate with your existing course progress tracking
        return "Currently in Solar Panel Basics module"
    
    def build_dynamic_prompt(self, user_message, context):
        """Create context-aware system prompt"""
        base_prompt = """You are JuaBot, a personalized solar energy tutor for Kenyan learners. 
        
        User Context:
        - Learning Level: {learning_level}
        - Completed Courses: {completed_courses}
        - Current Progress: {current_progress}
        
        Instructions:
        1. Adapt your language complexity to their learning level
        2. Reference their completed courses when relevant
        3. Provide practical examples relevant to Kenya's climate and economy
        4. If they ask about advanced topics but are a beginner, gently guide them to foundational concepts first
        5. Always be encouraging and supportive
        """.format(**context)
        
        return base_prompt
    
    def get_chat_response(self, user_message, session_id=None):
        """Generate dynamic response based on user context"""
        
        # Get or create chat session
        session, created = ChatSession.objects.get_or_create(
            user=self.user,
            id=session_id if session_id else None,
            defaults={'context_data': self.get_user_context()}
        )
        
        # Build context-aware prompt
        context = session.context_data
        system_prompt = self.build_dynamic_prompt(user_message, context)
        
        # Get recent conversation history for context
        recent_messages = ChatMessage.objects.filter(
            session=session
        ).order_by('-timestamp')[:5]
        
        # Build message history
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for msg in reversed(recent_messages):
            messages.append({"role": "user", "content": msg.user_message})
            messages.append({"role": "assistant", "content": msg.bot_response})
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            bot_response = response.choices[0].message.content
            
            # Save to database
            ChatMessage.objects.create(
                session=session,
                user_message=user_message,
                bot_response=bot_response
            )
            
            return {
                'response': bot_response,
                'session_id': session.id,
                'context': context
            }
            
        except Exception as e:
            return {'error': str(e)}