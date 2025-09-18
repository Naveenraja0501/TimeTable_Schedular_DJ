from django.urls import path,include
from django.contrib.auth.views import LogoutView
from .views import signup_view,login_view,details_view,generate_timetable,save_timetable_entry,get_timetable_content
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('',signup_view, name="signup"),
    path('login/',login_view, name="login"),
    path("details/", details_view, name="details"),
    path('logout/', LogoutView.as_view(next_page='login'), name="logout"),
    path('timetable/generate/', generate_timetable, name='generate_timetable'),

    #path('save-timetable-content/', save_timetable_content, name='save_timetable_content'),
    path('get-timetable-content/<int:timetable_id>/', get_timetable_content, name='get_timetable_content'),
    path('save_timetable_entry/', save_timetable_entry, name='save_timetable_entry'),

]
