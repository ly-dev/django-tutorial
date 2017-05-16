from django.conf.urls import url, include
from rest_framework import routers


from . import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

app_name = 'myshop'
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^login$', views.LoginView.as_view()),
    url(r'^sign-up$', views.SignUpView.as_view()),
    url(r'^supermarket/(?P<supermarket>\w{0,20})/products/$', views.ProductsView.as_view()),
]