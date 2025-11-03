"""
API Views for the chatbot
"""
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
import uuid

from .models import Conversation, Message, BotResponse
from .serializers import (
    ConversationSerializer, MessageSerializer, 
    BotResponseSerializer, A2ARequestSerializer, A2AResponseSerializer
)
from .agent import agent


class A2AAgentView(APIView):
    """
    Main endpoint for Telex.im A2A (Agent-to-Agent) protocol integration
    This endpoint follows the JSON-RPC 2.0 specification for A2A protocol
    """
    
    def post(self, request):
        """
        Handle incoming A2A messages using JSON-RPC 2.0 format
        
        Expected JSON-RPC format:
        {
            "jsonrpc": "2.0",
            "id": "request-id",
            "method": "message/send",
            "params": {
                "message": {
                    "kind": "message",
                    "role": "user",
                    "parts": [{"kind": "text", "text": "Hello"}],
                    "messageId": "msg-001",
                    "taskId": "task-001"
                },
                "configuration": {
                    "blocking": true
                }
            }
        }
        
        Simplified format also supported:
        {
            "message": "User's message text",
            "conversation_id": "unique_conversation_id"
        }
        """
        try:
            body = request.data
            
            # Check if it's JSON-RPC 2.0 format
            if body.get('jsonrpc') == '2.0':
                return self._handle_jsonrpc_request(body)
            else:
                # Handle simplified format for backward compatibility
                return self._handle_simple_request(body)
                
        except Exception as e:
            return Response(
                {
                    'jsonrpc': '2.0',
                    'id': body.get('id') if 'body' in locals() else None,
                    'error': {
                        'code': -32603,
                        'message': 'Internal error',
                        'data': {'details': str(e)}
                    }
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _handle_jsonrpc_request(self, body):
        """Handle JSON-RPC 2.0 A2A protocol request"""
        # Validate JSON-RPC format
        if 'id' not in body:
            return Response(
                {
                    'jsonrpc': '2.0',
                    'id': None,
                    'error': {
                        'code': -32600,
                        'message': 'Invalid Request: id is required'
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        request_id = body['id']
        method = body.get('method')
        params = body.get('params', {})
        
        # Ensure params is a dict
        if not isinstance(params, dict):
            return Response(
                {
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'error': {
                        'code': -32602,
                        'message': 'Invalid params: params must be an object'
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Extract message from params
        message_data = params.get('message', {})
        
        # Handle both nested message object and direct params
        if isinstance(message_data, dict):
            parts = message_data.get('parts', [])
        else:
            # Fallback: check if message is directly in params
            parts = []
            message_data = {}
        
        # Also check for direct message in params (Telex format)
        if 'message' in params and isinstance(params['message'], str):
            user_message = params['message']
        else:
            # Extract text from parts
            user_message = ''
            for part in parts:
                if isinstance(part, dict) and part.get('kind') == 'text':
                    user_message = part.get('text', '')
                    break
        
        if not user_message:
            return Response(
                {
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'error': {
                        'code': -32602,
                        'message': 'Invalid params: message text is required'
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get task and message IDs
        task_id = params.get('taskId') or (message_data.get('taskId') if isinstance(message_data, dict) else None) or str(uuid.uuid4())
        message_id = (message_data.get('messageId') if isinstance(message_data, dict) else None) or str(uuid.uuid4())
        context_id = params.get('contextId') or str(uuid.uuid4())
        
        # Process message
        result = agent.process_message(
            user_message=user_message,
            conversation_id=context_id,
            user_id=(message_data.get('userId') if isinstance(message_data, dict) else None),
            channel_id=(message_data.get('channelId') if isinstance(message_data, dict) else None)
        )
        
        # Build JSON-RPC response in A2A format
        response_data = {
            'jsonrpc': '2.0',
            'id': request_id,
            'result': {
                'id': task_id,
                'contextId': context_id,
                'status': {
                    'state': 'input-required',
                    'timestamp': timezone.now().isoformat(),
                    'message': {
                        'messageId': str(uuid.uuid4()),
                        'role': 'agent',
                        'parts': [
                            {
                                'kind': 'text',
                                'text': result['response']
                            }
                        ],
                        'kind': 'message',
                        'taskId': task_id
                    }
                },
                'artifacts': [
                    {
                        'artifactId': str(uuid.uuid4()),
                        'name': 'response',
                        'parts': [
                            {
                                'kind': 'text',
                                'text': result['response']
                            }
                        ]
                    }
                ],
                'history': [
                    {
                        'messageId': message_id,
                        'role': 'user',
                        'parts': [{'kind': 'text', 'text': user_message}],
                        'kind': 'message',
                        'taskId': task_id
                    },
                    {
                        'messageId': str(uuid.uuid4()),
                        'role': 'agent',
                        'parts': [{'kind': 'text', 'text': result['response']}],
                        'kind': 'message',
                        'taskId': task_id
                    }
                ],
                'kind': 'task'
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    def _handle_simple_request(self, body):
        """Handle simplified request format for backward compatibility"""
        serializer = A2ARequestSerializer(data=body)
        if not serializer.is_valid():
            return Response(
                {'error': 'Invalid request format', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = serializer.validated_data
        user_message = data.get('message')
        conversation_id = data.get('conversation_id') or str(uuid.uuid4())
        user_id = data.get('user_id')
        channel_id = data.get('channel_id')
        
        result = agent.process_message(
            user_message=user_message,
            conversation_id=conversation_id,
            user_id=user_id,
            channel_id=channel_id
        )
        
        response_data = {
            'response': result['response'],
            'conversation_id': result['conversation_id'],
            'timestamp': result['timestamp'],
            'status': 'success'
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    def get(self, request):
        """
        Health check endpoint
        """
        return Response({
            'status': 'online',
            'service': 'Chat Automation Bot',
            'version': '1.0.0',
            'protocol': 'A2A JSON-RPC 2.0',
            'timestamp': timezone.now().isoformat()
        })


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    
    def get_queryset(self):
        queryset = Conversation.objects.all()
        
        # Filter by channel_id if provided
        channel_id = self.request.query_params.get('channel_id')
        if channel_id:
            queryset = queryset.filter(channel_id=channel_id)
        
        # Filter by user_id if provided
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """
        Get all messages for a specific conversation
        """
        conversation = self.get_object()
        messages = conversation.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing messages (read-only)
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    
    def get_queryset(self):
        queryset = Message.objects.all()
        
        # Filter by conversation_id if provided
        conversation_id = self.request.query_params.get('conversation_id')
        if conversation_id:
            queryset = queryset.filter(conversation__conversation_id=conversation_id)
        
        # Filter by message_type if provided
        message_type = self.request.query_params.get('message_type')
        if message_type:
            queryset = queryset.filter(message_type=message_type)
        
        return queryset


class BotResponseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing automated bot responses
    """
    queryset = BotResponse.objects.all()
    serializer_class = BotResponseSerializer
    
    def get_queryset(self):
        queryset = BotResponse.objects.all()
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset


@api_view(['GET'])
def health_check(request):
    """
    Simple health check endpoint
    """
    return Response({
        'status': 'healthy',
        'service': 'Telex Chat Automation Bot',
        'timestamp': timezone.now().isoformat()
    })


@api_view(['POST'])
def test_agent(request):
    """
    Test endpoint to quickly test the agent without Telex integration
    """
    message = request.data.get('message', '')
    
    if not message:
        return Response(
            {'error': 'Message is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        result = agent.process_message(
            user_message=message,
            conversation_id=f"test-{uuid.uuid4()}",
            user_id="test_user",
            channel_id="test_channel"
        )
        return Response(result, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
