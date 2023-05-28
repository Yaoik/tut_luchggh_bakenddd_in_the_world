from rest_framework import serializers
from .models import Post, Comment, Dish, Order, DishHasOrder, Status, Shift, UserOnShift
from django.contrib.auth.models import User, Group
from datetime import datetime



class DishSerializer(serializers.ModelSerializer):

    class Meta:
        model = Dish
        fields = ['id', 'name', 'cost']

#cook = serializers.PrimaryKeyRelatedField(many=False, source='cook.username', default=None, read_only=True)
#statuss = serializers.PrimaryKeyRelatedField(many=False, read_only=True, source='statuss.name', default=6) 
class OrderSerializer(serializers.ModelSerializer):
    waiter = serializers.ReadOnlyField(source='waiter.username')
    dishs = serializers.PrimaryKeyRelatedField(many=True, read_only=True) 
    
    class Meta:
        model = Order
        fields = ['id', 'created', 'waiter', 'cook', 'statuss', 'dishs']
        depth = 0

class DishHasOrderSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    #dish = serializers.SlugRelatedField(many=False, read_only=True, slug_field='name') 
    #dish = serializers.HyperlinkedIdentityField(many=False, read_only=True, view_name='name')
    
    
    class Meta:
        model = DishHasOrder
        fields = ['id', 'order', 'dish', 'count']
        depth = 0



class PostSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    comments = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'body', 'owner', 'comments']
  

class UserSerializer(serializers.ModelSerializer):
    #posts = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    #comments = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    groups = serializers.SlugRelatedField(many=True, read_only=False, slug_field='name', queryset=Group.objects.all()) 
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'groups']
        

class CommentSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Comment
        fields = ['id', 'body', 'owner', 'post']


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'name']


class ShiftSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Shift
        fields = ['id', 'data_start', 'data_end']
        
    def get_now():
        queryset = Shift.objects.filter(data_start__lt=datetime.now())&Shift.objects.filter(data_end__gt=datetime.now())
        n = [ShiftSerializer(i).data for i in queryset]
        if len(n)>0:
            return n[0]
        return []
        
class UserOnShiftSerializer(serializers.ModelSerializer):
    #user = serializers.SlugRelatedField(many=False, read_only=True, slug_field='username') 
    shift = serializers.SlugRelatedField(many=False, read_only=True, slug_field='data_start') 
    
    class Meta:
        model = UserOnShift
        fields = ['id', 'user', 'shift']