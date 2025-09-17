from django.urls import path,include
from django.contrib.auth.views import LogoutView
from .views import home,signup_view,login_view,details_view,generate_timetable

urlpatterns = [
    #path('', home, name="home"),
    path('',signup_view, name="signup"),
    path('login/',login_view, name="login"),
    path("details/", details_view, name="details"),
    path('logout/', LogoutView.as_view(next_page='login'), name="logout"),
    path('timetable/generate/', generate_timetable, name='generate_timetable'),
    
]
