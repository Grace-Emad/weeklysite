from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django's built-in login/logout views (we supply our own login.html template)
    path('accounts/', include('django.contrib.auth.urls')),

    # our app's pages (activity list, enroll, score)
    path('', include('activities.urls')),
]
