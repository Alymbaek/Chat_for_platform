# urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register-list'),
    path('login/', CustomLoginView.as_view(), name='login-list'),
    path('logout/', LogoutView.as_view(), name='logout-list'),

    path('group/<int:group_id>/remove_user/<int:user_id>/', RemoveUserFromGroupView.as_view(), name='remove_user_from_group'),

    path('user/', UserProfileList.as_view(), name='user_list'),
    path('user/<int:pk>/', GroupMemberRetrieve.as_view(), name='user_detail'),
    path('groups/', GroupListCreateView.as_view(), name='group-list-create'),
    path('groups/<int:pk>/', GroupDetailView.as_view(), name='group-detail'),
    path('group_members/', GroupMemberView.as_view(), name='group_member-list'),
    path('group_members/<int:pk>/', GroupMemberRetrieve.as_view(), name='group_member-detail'),
    path('messages/', MessageListCreateView.as_view(), name='message-list-create'),
    path('messages/<int:pk>/', MessageDetailView.as_view(), name='message-detail'),
]