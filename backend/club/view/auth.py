# views/auth.py
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import Account, Admin

@api_view(['POST'])
def admin_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    try:
        account = Account.objects.get(username=username, password=password)
    except Account.DoesNotExist:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    if not Admin.objects.filter(account=account).exists():
        return Response({'error': 'Not an admin'}, status=status.HTTP_403_FORBIDDEN)

    refresh = RefreshToken.for_user(account)

    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    })
