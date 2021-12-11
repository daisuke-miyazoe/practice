from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Friend
from .forms import FriendForm

def __new_str__(self):
    result = ''
    for item in self:
        result += '<tr>'
        for k in item:
            result += '<td>' + str(k) + '=' + str(item[k]) + '</td>'
        result += '</tr>'
    return result

def index(request):
    data = Friend.objects.all().values('id', 'name', 'age')
    params = {
        'title': 'Hello',
        'data': data,
    }
    return render(request, 'hello/index.html', params)

def create(request):
    if (request.method == 'POST'):
        obj = Friend()
        friend = FriendForm(request.POST, instance=obj)
        friend.save()
        return redirect(to='/hello')
    params = {
        'title': 'Hello',
        'form': FriendForm(),
    }
    return render(request, 'hello/create.html', params)