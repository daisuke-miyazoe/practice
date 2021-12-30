from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from .models import Message, Friend, Group, Good
from .forms import GroupCheckForm, GroupSelectForm, \
    FriendsForm, CreateGroupForm, PostForm

# indexのビュー関数
@login_required(login_url='/admin/login/')
def index(request, page=1):
  # publicのuserを取得
  (public_user, public_group) = get_public()

  # POST送信時の