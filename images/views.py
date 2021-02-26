import redis

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.http import HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.decorators.http import require_POST
from django.conf import settings

from actions.utils import create_action
from bookmarks.common.decorators import ajax_required
from .models import Image
from .forms import ImageCreateForm

# Connect to redis
r = redis.Redis(host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB)


@login_required
def image_create(request):
    if request.method == 'POST':
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_item = form.save(commit=False)
            new_item.user = request.user
            new_item.save()
            create_action(request.user, 'bookmarked image', new_item)
            messages.success(request, 'Image added successfully.')
            return redirect(new_item.get_absolute_url())
    else:
        form = ImageCreateForm(data=request.GET)

    return render(
        request,
        'images/image/create.html',
        context={'section': 'images',
                 'form': form}
    )


@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(object_list=images,
                          per_page=8)
    page = request.GET.get('page')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            return HttpResponse('')
        images = paginator.page(paginator.num_pages)
    if request.is_ajax():
        return render(request,
                      template_name='images/image/list_ajax.html',
                      context={'section': 'images', 'images': images})

    return render(request,
                  template_name='images/image/list.html',
                  context={'section': 'images', 'images': images})


@login_required
def image_detail(request, _id, slug):
    image = get_object_or_404(Image, id=_id, slug=slug)
    total_views = r.incr(f'image: {image.id}: views')  # object-type:id:field image:33:id
    r.zincrby('image_ranking', 1, image.id)
    return render(
        request,
        'images/image/detail.html',
        context={'section': 'images',
                 'image': image,
                 'total_views': total_views}
    )


@login_required
def image_ranking(request):
    # Get image ranking dict
    image_ranking_ = r.zrange('image_ranking', 0, -1, desc=True)[:10]
    image_ranking_ids = [int(id_) for id_ in image_ranking_]
    # Get most viewed images
    most_viewed = list(Image.objects.filter(id__in=image_ranking_ids))
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
    return render(request,
                  template_name='images/image/ranking.html',
                  context={'most_viewed': most_viewed})


@ajax_required
@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
                create_action(user=request.user, verb='likes', target=image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except:
            pass
        return JsonResponse({'status': 'error'})
