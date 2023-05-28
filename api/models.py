import django.contrib.auth.models
from django.db import models
from datetime import datetime, timedelta



class Post(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    body = models.TextField(blank=True, default='')
    owner = models.ForeignKey('auth.User', related_name='posts', on_delete=models.CASCADE)

    class Meta:
        ordering = ['created']
        

class Comment(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    body = models.TextField(blank=False)
    owner = models.ForeignKey('auth.User', related_name='comments', on_delete=models.CASCADE)
    post = models.ForeignKey('Post', related_name='comments', on_delete=models.CASCADE)

    class Meta:
        ordering = ['created']



class Status(models.Model):
    name = models.TextField(blank=False)


class Dish(models.Model):
    name = models.TextField(blank=False)
    cost = models.IntegerField()


class Order(models.Model):
    created = models.DateTimeField(auto_now_add=True, blank=False)
    waiter = models.ForeignKey('auth.User', related_name='waiter', on_delete=models.CASCADE, blank=False)
    cook = models.ForeignKey('auth.User', related_name='cook', on_delete=models.CASCADE, null=True)
    statuss = models.ForeignKey('Status', related_name='statuss', on_delete=models.CASCADE, default=1)


class DishHasOrder(models.Model):
    order = models.ForeignKey('Order', related_name='dishs', on_delete=models.CASCADE)
    dish = models.ForeignKey('Dish', related_name='dishs', on_delete=models.CASCADE)
    count = models.IntegerField(blank=True)


class Shift(models.Model):
    data_start = models.DateTimeField()
    data_end = models.DateTimeField()
    #user_on_shift = models.ManyToManyField('User')

class UserOnShift(models.Model):
    user = models.ForeignKey('auth.User', related_name='user', on_delete=models.CASCADE)
    shift = models.ForeignKey('Shift', related_name='shift', on_delete=models.CASCADE)
    
    
    
#@permission_required