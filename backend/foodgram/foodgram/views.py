from django.shortcuts import redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


@api_view(['GET'])
@permission_classes([AllowAny])
def short_link(request, recipe_id=None):
    return redirect(f'/api/recipes/{recipe_id}/')
