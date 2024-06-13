from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, generics, filters
from rest_framework import pagination
from rest_framework.permissions import IsAuthenticated

from django_filters.rest_framework import DjangoFilterBackend

from django.contrib.auth import authenticate
from django.http.response import *
from django.http.request import *
from django.conf import settings
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.db.models import Q
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from .models import *
from .serializers import *
from .requests import *
from .mixins import *
from .sheets import *
from .filters import *
from .pagination import *


from operator import or_, not_, and_
import pandas as pd
from dateutil.relativedelta import relativedelta   

from rest_framework_simplejwt.tokens import RefreshToken


# tester
class Tester(APIView):
    def get(self, request):
        # myURL = "https://docs.google.com/spreadsheets/d/13FduNu5j0kNVUl2XGXbfiD1VPjQQr_ELXuL46G_Mzgk/edit#gid=1428591798"
        # pr = GoogleSheetProcessor(myURL, myURL)
        
        # print(pr.__str__())
        # # pr.get_episode()
        # pr.save_full_episode_series_sequence()
        
        return Response({
            "response": "Level 1 Working"
        })

# SHeet API

class EpisodeSheetApi(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request: HttpRequest):
        data = request.data
        
        serializer = SheetSerializer(data=data, context={
            # 'user': request.user
        })
        
        if serializer.is_valid():
            return ApiResponseMixin().structure(request, Response(data="Sheet Uploaded Successfully!", status=status.HTTP_200_OK), [])
        else:
            return ApiResponseMixin().structure(request, Response(data="Invalid Data!", status=status.HTTP_400_BAD_REQUEST), errors=serializer.errors)


# EPISODE APIS
class EpisodeListApi(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    
    serializer_class = EpisodeListSerializer
    
    pagination_class = EpisodePagination
    
    queryset = EpisodeModel.objects.all()
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']
    
    ordering_fields = ['-created_at']
    
     
    def get_queryset(self):
        
        current_user = self.request.user
        
        queryset =  super().get_queryset()
        
        filtered = queryset.filter(
            # user = current_user
            )
        return filtered
    
    def list(self, request, *args, **kwargs):
        
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
            
            
        response = None
        errors = []
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            response = Response(serializer.data)
           
            
        # return response
        return ApiResponseMixin().structure(request, response, errors, *args, **kwargs)

class EpisodeDetailApi(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, uid):
        episode_model = EpisodeModel.objects.filter(id = uid).first()
        if episode_model is None:
            return ApiResponseMixin().structure(request, Response(data="Episode Not Found!", status = 404), [])
        
        episode_serialized = EpisodeDetailSerializer(instance=episode_model).data
        
        return ApiResponseMixin().structure(request, Response(episode_serialized), [])

# CHAPTERS API
class ChapterListApi(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    
    serializer_class = ChapterListSerializer
    
    pagination_class = ChapterPagination
    
    queryset = ChapterModel.objects.all()
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']
    
    ordering_fields = ['chapter_number']
    
     
    def get_queryset(self):
        current_user = self.request.user
        
        queryset =  super().get_queryset()
        
        episode_id = self.kwargs['episode_id']
        filtered = queryset.filter(
            # user = current_user, 
            episode = episode_id)
        return filtered
    
    def list(self, request, *args, **kwargs):
        
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
            
            
        response = None
        errors = []
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            response = Response(serializer.data)
           
            
        # return response
        return ApiResponseMixin().structure(request, response, errors, *args, **kwargs)

class ChapterDetailApi(APIView):
    permission_classes = [IsAuthenticated]

    def verifier(self, episode_id, chapter_id):
        current_user = self.request.user

        episode_model = EpisodeModel.objects.filter(
            id=episode_id, 
            # user=current_user
        ).first()
        if episode_model is None:
            return {"data": "Episode Not Found!", "status": 404}

        chapter_model = ChapterModel.objects.filter(id = chapter_id, episode=episode_model).first()
        if chapter_model is None:
            return {"data": "Chapter Not Found!", "status": 404}
        
        return [episode_model, chapter_model]
    
    # reading chapter's detail info
    def get(self, request, episode_id, uid):
        verify = self.verifier(episode_id, uid)
        if type(verify) is dict:
            return ApiResponseMixin().structure(request, Response(**verify), [])

        episode_model = verify[0]
        chapter_model = verify[1]
        cs = ChapterDetailSerializer(instance=chapter_model)
        # return response
        return ApiResponseMixin().structure(request, Response(cs.data), [])

    # updating chapter's data
    def put(self, request, episode_id, uid):
        verify = self.verifier(episode_id, uid)
        if type(verify) is dict:
            return ApiResponseMixin().structure(request, Response(**verify), [])

        episode_model = verify[0]
        chapter_model = verify[1]

        cs = ChapterUpdateSerializer(data=request.data, context={
            'episode': episode_model,
            'chapter': chapter_model
        })
        if cs.is_valid():
            return ApiResponseMixin().structure(request, Response("Chapter Updated Successfully!"), [])
        else:
            return ApiResponseMixin().structure(request, Response(data="Invalid Data!", status=status.HTTP_400_BAD_REQUEST), cs.errors)


# AUTHENTICATION API

def get_user_token(user):
    token = RefreshToken.for_user(user)
    return {
        "access_token": str(token.access_token),
        "refresh_token": str(token)
    }

class UserRegistrationApi(APIView):
    def post(self, request: HttpRequest):
        data = request.data
        
        serializer = UserDetailSerializer(data=data)
        if serializer.is_valid():
            user = serializer.validated_data
            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password")
            
            serializer.save()
            user_model = authenticate(email=email, password=password)
            print(user_model)
            token = get_user_token(user_model)
            return ApiResponseMixin().structure(request, Response(data={
                    "token": token
                    }, status=status.HTTP_201_CREATED), [])
        else:
            return ApiResponseMixin().structure(request, Response(data="Invalid Data!", status=status.HTTP_400_BAD_REQUEST), errors=serializer.errors)

class UserLoginApi(APIView):
    def post(self, request: HttpRequest):
        data = request.data
        
        serializer = UserLoginSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password")
            print(email, password)
            
            user = authenticate(email = email, password=password)
            
            # databse level errors
            if user is not None:
                token = get_user_token(user)
                return ApiResponseMixin().structure(request, Response(data={
                    "token": token
                    }, status=status.HTTP_200_OK), [])
            else:
                return ApiResponseMixin().structure(request, Response(status=status.HTTP_400_BAD_REQUEST), errors={
                    "non_field_errors": [
                        "Email or Password is incorrect."
                    ]
                })
                
        else:
            return ApiResponseMixin().structure(request, Response(data={}, status=status.HTTP_400_BAD_REQUEST), errors=serializer.errors)

class UserProfileUpdateApi(APIView):
    
    permission_classes = [IsAuthenticated]

    def put(self, request: HttpRequest):
        data = request.data
        
        serializer = UserProfileSerializer(instance=request.user, data=data, partial=True)
        if serializer.is_valid():
            user = serializer.validated_data
            
            user_model = serializer.save()
            print(user_model)
            
            return ApiResponseMixin().structure(request, Response(data="User updated successfully!", status=status.HTTP_200_OK), [])
        else:
            return ApiResponseMixin().structure(request, Response(data="Invalid Data!", status=status.HTTP_400_BAD_REQUEST), errors=serializer.errors)

class UserPasswordChangeApi(APIView):
    
    permission_classes = [IsAuthenticated]

    def put(self, request: HttpRequest):
        data = request.data
        
        serializer = UserChangePasswordSerializer(instance=request.user, data=data)
        if serializer.is_valid():
            current_user = request.user
            password = serializer.validated_data.get("password")
            current_user.set_password(password)
            current_user.save()
            
            # user_model = serializer.save()
            print("Changed Password: ", current_user)
            
            return ApiResponseMixin().structure(request, Response(data="User password changed successfully!", status=status.HTTP_200_OK), [])
        else:
            return ApiResponseMixin().structure(request, Response(data="Invalid Data!", status=status.HTTP_400_BAD_REQUEST), errors=serializer.errors)

class UserPasswordForgotApi(APIView):
    
    def get(self, request: HttpRequest):
        data = request.data
        
        serializer = UserPasswordForgotSerializer(data=data)
        if serializer.is_valid():
            
            # user_model = serializer.save()
            # print("Changed Password: ", current_user)
            
            return ApiResponseMixin().structure(request, Response(data="Email sent successfully!", status=status.HTTP_200_OK), [])
        else:
            return ApiResponseMixin().structure(request, Response(data="Invalid Data!", status=status.HTTP_400_BAD_REQUEST), errors=serializer.errors)

class UserPasswordResetApi(APIView):
    
    def post(self, request: HttpRequest, uid, token):
        data = request.data
        
        serializer = UserPasswordResetSerializer(data=data, context={
            'uid': uid,
            'token': token
        })
        if serializer.is_valid():
            
            # user_model = serializer.save()
            # print("Changed Password: ", current_user)
            
            return ApiResponseMixin().structure(request, Response(data="Password has been reset successfully!", status=status.HTTP_200_OK), [])
        else:
            return ApiResponseMixin().structure(request, Response(data="Invalid Data!", status=status.HTTP_400_BAD_REQUEST), errors=serializer.errors)