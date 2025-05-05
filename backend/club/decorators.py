# yourapp/decorators.py
from rest_framework.response import Response
from rest_framework import status
from .models import Admin

def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        account = request.user  # Already set by JWT
        if not Admin.objects.filter(account=account).exists():
            return Response({'error': 'Admin access only'}, status=status.HTTP_403_FORBIDDEN)
        return view_func(request, *args, **kwargs)
    return _wrapped_view
