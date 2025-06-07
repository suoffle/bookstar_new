from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Feed, Like, Bookmark  # 또는 Post, Content 등 실제 모델명
from user.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from user.models import User, Follow
from django.utils.decorators import method_decorator

class Main(APIView):
    def get(self, request):
        email = request.session.get('email')
        feed_list = Feed.objects.all().order_by('-id')
        user = User.objects.filter(email=email).first() if email else None

        #추천 사용자
        #recommended_users=[]
        #if user:
        #    recommended_users=User.objects.exclude(id=user.id)[:5]

        mike = User.objects.get(user_id='Mike')
        sulley = User.objects.get(user_id='sulley')
        rose = User.objects.get(user_id='Rose')
        monsterinc = User.objects.get(user_id='MonsterINC')
        monsteruni = User.objects.get(user_id='MonsterUni')

        if user:
            for u in [mike, sulley, rose, monsterinc, monsteruni]:
                u.is_following = Follow.objects.filter(from_user=user, to_user=u).exists()
        else:
            for u in [mike, sulley, rose, monsterinc, monsteruni]:
                u.is_following = False

        for feed in feed_list:
            if email:
                feed.is_liked = Like.objects.filter(feed_id=feed.id, email=email, is_like=True).exists()
                is_marked = Bookmark.objects.filter(feed_id=feed.id, email=email, is_marked=True).exists()
                feed.is_marked = is_marked
            else:
                feed.is_marked = False
                feed.is_liked = False

        return render(request, 'bookstar/main.html', {
            'feed_list': feed_list,
            'user': user,
            'mike': mike,
            'sulley': sulley,
            'rose': rose,
            'monsterinc': monsterinc,
            'monsteruni': monsteruni,

        })

class ToggleLike(APIView):
    def post(self, request):
        feed_id = request.data.get('feed_id')
        favorite_text = request.data.get('favorite_text')
        email = request.session.get('email')

        if not (feed_id and email):
            return Response({'error': 'Invalid data'}, status=400)

        is_like = (favorite_text == 'favorite_border')

        like = Like.objects.filter(feed_id=feed_id, email=email).first()

        if like:
            like.is_like = is_like
            like.save()
        else:
            Like.objects.create(feed_id=feed_id, is_like=is_like, email=email)

        # 좋아요 수 갱신
        like_count = Like.objects.filter(feed_id=feed_id, is_like=True).count()
        Feed.objects.filter(id=feed_id).update(like_count=like_count)

        return Response({'like_count': like_count}, status=200)

class ToggleBookmark(APIView):
    def post(self, request):
        feed_id = request.data.get('feed_id')
        email = request.session.get('email')

        if not (feed_id and email):
            return Response({'error': 'Invalid data'}, status=400)

        # 북마크가 이미 존재하는지 확인
        bookmark = Bookmark.objects.filter(feed_id=feed_id, email=email).first()

        if bookmark:
            # is_marked 값을 반대로 토글
            bookmark.is_marked = not bookmark.is_marked
            bookmark.save()
        else:
            # 없으면 새로 생성 (북마크 ON 상태로)
            Bookmark.objects.create(feed_id=feed_id, email=email, is_marked=True)

        return Response({'message': 'Bookmark toggled successfully'}, status=200)

@method_decorator(csrf_exempt, name='dispatch')
class UploadFeed(APIView):
    def post(self, request):
        file = request.FILES['file']
        uuid_name = uuid4().hex
        save_path = os.path.join(MEDIA_ROOT, uuid_name)

        with open(save_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        content = request.data.get('content')
        image = uuid_name

        email = request.session.get('email')
        if not email:
            return Response(status=400, data={'message': '로그인이 필요합니다.'})

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(status=400, data={'message': '존재하지 않는 사용자입니다.'})

        Feed.objects.create(
            content=content,
            image=image,
            user=user,
            like_count=0
        )
        return Response(status=200)

def feed_search(request):
    query = request.GET.get('q', '')
    feeds = Feed.objects.filter(
        Q(content__icontains=query) | Q(user_id__icontains=query)
    ) if query else []

    return render(request, 'bookstar/search_result.html', {
        'query': query,
        'feeds': feeds
    })
