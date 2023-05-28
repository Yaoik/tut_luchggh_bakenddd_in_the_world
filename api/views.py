from . import serializers
from .models import Post, Comment, Dish, Order, DishHasOrder, Status, Shift, UserOnShift
from .permisisions import IsOwnerOrReadOnly, IsAdminOrReadOnly, IsWaiterOrReadOnly, IsСookOrReadOnly
from rest_framework import generics, permissions
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from django.http import HttpResponse
from django.db.models.query import QuerySet
from rest_framework.decorators import api_view, renderer_classes, action, permission_classes as view_permission_classes
from rest_framework.request import Request
from rest_framework import status
from datetime import datetime, timedelta
import json
#@view_permission_classes([IsWaiterOrReadOnly])

def is_cook(user):
    return user.groups.filter(name__in=['Повар']).exists()

def is_waiter(user):
    return user.groups.filter(name__in=['Официант']).exists()

def is_admin(user):
    return user.groups.filter(name__in=['Админ']).exists()

class PostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = serializers.PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = serializers.PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
 
    
class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    def perform_create(self, serializer:serializers.UserSerializer):
        user = User.objects.create_user(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password'],
            )
        return Response(serializers.UserSerializer(user).data)
    
class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer   
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    def put(self, request:Request, *args, **kwargs):
        print(f'{request.data=}')
        print(f'{args=}')
        print(f'{kwargs=}')
        print(f'{User.objects.get(pk=kwargs["pk"])=}')
        user = User.objects.get(pk=kwargs['pk'])
        if request.data['password'] != '':
            user.set_password(request.data['password'])
        if request.data['username'] != '':
            user.username = request.data['username']
        if request.data['groups'] != '':
            user.groups.set([Group.objects.get(name=request.data['groups']).id])
        user.save()
        return Response(serializers.UserSerializer(user).data)
    
    
class CommentList(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]


class DishList(generics.ListCreateAPIView):
    queryset = Dish.objects.all()
    serializer_class = serializers.DishSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class DishDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Dish.objects.all()
    serializer_class = serializers.DishSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]



class OrderList(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = serializers.OrderSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsWaiterOrReadOnly]
    
    def perform_create(self, serializer:serializers.OrderSerializer):
        if serializer.is_valid():
            serializer.save(waiter=self.request.user, statuss=Status.objects.get(pk=1), cook=None)
            
    @api_view(['GET'])
    @renderer_classes([JSONRenderer])
    def get_gotovitsay(request:Request, *args, **kwargs):
        return Response([serializers.OrderSerializer(i).data for i in Order.objects.filter(statuss__in=[1,2,3])])
    
    @api_view(['GET'])
    @renderer_classes([JSONRenderer])
    def on_shift(request:Request, *args, **kwargs):
        n = serializers.ShiftSerializer.get_now()
        return Response([serializers.OrderSerializer(i).data for i in Order.objects.filter(created__range=(n["data_start"], n["data_end"]))])
    
class OrderDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = serializers.OrderSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsСookOrReadOnly|IsWaiterOrReadOnly]

    def put(self, request:Request, pk, format=None):
        order = self.get_object()
        serializer = serializers.OrderSerializer(order, data=request.data)
        if serializer.is_valid():
            if order.cook == '':
                if order.cook != request.data.get('cook', None):
                    if request.user.groups.filter(name__in=['Повар']).exists() and str(request.user.id) == request.data['cook']:
                        pass
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  
            else:
                request.data._mutable = True
                request.data['cook'] = order.cook
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class DishHasOrderList(generics.ListCreateAPIView):
    queryset = DishHasOrder.objects.all()
    serializer_class = serializers.DishHasOrderSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsWaiterOrReadOnly]
    
    def perform_create(self, serializer: serializers.DishHasOrderSerializer, *args, **kwargs):
        serializer.is_valid(raise_exception=True)
        queryset = DishHasOrder.objects.filter(order=self.kwargs['pk'], dish=serializer.validated_data.get('dish'))
        if queryset.count()>0:
            queryset.delete()
        serializer.save(order=Order.objects.get(pk=self.kwargs['pk']))
    #@action(detail=False, methods=['GET'])
    @api_view(['GET'])
    @renderer_classes([JSONRenderer])
    def id_list(request:Request, *args, **kwargs):
        queryset = DishHasOrder.objects.filter(order=kwargs['pk'])
        return Response([serializers.DishHasOrderSerializer(i).data for i in queryset])
    
class DishHasOrderDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = DishHasOrder.objects.all()
    serializer_class = serializers.DishHasOrderSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    def put(self, request:Request, pk, format=None):
        order = self.get_object()
        serializer = serializers.OrderSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    
class ShiftList(generics.ListCreateAPIView):
    queryset = Shift.objects.all()
    serializer_class = serializers.ShiftSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    def perform_create(self, serializer:serializers.UserOnShiftSerializer):
        if serializer.is_valid():
            print(f"{self.queryset.filter(data_start__range=(serializer.validated_data['data_start'], serializer.validated_data['data_end']))=}")
            print(f"{self.queryset.filter(data_end__range=(serializer.validated_data['data_start'], serializer.validated_data['data_end']))=}")
            print(f"{serializer.validated_data['data_start']<serializer.validated_data['data_end']=}")
            if not (self.queryset.filter(data_start__range=(serializer.validated_data['data_start'], serializer.validated_data['data_end'])) or self.queryset.filter(data_end__range=(serializer.validated_data['data_start'], serializer.validated_data['data_end'])) or serializer.validated_data['data_start']>=serializer.validated_data['data_end']):
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    @api_view(['GET'])
    @renderer_classes([JSONRenderer])
    def today(request:Request, *args, **kwargs):
        print(f'{Shift.objects.filter(data_start__lt=datetime.now())&Shift.objects.filter(data_end__gt=datetime.now())}')
        queryset = Shift.objects.filter(data_start__lt=datetime.now())&Shift.objects.filter(data_end__gt=datetime.now())
        return Response([serializers.ShiftSerializer(i).data for i in queryset])     
    
    
class ShiftDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Shift.objects.all()
    serializer_class = serializers.ShiftSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    def put(self, request:Request, pk, format=None):
        shift = self.get_object()
        serializer = serializers.ShiftSerializer(shift, data=request.data)
        if serializer.is_valid():
            if not (self.queryset.filter(data_start__range=(request.data['data_start'], request.data['data_end'])).exists() or self.queryset.filter(data_end__range=(request.data['data_start'], request.data['data_end'])).exists()):
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class UserOnShiftList(generics.ListCreateAPIView):
    queryset = UserOnShift.objects.all()
    serializer_class = serializers.UserOnShiftSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    def perform_create(self, serializer:serializers.UserOnShiftSerializer):
        print(f'{self.kwargs=}')
        if serializer.is_valid():
            serializer.save(shift=Shift.objects.get(pk=self.kwargs['pk']))
            
    @api_view(['GET'])
    @renderer_classes([JSONRenderer])
    def by_pk(request:Request, *args, **kwargs):
        queryset = UserOnShift.objects.filter(shift=Shift.objects.get(pk=kwargs['pk']))
        print(f'{queryset=}')
        return Response([serializers.UserOnShiftSerializer(i).data for i in queryset])   
    
class UserOnShiftDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserOnShift.objects.all()
    serializer_class = serializers.UserOnShiftSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]