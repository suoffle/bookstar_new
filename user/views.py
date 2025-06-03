from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from .models import User, Follow
from content.models import Feed, Bookmark
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from uuid import uuid4
from config.settings import MEDIA_ROOT
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from django.contrib.auth import authenticate,login
import json
from django.http import JsonResponse
from django.contrib import messages
import os


def profile_view(request):
    user=request.user
    feeds=Feed.objects.filter(user=user).order_by('-created_at')

    bookmarked_feed_ids = Bookmark.objects.filter(email=user.email, is_marked=True).values_list('feed_id', flat=True)
    bookmarked_feeds = Feed.objects.filter(id__in=bookmarked_feed_ids).order_by('-created_at')

    #팔로우
    follower_count = Follow.objects.filter(to_user=user).count()
    following_count = Follow.objects.filter(from_user=user).count()
    return render(request, 'user/profile.html',{
        'user':user,
        'feeds':feeds,
        'bookmarked_feeds':bookmarked_feeds,
        'follower_count': follower_count,
        'following_count': following_count,
    })

@method_decorator(csrf_exempt, name='dispatch')
class UpdateProfileImage(APIView):
    def post(self, request):
        email = request.session.get('email')
        if not email:
            return Response({'error': '로그인이 필요합니다.'}, status=403)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': '사용자를 찾을 수 없습니다.'}, status=404)

        uploaded_file = request.FILES.get('profile_image')
        if not uploaded_file:
            return Response({'error': '이미지를 선택하세요.'}, status=400)

        ext = os.path.splitext(uploaded_file.name)[1]
        filename = f"{uuid4().hex}{ext}"
        save_path = os.path.join(MEDIA_ROOT, filename)

        with open(save_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        user.profile_image = filename
        user.save()

        return Response({'message': '프로필 이미지가 업데이트되었습니다.'}, status=200)

class Login(APIView):
    def get(self, request):
        return render(request, 'user/login.html')

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(status=400, data=dict(message='이메일과 비밀번호를 입력해주세요.'))

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)  # Django 세션에 사용자 등록
            request.session['email'] = user.email
            return Response(status=200, data=dict(message='로그인 성공'))
        else:
            return Response(status=401, data=dict(message='입력 정보가 잘못되었습니다.'))

class Join(APIView):
    def get(self, request):
        return render(request, 'user/join.html')

    def post(self, request):
        password=request.data.get('password')
        email=request.data.get('email')
        user_id=request.data.get('user_id')
        name=request.data.get('name')

        if User.objects.filter(email=email).exists():
            return Response(status=500, data=dict(message="이메일 주소가 이미 존재합니다."))
        elif User.objects.filter(user_id=user_id).exists():
            return Response(status=500, data=dict(message='사용자 이름 "'+user_id+'"이(가) 존재합니다.'))

        User.objects.create(password=make_password(password),
                            email=email,
                            user_id=user_id,
                            name=name)

        # UserPreference 생성
        from .models import UserPreference
        UserPreference.objects.create(user=User.objects.get(email=email))

        # 세션 저장 (자동 로그인)
        request.session['loginCheck'] = True
        request.session['email'] = email

        # 온보딩으로 리다이렉트
        return Response(status=200, data=dict(
            message="회원가입에 성공하였습니다. 취향을 설정해주세요.",
            redirect_to_onboarding=True
        ))

class Logout(APIView):
    def get(self, request):
        request.session.flush()  # 세션 초기화
        return redirect('/')  # 또는 로그인 페이지로 이동


class ToggleFollow(APIView):
    def post(self, request):
        email = request.session.get('email')
        to_user_id = request.data.get('to_user_id')

        if not email or not to_user_id:
            return Response({'error': '잘못된 요청'}, status=400)

        from_user = User.objects.get(email=email)
        to_user = User.objects.get(id=to_user_id)

        follow, created = Follow.objects.get_or_create(from_user=from_user, to_user=to_user)
        if not created:
            follow.delete()
            return Response({'message': '언팔로우 성공'})
        return Response({'message': '팔로우 성공'})


def onboarding_view(request):
    if not request.session.get('loginCheck'):
        messages.error(request, '로그인이 필요합니다.')
        return redirect('/user/login/')

    if request.method == 'GET':
        user_email = request.session.get('email')
        user = User.objects.filter(email=user_email).first()

        if not user:
            return redirect('/user/login/')

        from .models import UserPreference
        preference, created = UserPreference.objects.get_or_create(user=user)

        if preference.onboarding_completed:
            messages.info(request, '이미 취향 설정이 완료되었습니다.')
            return redirect('/')

        return render(request, 'user/onboarding.html')

    elif request.method == 'POST':
        try:
            user_email = request.session.get('email')
            user = User.objects.filter(email=user_email).first()

            if not user:
                return JsonResponse({'success': False, 'message': '사용자 정보를 찾을 수 없습니다.'})

            data = json.loads(request.body)
            from .models import UserPreference
            preference, created = UserPreference.objects.get_or_create(user=user)

            # 온보딩 데이터 저장
            preference.genres = data.get('genres', [])
            preference.goals = data.get('goals', [])
            preference.reading_time = data.get('readingTime', '')
            preference.reading_duration = data.get('readingDuration', '')
            preference.reading_complexity = data.get('readingComplexity', '')
            preference.favorite_books = data.get('favoriteBooks', [])
            preference.mood = data.get('mood', [])
            preference.onboarding_completed = True
            preference.save()

            return JsonResponse({
                'success': True,
                'message': '취향 설정이 완료되었습니다!',
                'redirect_url': '/'
            })

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'저장 중 오류가 발생했습니다: {str(e)}'})


def skip_onboarding_view(request):
    if not request.session.get('loginCheck'):
        return redirect('/user/login/')

    user_email = request.session.get('email')
    user = User.objects.filter(email=user_email).first()

    if user:
        from .models import UserPreference
        preference, created = UserPreference.objects.get_or_create(user=user)
        preference.onboarding_completed = True
        preference.save()
        messages.info(request, '나중에 설정에서 취향을 설정할 수 있습니다.')

    return redirect('/')