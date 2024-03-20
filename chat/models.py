from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, related_name="profile", on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    surname = models.CharField(max_length=20)
    email = models.CharField(max_length=250)
    note = models.CharField(max_length=250, null=True, blank=True)
    profile_pic = models.ImageField(null=True, blank=True, upload_to='profile_pics/')

class FriendRequest(models.Model):
    id = models.AutoField(primary_key=True)
    sender_id = models.ForeignKey(User, related_name="sender",on_delete=models.CASCADE)
    receiver_id = models.ForeignKey(User, related_name="receiver",on_delete=models.CASCADE)
    status = models.BooleanField(default=False)

class DirectMessage(models.Model):
    id = models.AutoField(primary_key=True)
    sender_id = models.ForeignKey(User, related_name="sender_msg",on_delete=models.CASCADE)
    receiver_id = models.ForeignKey(User, related_name="receiver_msg",on_delete=models.CASCADE)
    message = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)