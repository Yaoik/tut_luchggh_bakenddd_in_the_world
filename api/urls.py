from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('users/', views.UserList.as_view()),
    path('users/<int:pk>/', views.UserDetail.as_view()),
]

urlpatterns += [
    path('order/', views.OrderList.as_view()),
    path('orders/', views.OrderList.get_gotovitsay),
    path('order/<int:pk>/', views.OrderDetail.as_view()),
    path('order/<int:pk>/add_dish', views.DishHasOrderList.as_view()),
    path('order/<int:pk>/dishs', views.DishHasOrderList.id_list),
]

urlpatterns += [
    path('shift/', views.ShiftList.as_view()),
    path('shift/<int:pk>/', views.ShiftDetail.as_view()),
    path('shift/now/', views.ShiftList.today),
    path('shift/<int:pk>/users/', views.UserOnShiftList.by_pk),
    path('shift/<int:pk>/add_user/', views.UserOnShiftList.as_view()),
    path('shift/<int:pk>/edit', views.UserOnShiftDetail.as_view()), 
    path('shift/<int:pk>/orders', views.OrderList.on_shift), 
]


urlpatterns = format_suffix_patterns(urlpatterns)