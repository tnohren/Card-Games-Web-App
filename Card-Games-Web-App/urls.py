"""
Definition of urls for CardGames.
"""
from datetime import datetime
from django.urls import path
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from app import forms, views


urlpatterns = [
    path('', views.home, name='home'),
    path('home/<str:ignore>', views.home2, name="home2"),
    path('about/', views.about, name = 'about'),
    path('login/',
         LoginView.as_view
         (
             template_name='app/login.html',
             authentication_form=forms.BootstrapAuthenticationForm,
             extra_context=
             {
                 'title': 'Log in',
                 'year' : datetime.now().year,
             }
         ),
         name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name = 'logout'),
    url(r'^signup/$', views.SignUp, name = "signup"),
    path('admin/', admin.site.urls),
    path('startgame/', views.StartGame, name = "startgame"),
    path('loadornewgame/<str:gameType>', views.LoadOrNewGame, name = "loadornewgame"),
    path('newgame/<str:gameType>', views.NewGame, name="newgame"),
    path('loadgame/<str:gameType>', views.LoadGame, name="loadgame"),
    path('playblackjack/<int:gameNumber>', views.PlayBlackjack, name="playblackjack"),
    path('hit/<int:gameNumber>', views.HandleHit, name="hit"),
    path('stay/<int:gameNumber>', views.HandleStay, name="stay"),
]
