import datetime
from rest_framework import permissions
from rest_framework.request import Request
from .views import UserOnShift, Shift

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.owner == request.user


class IsWaiterOrReadOnly(permissions.BasePermission):
        
    def has_object_permission(self, request:Request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.groups.filter(name__in=['Официант']).exists()


class IsСookOrReadOnly(permissions.BasePermission):
        
    def has_object_permission(self, request:Request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.groups.filter(name__in=['Повар']).exists()
    
    
class IsAdminOrReadOnly(permissions.BasePermission):
        
    def has_object_permission(self, request:Request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.groups.filter(name__in=['Админ']).exists()