from django.contrib import admin
from .models import Post, Comment, Dish, Status, Order, DishHasOrder, Shift, UserOnShift


admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Dish)
admin.site.register(Status)
admin.site.register(Order)
admin.site.register(DishHasOrder)
admin.site.register(Shift)
admin.site.register(UserOnShift)