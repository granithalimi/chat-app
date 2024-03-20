from django.contrib import admin
from .models import FriendRequest, DirectMessage, Profile

# Register your models here.
admin.site.register([FriendRequest, DirectMessage, Profile])