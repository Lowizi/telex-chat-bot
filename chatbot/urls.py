"""
URL configuration for chatbot app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for viewsets
router = DefaultRouter()
router.register(r'conversations', views.ConversationViewSet, basename='conversation')
router.register(r'messages', views.MessageViewSet, basename='message')
router.register(r'bot-responses', views.BotResponseViewSet, basename='botresponse')

urlpatterns = [
    # Main A2A endpoint for Telex.im integration
    path('a2a/agent/chatbot', views.A2AAgentView.as_view(), name='a2a-agent'),
    
    # Health check
    path('health', views.health_check, name='health-check'),
    
    # Test endpoint
    path('test', views.test_agent, name='test-agent'),
    
    # Include router URLs
    path('', include(router.urls)),
]
