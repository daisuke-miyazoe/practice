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
  if request.method == "POST":

    # Groupのチェックを更新した時の処理
    # フォームの用意
    checkform = GroupCheckForm(request.user, request.post)
    # チェックされたGroup名をリストにまとめる
    glist = []
    for item in request.POST.getlist('groups'):
      glist.append(item)
    # Messageの取得
    messages = get_your_group_message(request.user, glist, page)

  # Getアクセス時の処理
  else:
    # フォームの用意
    checkform = GroupCheckForm(request.user)
    gps = Group.objects.filter(owner=request.user)
    glist = [public_group.title]
    for item in gps:
      glist.append(item.title)
    # メッセージの取得
    messages = get_your_group_message(request.user, glist, page)

  # 共通の処理
  params = {
    'login_user':request.user,
    'contents':messages,
    'check_form':checkform
  }
  return render(request, 'sns/index.html', params)

@login_required(login_url='/admin/login/')
def group(request):
  # 自分が登録したFriendを取得
  friend = Friend.objects.filter(owner=request.user)

  # POST送信時の
  if request.method == "POST":

    # Groupsメニュー選択時の処理
    sel_group = request.POST['groups']
    # Groupを取得
    gp = Group.objects.filter(owner=request.user) \
        .filter(title=sel_group).first()
    # Groupに含まれるFriendを取得
    fds = Friend.objects.filter(owner=request.user) \
        .filter(group=gp)
    # FriendのUserをリストにまとめる
    vlist = []
    for item in fds:
      vlist.append(item.user.username)
    # フォームの用意
    groupsform = GroupSelectForm(request.user, request.POST)
    friendform = FriendForm(request.user, \
              friends=friends, vals=vlist)

  # Friendsのチェック更新時の処理
  if request.POST['mode'] == '__friends_form__':
    # 選択したGroupの取得
    sel_group = request.POST['group']
    group_obj = Group.objects.filter(title=sel_group).first()
    print(group_obj)
    # チェックしたFriendsを取得
    sel_fds = request.POST.getlist('friends')
    # FriendsのUserを取得
    sel_users = User.objects.fiter(username__in=sel_fds)
    # Userのリストに含まれるユーザーが登録したFriendを取得
    fds = Friend.objects.filter(owner=request.user) \
        .filter(user__in=sel_users)
    # 全てのFriendにGroupを設定し保存する
    vlist = []
    for item in fds:
      item.group = group_obj
      item.save()
      vlist.append(item.user.username)
    # メッセージを設定
    message.success(request, ' チェックされたFriendを' + \
            sel_group + 'に登録しました。')
    # フォームの用意
    groupform = GroupSelectForm(request.user, \
            {'groups':sel_group})
    friendform = FriendsForm(request, \
            friends=friends, vals=vlist)
    
    # GETアクセス時の処理
    else:
      # フォームの用意
      groupsform = GroupSelectForm(request.user)
      friendsform = FriendsForm(request.user, friends=friends, vals=[])
      sel_group = '-'

    # 共通処理
    createform = CreateGroupForm()
    params = {
      'login_user':request.user,
      'groups_form':groupform,
      'friends_form':friendform,
      'create_form':createform,
      'group':sel_group,
    }
    return render(request, 'sns/groups.html', params)

# Friendの追加処理
@login_required(login_url='/admin/login/')
def add(request):
  # 追加するUserを取得
  add_name = request.GET('name')
  add_user = User.objects.filter(username=add_name).first()
  # Userが本人だった場合の処理
  if add_user == request.user:
    messages.info(request, '自分自身をFriendに追加することは\
            できません。')
            return redirect(to='/sns')
    
  # ここからFriendの登録処理
  frd = Friend()
  frd.owner = request.user
  frd.user = add_user
  frd.group = public_group
  frd.save()
  # メッセージを設定
  messages.success(request, add_user.username + '　を追加しました！\
      groupページに移動して、追加したFriendをメンバーに設定してください。')
  return redirect(to='/sns')

# グループの作成処理
@login_required(login_url='/admin/login/')
def creategroup(request):
  # Groupを作り、Userとtitleを設定して保存する
  gp = Group()
  gp.owner = request.user
  gp.title = request.user.username + 'の' + request.POST['group_name']
  gp.save()
  messages.info(request, '新しいグループを作成しました！')
  return redirect(to='/sns/groups')

# メッセージのポスト処理
@login_required(login_url='/admin/login/')
def post(request):
  # POST送信の処理
  if request.method == 'POST':
    # 送信内容の取得
    gr_name =request.POST['groups']
    content = request.POST['content']
    # Groupの取得
    group = Group.objects.filter(owner=request.user) \
            .filter(title=gr_name).first()
    if group == None:
      (pub_user, group) = get_public()
    # Messageを作成し設定して保存
    msg = Message()
    msg.owner = request.user
    msg.group = group
    msg.content = content
    msg.save()
    # メッセージを設定
    messages.success(request, '新しいメッセージを投稿しました！')
    return redirect(to='/sns')

  # GETアクセス時の処理
  else:
    form = PostForm(request.user)

  # 共通処理
  params = {
    'login_user':request.user,
    'form':form,
  }
  return render(request, 'sns/post.heml', params)

# 投稿をシェアする
@login_required(login_url='/admin/login/')
def share(request, share_id):
  # シェアするMessageの取得
  shere = Message.objects.get(id=share_id)
  print(share)
  # POST送信時の処理
  if request.method == 'POST':
    gr_name = request.post['group']
    content = request.post['content']
    # Groupの取得
    group = Group.objects.filter(owner=request.user) \
            .filter(title=gr_name).first()
    if group == None:
      (pub_user, group) = get_public()
    # メッセージを作成し、設定をして保存
    msg = Message()
    msg.owner = request.user
    msg.group = group
    msg.content = content
    msg.share_id = share.id
    msg.save()
    share_msg = msg.get_share()
    share_msg.share_count += 1
    share_msg.save()
    # メッサージを設定
    messages.success(request, 'メッセージをシェアしました！')
    return redirect(to='/sns')

  # 共通処理
  form = PostForm(request.user)
  params = {
    'login_user':request.user,
    'form':form,
    'share':share,
  }
  return render(request, 'sns/share.html', params)