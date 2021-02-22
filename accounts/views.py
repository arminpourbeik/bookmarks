from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from bookmarks.common.decorators import ajax_required
from django.contrib.auth.models import User

from .forms import UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Contact


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            return render(request,
                          template_name='account/register_done.html',
                          context={'new_user': new_user, })
    else:
        form = UserRegistrationForm()
        return render(request,
                      template_name='account/register.html',
                      context={'form': form, })


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Error updating your profile.')
        return render(request,
                      template_name='account/dashboard.html')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
        return render(request,
                      template_name='account/edit.html',
                      context={'user_form': user_form, 'profile_form': profile_form, })


@login_required
def dashboard(request):
    return render(
        request,
        template_name='account/dashboard.html',
        context={'section': 'dashboard'}
    )


@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)
    return render(request,
                  template_name='account/user/list.html',
                  context={'section': 'people', 'users': users})


@login_required
def user_detail(request, username):
    user = get_object_or_404(User, is_active=True, username=username)
    return render(request,
                  template_name='account/user/detail.html',
                  context={'section': 'people', 'user': user})


@ajax_required
@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(
                    user_from=request.user,
                    user_to=user
                )
            else:
                Contact.objects.filter(user_from=request.user, user_to=user).delete()
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'error'})
