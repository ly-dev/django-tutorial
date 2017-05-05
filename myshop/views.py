from django.contrib.auth.models import User, Group
from rest_framework import viewsets
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
        result = {
            'status': 'error',
            'message': 'Oops! Something goes wrong'
        }

        if (request.data and request.data.get('username', None) and request.data.get('password', None)):
            username = request.data.get('username');
            user = User.objects.filter(username=username).first()
            if (user):
                password = request.data.get('password');
                if (user.check_password(password)):
                    token = Token.objects.get_or_create(user=user)
                    result['status'] = 'success'
                    result['message'] = 'ok'
                    result['data'] = {
                        'username': username,
                        'token': token.key,
                    }
                else:
                    result['message'] = 'Invalid password'
            else:
                result['message'] = 'User not found: ' + username
        else:
            result['message'] = 'Invalid parameters'

        return Response(result)

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
