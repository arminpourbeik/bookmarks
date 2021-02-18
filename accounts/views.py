from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import UserRegistrationForm, UserEditForm, ProfileEditForm


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
