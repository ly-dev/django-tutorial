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

import random

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

class ProductsView(APIView):
    def post(self, request, supermarket):
        result  = []
        template = {
            "id": 0,
            "name": "name",
            "supermarket": 0,
            "supermarket_name": "supermarket_name",
            "brand": "brand",
            "product_id": 0,
            "serving_size": "serving size",
            "size": "380g",
            "food_type": "food",
            "fat_100": 8.5,
            "sat_100": 4.6,
            "sugar_100": 3,
            "salt_100": 0.78,
            "fat_serving": 10.8,
            "sat_serving": 5.8,
            "sugar_serving": 3.8,
            "salt_serving": 0.98,
            "tl_fat": "Red",
            "tl_sat": "Amber",
            "tl_sugar": "Green",
            "tl_salt": "Amber",
            "owner": 1,
            "health_score": 0
        }

        trafficLights = ["Red", "Amber", "Green"]
        trafficTabs = ['tl_fat', 'tl_sat', 'tl_sugar', 'tl_salt']

        if (request.data):
            data = request.data

            for productId in data:
                product = template.copy()
                product['product_id']= str(productId)
                product['name'] = 'product_' + str(productId)
                product['supermarket_name'] = supermarket
                product['health_score'] = 0
                for tag in trafficTabs:
                    rdm = random.randint(0, len(trafficLights)-1)
                    product[tag] = trafficLights[rdm]
                    product['health_score']  =  product['health_score'] + 2^rdm

                result.append(product)

        return Response(result)

class ConfigureView(APIView):
    def post(self, request, supermarket):
        template = {
            #//////////////////// ASDA ////////////////////
            'asda': {
              'timers': {
                'process_pages': 2000
              },
              'pages': [
                {
                  'type': 'browse',
                  'url_pattern': '/(cat|dept|aisle|shelf|special-offers)/',
                  'timers': {
                    'process_products': 2000
                  },
                  'products': [
                    #// Potential in here to separate out different product lists, on the same page
                    #// e.g. recommended products etc...
                    {
                      'selector': 'div.listings div.product',
                      'id': {
                        'selector': 'a.addItemToTrolley',
                        'attribute': 'data-skuid'
                      },
                      'trafficLight': {
                        'template': 'traffic_light_list_page',
                        'selector': 'div.cartBground',
                        'position': 'before'
                      }
                    }
                  ]
                },
                {
                  'type': 'basket',
                  'url_pattern': '/trolley',
                  'timers': {
                    'process_products': 2000
                  },
                  'trolleySummary': {
                    'template': 'trolley_summary_page',
                    'selector': 'div#fullTrolley',
                    'position': 'before'
                  },
                  'products': [
                    {
                      'selector': 'div.full-trolley-table div.full-trolley-prod-listing',
                      'id': {
                        'selector': 'div.product>a',
                        'attribute': { 'name': 'href', 'pattern': '\\d+$' }
                      },
                      'trafficLight': {
                        'template': 'traffic_light_list_page',
                        'selector': 'div.fulltrolleyDetails',
                        'position': 'after'
                      },
                      'productResource': {
                        'name': {
                          'selector': 'div.productInformation span.productTitle>a>strong',
                          'text': True
                        },
                        'image_src': {
                          'selector': 'div.product>a>img',
                          'attribute': 'src'
                        },
                        'image_alt': {
                          'selector': 'div.product>a>img',
                          'attribute': 'alt'
                        },
                        'quantity': {
                          'selector': 'div.price-info div.quantity-col.qty-price div.qty-price> span.qtyTxt',
                          'text': True
                        }
                      }
                    }
                  ]
                },
                {
                  'type': 'detail',
                  'url_pattern': '/product/.*/\\d+$',
                  'timers': {
                    'process_products': 2000
                  },
                  'products': [
                    {
                      'selector': 'div#mainContainer',
                      'id': {
                        'url_pattern': '/\\d+$',
                        'id_pattern': '\\d+$'
                      },
                      'trafficLight': {
                        'template': 'traffic_light_detail_page',
                        'selector': 'div#itemDetails p.prod-btn-holder',
                        'position': 'before'
                      },
                      'productResource': {
                        'name': {
                          'selector': 'div#itemDetails>h1.prod-title',
                          'text': True
                        },
                        'image_src': {
                          'selector': 'div.s7staticimage>img',
                          'attribute': 'src'
                        },
                        'image_alt': {
                          'selector': 'div.s7staticimage>img',
                          'attribute': 'alt'
                        }
                      }
                    }
                  ]
                },
                {
                  'type': 'search',
                  'url_pattern': '/search/',
                  'timers': {
                    'process_products': 2000
                  },
                  'products': [
                    {
                      'selector': 'div.productListing div.product',
                      'id': {
                        'selector': 'a.addItemToTrolley',
                        'attribute': 'data-skuid'
                      },
                      'trafficLight': {
                        'template': 'traffic_light_list_page',
                        'selector': 'div.cartBground',
                        'position': 'before'
                      }
                    }
                  ]
                },
              ]
            },
            #//////////////////// MORRISONS & OCADO ////////////////////
            'morrisons': {
              'pages': [
                {
                  'type': 'browse',
                  'url_pattern': '/webshop/getCategories.do',
                  'timers': {
                    'process_products': 2000
                  },
                  'products': [
                    {
                      'selector': 'div#js-productPageFops ul.fops>li',
                      'id': {
                        'attribute': 'data-sku'
                      },
                      'trafficLight': {
                        'template': 'traffic_light_list_page',
                        'selector': 'div.fop-item div.fop-content',
                        'position': 'append'
                      }
                    }
                  ]
                },
                {
                  'type': 'basket',
                  'url_pattern': '/webshop/displaySmartBasket.do|/webshop/displayLoggedOutSmartBasket.do',
                  'timers': {
                    'process_products': 2000
                  },
                  'trolleySummary': {
                    'template': 'trolley_summary_page',
                    'selector': 'div#smartTrolley',
                    'position': 'before'
                  },
                  'products': [
                    {
                      'selector': 'div#smartTrolley ul li.pictureView',
                      'id': {
                        'attribute': {
                          'name': 'id',
                          'pattern': '\\d+$'
                        }
                      },
                      'trafficLight': {
                        'template': 'traffic_light_list_page',
                        'selector': 'div.pictureViewInfo',
                        'position': 'after'
                      },
                      'productResource': {
                        'name': {
                          'selector': 'a.productImageLink>img',
                          'attribute': 'alt'
                        },
                        'image_src': {
                          'selector': 'a.productImageLink>img',
                          'attribute': 'src'
                        },
                        'image_alt': {
                          'selector': 'a.productImageLink>img',
                          'attribute': 'alt'
                        },
                        'quantity': {
                          'selector': 'input[name=quantity]',
                          'attribute': 'value'
                        }
                      }
                    }
                  ]
                },
                {
                  'type': 'detail',
                  'selector': 'div#content div[itemtype="http://schema.org/Product"]',
                  'products': [
                    {
                      'selector': 'div#content div[itemtype="http://schema.org/Product"]',
                      'id': {
                        'selector': 'meta[itemprop=sku]',
                        'attribute': 'content'
                      },
                      'trafficLight': {
                        'template': 'traffic_light_detail_page',
                        'selector': 'div.productDescription',
                        'position': 'after'
                      },
                      'productResource': {
                        'name': {
                          'selector': 'h1.productTitle strong[itemprop=name]',
                          'text': True
                        },
                        'image_src': {
                          'selector': 'ul#galleryImages>li.active>a>img',
                          'attribute': 'src'
                        },
                        'image_alt': {
                          'selector': 'ul#galleryImages>li.active>a>img',
                          'attribute': 'alt'
                        }
                      }
                    }
                  ]
                },
                {
                  'type': 'search',
                  'url_pattern': '/webshop/getSearchProducts.do',
                  'timers': {
                    'process_products': 2000
                  },
                  'products': [
                    {
                      'selector': 'div#js-productPageFops ul.fops>li',
                      'id': {
                        'attribute': 'data-sku'
                      },
                      'trafficLight': {
                        'template': 'traffic_light_list_page',
                        'selector': 'div.fop-item div.fop-content',
                        'position': 'append'
                      }
                    }
                  ]
                },
              ]
            },
            #//////////////////// SAINSBURY'S ////////////////////
            'sainsburys': {
              'pages': [
                {
                  'type': 'browse',
                  'selector': 'body#shelfPage',
                  'products': [
                    {
                      'selector': 'ul.productLister>li',
                      'id': {
                        'selector': 'form.addToTrolleyForm input[name=SKU_ID]',
                        'attribute': 'value'
                      },
                      'trafficLight': {
                        'template': 'traffic_light_list_page',
                        'selector': 'div.productInfo',
                        'position': 'append'
                      }
                    }
                  ]
                },
                {
                  'type': 'basket',
                  'selector': 'body#fullTrolley',
                  'trolleySummary': {
                    'template': 'trolley_summary_page',
                    'selector': 'div.article>div.tableContainer',
                    'position': 'before'
                  },
                  'products': [
                    {
                      'selector': 'table.fullTrolley tbody>tr',
                      'id': {
                        'selector': 'td.productPrice>div.siteCatalystTag',
                        'text': True
                      },
                      'trafficLight': {
                        'template': 'traffic_light_list_page',
                        'selector': 'td.product div.productContainer',
                        'position': 'append'
                      },
                      'productResource': {
                        'name': {
                          'selector': 'td.product>div.productContainer>a',
                          'text': True
                        },
                        'image_src': {
                          'selector': 'td.product>div.productContainer>a>img',
                          'attribute': 'src'
                        },
                        'image_alt': {
                          'selector': 'td.product>div.productContainer>a',
                          'text': True
                        },
                        'quantity': {
                          'selector': 'td.quantity>ul>li.inTrolley',
                          'text': True
                        }
                      }
                    }
                  ]
                },
                {
                  'type': 'detail',
                  'selector': 'body#productDetails',
                  'products': [
                    {
                      'selector': 'div.productContent',
                      'id': {
                        'selector': 'input[name=productId]',
                        'attribute': 'value'
                      },
                      'trafficLight': {
                        'template': 'traffic_light_detail_page',
                        'selector': 'div.productTitleDescriptionContainer',
                        'position': 'append'
                      },
                      'productResource': {
                        'name': {
                          'selector': 'div.productTitleDescriptionContainer>h1',
                          'text': True
                        },
                        'image_src': {
                          'selector': 'div#productImageHolder>img',
                          'attribute': 'src'
                        },
                        'image_alt': {
                          'selector': 'div#productImageHolder>img',
                          'attribute': 'alt'
                        }
                      }
                    }
                  ]
                },
                {
                  'type': 'search',
                  'selector': 'body#searchResultsPage',
                  'products': [
                    {
                      'selector': 'ul.productLister>li',
                      'id': {
                        'selector': 'form.addToTrolleyForm input[name=productId]',
                        'attribute': 'value'
                      },
                      'trafficLight': {
                        'template': 'traffic_light_list_page',
                        'selector': 'div.productInfo',
                        'position': 'append'
                      }
                    }
                  ]
                },
              ]
            },
            #//////////////////// TESCO ////////////////////
            'tesco': {
              'timers': {
                'process_pages': 2000
              },
              'pages': [
                {
                  'type': 'browse',
                  'url_pattern': '/shop',
                  'timers': {
                    'process_products': 2000
                  },
                  'products': [
                    {
                      'selector': 'ul.product-list>li.product-list--list-item',
                      'id': {
                        'selector': 'div[data-auto-id]',
                        'attribute': 'data-auto-id'
                      },
                      'trafficLight': {
                        'template': 'traffic_light_list_page',
                        'selector': 'div.product-details--wrapper',
                        'position': 'after'
                      }
                    }
                  ]
                },
                {
                  'type': 'basket',
                  'url_pattern': '/trolley',
                  'timers': {
                    'process_products': 2000
                  },
                  'trolleySummary': {
                    'template': 'trolley_summary_page',
                    'selector': 'ul[data-auto="product-list"]',
                    'position': 'before'
                  },
                  'products': [
                    {
                      'selector': 'ul[data-auto="product-list"]>li.product-list--list-item',
                      'id': {
                        'selector': 'a.product-image-wrapper',
                        'attribute': {
                            'name': 'href',
                            'pattern': '\\d+$'
                        }
                      },
                      'trafficLight': {
                        'template': 'traffic_light_list_page',
                        'selector': 'div.product-details--content',
                        'position': 'append'
                      },
                      'productResource': {
                        'name': {
                          'selector': 'div.product-details--content>a.product-tile--title',
                          'text': True
                        },
                        'image_src': {
                          'selector': 'div.product-image__container>img',
                          'attribute': 'src'
                        },
                        'image_alt': {
                          'selector': 'div.product-image__container>img',
                          'attribute': 'alt'
                        },
                        'quantity': {
                          'selector': 'div.inputControl-wrapper>input.product-input',
                          'attribute': 'value'
                        }
                      }
                    }
                  ]
                },
                {
                  'type': 'detail',
                  'url_pattern': '/products/\\d+$',
                  'timers': {
                    'process_products': 2000
                  },
                  'products': [
                    {
                      'selector': 'div.grocery-product:first-child',
                      'id': {
                        'url_pattern': '/\\d+$',
                        'id_pattern': '\\d+$'
                      },
                      'trafficLight': {
                        'template': 'traffic_light_detail_page',
                        'selector': 'body.controls--unit-toggle',
                        'position': 'before'
                      },
                      'productResource': {
                        'name': {
                          'selector': 'h1.product-title__h1',
                          'text': True
                        },
                        'image_src': {
                          'selector': 'div.product-image__container>img',
                          'attribute': 'src'
                        },
                        'image_alt': {
                          'selector': 'div.product-image__container>img',
                          'attribute': 'alt'
                        }
                      }
                    }
                  ]
                },
                {
                  'type': 'search',
                  'url_pattern': '/search',
                  'timers': {
                    'process_products': 2000
                  },
                  'products': [
                    {
                      'selector': 'ul.product-list>li.product-list--list-item',
                      'id': {
                        'selector': 'div[data-auto-id]',
                        'attribute': 'data-auto-id'
                      },
                      'trafficLight': {
                        'template': 'traffic_light_list_page',
                        'selector': 'div.product-details--wrapper',
                        'position': 'after'
                      }
                    }
                  ]
                },
              ]
            },
            #//////////////////// WAITROSE ////////////////////
            'waitrose': {
              'timers': {
                'process_pages': 2000
              },
              'pages': [
                {
                  'type': 'browse',
                  'url_pattern': '/ecom/shop/browse/groceries',
                  'timers': {
                    'process_products': 2000
                  },
                  'products': [
                    {
                      'selector': 'article[data-test="product-pod"]',
                      'id': {
                        'selector': 'header a',
                        'attribute': {
                          'name': 'href',
                          'pattern': '\\d+-\\d+-\\d+$'
                        }
                      },
                      'trafficLight': {
                        'template': 'traffic_light_list_page',
                        'selector': 'section:first-child',
                        'position': 'append'
                      }
                    }
                  ]
                },
                {
                  'type': 'basket',
                  'url_pattern': '/ecom/shop/trolley',
                  'timers': {
                    'process_products': 2000
                  },
                  'trolleySummary': {
                    'template': 'trolley_summary_page',
                    'selector': 'main>div>div:nth-child(2) button[data-test="empty-trolley"]',
                    'position': 'after'
                  },
                  'products': [
                    {
                      'selector': 'section[data-test="grouped-section"] ul li',
                      'id': {
                        'selector': 'section a[data-test="link-pdp"]',
                        'attribute': {
                          'name': 'href',
                          'pattern': '\\d+-\\d+-\\d+$'
                        }
                      },
                      'trafficLight': {
                        'template': 'traffic_light_list_page',
                        'selector': 'section:nth-child(3)',
                        'position': 'append'
                      },
                      'productResource': {
                        'name': {
                          'selector': 'section a[data-test="link-pdp-title"]',
                          'text': True
                        },
                        'image_src': {
                          'selector': 'section a[data-test="link-pdp"]>img',
                          'attribute': 'src'
                        },
                        'image_alt': {
                          'selector': 'section a[data-test="link-pdp"]>img',
                          'attribute': 'alt'
                        },
                        'quantity': {
                          'selector': 'section:nth-child(2)>div',
                          'text': {
                            'pattern': '\\d+'
                          }
                        }
                      }
                    }
                  ]
                },
                {
                  'type': 'detail',
                  'url_pattern': '/ecom/products/.+/\\d+-\\d+-\\d+$',
                  'products': [
                    {
                      'selector': 'div#content',
                      'id': {
                        'url_pattern': '/\\d+-\\d+-\\d+$',
                        'id_pattern': '\\d+-\\d+-\\d+$'
                      },
                      'trafficLight': {
                        'template': 'traffic_light_detail_page',
                        'position': {
                            'css': {
                                'position': 'absolute',
                                'top': '320px',
                                'right': '120px',
                            }
                        }
                      },
                      'productResource': {
                        'name': {
                          'selector': 'h1#productName span[data-test="product-name"]',
                          'text': True
                        },
                        'image_src': {
                          'selector': 'section#productImage picture img',
                          'attribute': 'src'
                        },
                        'image_alt': {
                          'selector': 'section#productImage picture img',
                          'attribute': 'alt'
                        }
                      }
                    }
                  ]
                },
                {
                  'type': 'search',
                  'url_pattern': '/shop/search',
                  'timers': {
                    'process_products': 2000
                  },
                  'products': [
                    {
                      'selector': 'article[data-test="product-pod"]',
                      'id': {
                        'selector': 'header a',
                        'attribute': {
                          'name': 'href',
                          'pattern': '\\d+-\\d+-\\d+$'
                        }
                      },
                      'trafficLight': {
                        'template': 'traffic_light_list_page',
                        'selector': 'section:first-child',
                        'position': 'append'
                      }
                    }
                  ]
                },
              ]
            }
          }
        
        template['ocado'] = template ['morrisons']
        
        result = template[supermarket]
        
        return Response(result);
    
class AuthSampleView(APIView):
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
