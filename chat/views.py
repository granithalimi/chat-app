# main
from django.shortcuts import render, HttpResponse, redirect
from django.views import View
from django.http import JsonResponse
# forms
from django.contrib.auth.forms import UserCreationForm
from .forms import ProfileForm
# models
from .models import Profile
from .models import FriendRequest
from .models import DirectMessage
from django.contrib.auth.models import User
from django.db.models import Q
# auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


# index
def index(request):
    if request.user.is_authenticated:
        users = Profile.objects.exclude(user=request.user)
        # get Friend Requests
        friend_requests = FriendRequest.objects.filter(receiver_id=request.user, status=True)
        # get users
        friends = []
        for i in friend_requests:
            friends.append(i.sender_id)
            
        messages = DirectMessage.objects.filter(Q(sender_id=request.user) | Q(receiver_id=request.user)).order_by('created_at')
        get_direct_messages = []
        for msg in messages:
            get_direct_messages.append(msg.receiver_id)

        direct_message_profile = Profile.objects.filter(user__in=get_direct_messages).exclude(user=request.user)
        print(direct_message_profile)
        friends_profile = Profile.objects.filter(user__in=friends)
        my_profile = Profile.objects.filter(user=request.user).get()
        context = {
            "friends" : friends_profile,
            "direct_message_profile" : direct_message_profile,
            "my_profile" : my_profile,
            "id" : request.user.id
        }
        return render(request, 'index.html', context)
    else:
        return redirect('login')

# AUTH
class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('index')

        form = UserCreationForm()
        return render(request, "registration/register.html", {"form" : form})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('create-profile')
        else:
            return render(request, "registration/register.html", {"form" : form})
        
class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('index')

        return render(request, 'registration/login.html')
    
    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('index')
        else:
            return render(request, "registration/login.html", {'msg' : "Wrong credentials!!"})
        
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('login')
    else:
        return redirect('login')


# PROFILE
class CreateProfile(View):
    def get(self, request):
        if Profile.objects.filter(user=request.user):
            return redirect('index')

        form = ProfileForm()
        context = {
            "form" : form
        }
        return render(request, "profile/create_profile.html", context)
    
    def post(self, request):
        name = request.POST['name']
        surname = request.POST['surname']
        email = request.POST['email']
        note = request.POST['note']
        profile_pic = request.FILES.get('profile_pic')
        form = Profile(user=request.user, name=name, surname=surname, email=email, note=note, profile_pic=profile_pic)
        if form:
            form.save()
            return redirect('index')
        else:
            return render(request, "profile/create_profile.html")

class UpdateProfile(View):
    def get(self, request):
        if not Profile.objects.filter(user=request.user):
            return redirect('index')

        my_profile = Profile.objects.filter(user=request.user).get()
        form = ProfileForm(instance=my_profile)
        messages = DirectMessage.objects.filter(Q(sender_id=request.user) | Q(receiver_id=request.user)).order_by('created_at')
        get_direct_messages = []
        for msg in messages:
            get_direct_messages.append(msg.receiver_id)

        direct_message_profile = Profile.objects.filter(user__in=get_direct_messages).exclude(user=request.user)
        context = {
            "form" : form,
            "my_profile" : my_profile,
            "direct_message_profile" : direct_message_profile,
        }
        return render(request, "profile/update_profile.html", context)

    def post(self, request):
        name = request.POST['name']
        surname = request.POST['surname']
        email = request.POST['email']
        note = request.POST['note']
        profile_pic = request.FILES.get('profile_pic')
        Profile.objects.filter(user=request.user).delete()
        form = Profile(user=request.user, name=name, surname=surname, email=email, note=note, profile_pic=profile_pic)
        if form:
            form.save()
            my_profile = Profile.objects.filter(user=request.user).get()
            return redirect('index')
        else:
            print(form.errors.as_data())
            return render(request, "profile/update_profile.html", {"form" : form, "my_profile" : my_profile, "id" : id})


# SEARCH
def searchUsers(request):
    if request.method == "POST" and request.user.is_authenticated:
        users = Profile.objects.exclude(user=request.user)
        my_profile = Profile.objects.filter(user=request.user).get()
        # get search value
        search = request.POST['search']
        # get users from db
        searched_users = Profile.objects.exclude(user=request.user).filter(name__contains=search)

        messages = DirectMessage.objects.filter(Q(sender_id=request.user) | Q(receiver_id=request.user)).order_by('created_at')
        get_direct_messages = []
        for msg in messages:
            get_direct_messages.append(msg.receiver_id)

        direct_message_profile = Profile.objects.filter(user__in=get_direct_messages).exclude(user=request.user)
        context = {
            "searched_users" : searched_users,
            "direct_message_profile" : direct_message_profile,
            "my_profile" : my_profile,
            "id" : request.user.id
        }
        return render(request, 'searched_users.html', context)
    else:
        return redirect('index')

def handleFriendRequest(request, id):
    if request.user.is_authenticated:
        # get receiver user
        receiver_user = User.objects.filter(id=id).get()
        # check if the friend req. exists
        if FriendRequest.objects.filter(sender_id=request.user, receiver_id=receiver_user).exists():
            # delete if exists
            fq = FriendRequest.objects.filter(sender_id=request.user, receiver_id=receiver_user).get()
            fq.delete()
            return redirect('index')
        else:
            # create if not
            sent_request = FriendRequest(sender_id=request.user, receiver_id=receiver_user, status=False)
            if sent_request:
                sent_request.save()
                return redirect('index')
            else:
                users = Profile.objects.exclude(user=request.user)
                my_profile = Profile.objects.filter(user=request.user).get()
                context = {
                    "users" : users,
                    "my_profile" : my_profile,
                    "id" : request.user.id
                }
                return render(request, 'searched_users.html', context)
            

# PENDING
def pending(request):
    if request.user.is_authenticated:
        users = Profile.objects.exclude(user=request.user)
        my_profile = Profile.objects.filter(user=request.user).get()
        # get friend requests
        friend_requests = FriendRequest.objects.filter(receiver_id=request.user, status=False)
        # get pending users
        pending_users = []
        for i in friend_requests:
            pending_users.append(i.sender_id)
        # get pending users profiles
        pending_users_profiles = Profile.objects.filter(user__in=pending_users)

        messages = DirectMessage.objects.filter(Q(sender_id=request.user) | Q(receiver_id=request.user)).order_by('created_at')
        get_direct_messages = []
        for msg in messages:
            get_direct_messages.append(msg.receiver_id)

        direct_message_profile = Profile.objects.filter(user__in=get_direct_messages).exclude(user=request.user)
        
        context = {
            "direct_message_profile" : direct_message_profile,
            "pending_users_profiles" : pending_users_profiles,
            "my_profile" : my_profile,
            "id" : request.user.id
        }
        return render(request, "pending.html", context)
    
def declineFriendRequest(request, id):
    # get sender user
    sender = User.objects.get(id=id)
    # delete Friend Request
    fq = FriendRequest.objects.get(sender_id=sender, receiver_id=request.user, status=False).delete()
    return redirect('pending')

def acceptFriendRequest(request, id):
    # get sender user
    sender = User.objects.get(id=id)
    FriendRequest.objects.filter(sender_id=sender, receiver_id=request.user, status=False).delete()
    new_friend_request = FriendRequest(sender_id=sender, receiver_id=request.user, status=True)
    if new_friend_request:
        new_friend_request.save()
        return redirect('pending')

class DirectMessageView(View):
    def get(self, request, user):
        # my profile
        my_profile = Profile.objects.get(user=request.user)

        # user profile
        user_profile = Profile.objects.get(user=user)

        messages = DirectMessage.objects.filter(Q(sender_id=request.user) | Q(receiver_id=request.user)).order_by('created_at')
        get_direct_messages = []
        for msg in messages:
            get_direct_messages.append(msg.receiver_id)

        direct_message_profile = Profile.objects.filter(user__in=get_direct_messages).exclude(user=request.user)
        context = {
            "my_profile" : my_profile,
            "user_profile" : user_profile,
            "id" : request.user.id,
            "direct_message_profile" : direct_message_profile,
        }
        return render(request, "direct_message.html", context)

from django.forms.models import model_to_dict

def getChat(request):
    user_id = request.GET.get('user_id')
    user = request.GET.get('user')

    # filter messages
    messages = DirectMessage.objects.filter(Q(sender_id=request.user, receiver_id=user_id) | Q(sender_id=user_id, receiver_id=request.user)).order_by('created_at')

    # create a list of dicts
    cow = [model_to_dict(obj) for obj in messages]


    # append dict to list of dicts
    for obj_dict in cow:
        # prof_id = obj_dict.sender_id
        profile = Profile.objects.get(user=obj_dict['sender_id'])
        obj_dict.update({"name" : profile.name, "profile_pic" : str(profile.profile_pic)})

    # return json
    return JsonResponse({
        "messages" : cow,
    }, safe=False)

def createChat(request):
    if request.method == "POST":
        msg = request.POST["message"]
        sender = request.POST["sender_id"]
        receiver = request.POST.get("receiver_id")
        receiver2 = User.objects.get(id=receiver)

        new_chat = DirectMessage(sender_id=request.user, receiver_id=receiver2, message=msg)
        new_chat.save()
        users = User.objects.all()
        return JsonResponse({
            "users" : list(users.values())
        })
    
def messageRequests(request):
    my_profile = Profile.objects.get(user=request.user)
    messages = DirectMessage.objects.filter(Q(sender_id=request.user) | Q(receiver_id=request.user)).order_by('created_at')
    get_direct_messages = []
    for msg in messages:
        get_direct_messages.append(msg.receiver_id)
        
    # friends
    friend_requests = FriendRequest.objects.filter(receiver_id=request.user, status=True)
    # get users
    friends = []
    for i in friend_requests:
        friends.append(i.sender_id)

    request_messages = DirectMessage.objects.filter(receiver_id=request.user).exclude(sender_id__in=friends)
    get_request_messages = []
    for msg in request_messages:
        get_request_messages.append(msg.sender_id)

    request_message_profile = Profile.objects.filter(user__in=get_request_messages)
    direct_message_profile = Profile.objects.filter(user__in=get_direct_messages).exclude(user=request.user)
    context = {
        "my_profile" : my_profile,
        "id" : request.user.id,
        "direct_message_profile" : direct_message_profile,
        "request_message_profile" : request_message_profile,
    }
    return render(request, "request_message.html", context)