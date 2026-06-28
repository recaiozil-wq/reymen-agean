---
skill_id: 0e1eeb15cff1
usage_count: 1
last_used: 2026-06-16
---
# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return Response({'message': 'You are authenticated'})
```