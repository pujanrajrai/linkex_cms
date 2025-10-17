from rest_framework_simplejwt.tokens import AccessToken
from django.http import JsonResponse
from rest_framework import status
from django.contrib import auth
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import redirect
from accounts.models import User
from django.http import JsonResponse
from rest_framework import status
from django.contrib.auth import logout


def has_roles(allowed_roles):
    def decorator(view_function):
        def wrap(request, *args, **kwargs):
            user = request.user
            authorization_header = request.META.get('HTTP_AUTHORIZATION')

            if authorization_header:
                token_prefix, token = authorization_header.split()
                if token_prefix != 'Bearer':
                    return JsonResponse({'error': 'Invalid token prefix'}, status=status.HTTP_401_UNAUTHORIZED)
                try:
                    access_token = AccessToken(token)
                    user_id = access_token.payload['user_id']
                    user = User.objects.get(pk=user_id)
                    username = user.username
                    if user.role in allowed_roles:
                        return view_function(request, *args, **kwargs)
                    else:
                        return JsonResponse({'error': 'PermissionDenied'}, status=status.HTTP_401_UNAUTHORIZED)
                except Exception as e:
                    return JsonResponse({'error': 'Invalid or expired token'}, status=status.HTTP_401_UNAUTHORIZED)
            elif user.is_authenticated:
                username = request.user.username
                if not user.is_blocked:
                    if user.role in allowed_roles:
                        return view_function(request, *args, **kwargs)
                    else:
                        # raise error 403
                        return JsonResponse({'error': 'PermissionDenied'}, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    auth.logout(request)
                    return HttpResponse('Your account is blocked. Please contact admin')
            else:
                return redirect('frontend:login')
        return wrap
    return decorator
