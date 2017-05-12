from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _

from rest_framework import viewsets
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated

from .serializers import GroupSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class LoginView(APIView):
    def post(self, request):
        data = request.data

        if ('email' in data) and ('password' in data):
            email = data['email']
            password = data['password']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = None

            if user and user.check_password(password):
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise serializers.ValidationError(msg, code='authorization')

                token, created = Token.objects.get_or_create(user=user)

                return Response({'email': email, 'token': token.key})
            else:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

class SignUpView(APIView):
    def post(self, request):
        data = request.data

        if ('email' in data) and ('password' in data):
            email = data['email']
            password = data['password']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = None

            if user:
                msg = _('User exists already.')
                raise serializers.ValidationError(msg, code='authorization')

            else:
                user = User.objects.create_user(username=email,
                                 email=email,
                                 password=password)
                token, created = Token.objects.get_or_create(user=user)

                return Response({'email': email, 'token': token.key})
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')
class ProductView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, supermarket):
        result = {
            'status': 'error',
            'message': 'Oops! Something goes wrong'
        }

        if (request.data):
            data = request.data
            user = request.user

            result['status'] = 'success'
            result['message'] = 'ok'
            result['data'] = {
                'username': user.username,
                'supermarket': supermarket,
                'ids': data
            }
        else:
            result['message'] = 'Invalid parameters'

        return Response(result)
