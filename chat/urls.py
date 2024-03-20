from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    # auth
    path('register/', views.RegisterView.as_view(), name="register"),
    path('login/', views.LoginView.as_view(), name="login"),
    path('logout/', views.logout_view, name="logout"),

    # profile
    path('create-profile/', views.CreateProfile.as_view(), name="create-profile"),
    path('update-profile/', views.UpdateProfile.as_view(), name="update-profile"),

    # search
    path('search/', views.searchUsers, name="search-users"),
    path('search/handle-friend-request/<int:id>/', views.handleFriendRequest, name="friend-request"),

    path('pending/', views.pending, name="pending"),
    path('pending/decline-friend-request/<int:id>/', views.declineFriendRequest, name="decline-friend-request"),
    path('pending/accept-friend-request/<int:id>/', views.acceptFriendRequest, name="accept-friend-request"),

    # chat
    path('direct-message/<int:user>/', views.DirectMessageView.as_view(), name="direct-message"),
    path('getChat', views.getChat, name="getChat"),
    path('createChat', views.createChat, name="createChat"),
    path('message/requests', views.messageRequests, name="messageRequests"),
]