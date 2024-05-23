import random
from django.conf import settings
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from .serializers import TweetSerializer
from .forms import Tweetform
from .models import Tweet
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.permissions import IsAuthenticated
ALLOWED_HOSTS = settings.ALLOWED_HOSTS

# Create your views here.
def home_view(request, *args, **kwargs):
    return render(request, "pages/home.html", context={}, status=200)

@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def tweet_create_view(request, *args,**kwargs):
    serializer = TweetSerializer(data=request.POST)
    if serializer.is_valid(raise_exception=True):
        serializer.save(user=request.user)
        return Response(serializer.data,status=201)
    return Response({},status=400)


def tweet_create_view_pure_django(request, *args, **kwargs):
    user = request.user
    print(user)
    if not request.user.is_authenticated:
        user = None
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({},status=401)
        return redirect(settings.LOGIN_URL)
    form = Tweetform(request.POST or None)
    next_url = request.POST.get("next") or None
    if form.is_valid():
        obj = form.save(commit=False)
        # do other form related logic
        obj.user = user
        obj.save()
        if (request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'):
            return JsonResponse(obj.serialize(), status=201) # 201 == created items
        if next_url != None and url_has_allowed_host_and_scheme(next_url, ALLOWED_HOSTS):
            return redirect(next_url)
        form = Tweetform()
    if form.errors:
        if (request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'):
            return JsonResponse(form.errors, status=400)
    return render(request, 'components/form.html', context={"form": form})

@api_view(['GET'])
def tweet_list_view(request, *args, **kwargs):
    qs = Tweet.objects.all()
    serializer = TweetSerializer(qs,many=True)
    return Response(serializer.data,status=200)






def tweet_list_view_pure_django(request, *args, **kwargs):
    """
    REST API VIEW
    Consume by JavaScript or Swift/Java/iOS/Andriod
    return json data
    """
    qs = Tweet.objects.all()
    tweets_list = [x.serialize() for x in qs]
    data = {
        "isUser": False,
        "response": tweets_list
    }
    return JsonResponse(data)

@api_view(['GET'])
def tweet_detail_view(request,tweet_id,*args, **kwargs):
    obj = Tweet.objects.filter(id=tweet_id)
    if not obj.exists():
        return Response({},status=404)
    obj = obj.first()
    serializer = TweetSerializer(obj)
    return Response(serializer.data,status=200)


@api_view(['DELETE','POST'])
@permission_classes([IsAuthenticated])
def tweet_delete_view(request,tweet_id,*args, **kwargs):
    obj = Tweet.objects.filter(id=tweet_id)
    if not obj.exists():
        return Response({},status=404)
    obj = obj.filter(user=request.user)
    if not obj.exists():
        return Response({"message": "You cannot delete this tweet"},status=401)
    obj = obj.first()
    obj.delete()
    return Response({"message": "Tweet removed"},status=200)


def tweet_detail_view_pure_django(request, tweet_id, *args, **kwargs):
    """
    REST API VIEW
    Consume by JavaScript or Swift/Java/iOS/Andriod
    return json data
    """
    data = {
        "id": tweet_id,
    }
    status = 200
    try:
        obj = Tweet.objects.get(id=tweet_id)
        data['content'] = obj.content
    except:
        data['message'] = "Not found"
        status = 404
    return JsonResponse(data, status=status) # json.dumps content_type='application/json'