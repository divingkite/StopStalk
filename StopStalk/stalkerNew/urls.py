from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.conf.urls import patterns, include
import django.contrib.auth

#for stalker

application_name = 'stalkerNew'

urlpatterns = [
              url(r'^logout/$', views.logout_page,name='logout'),
              url(r'^login/$',views.login,name='login' ),          # If user is not login it will redirect to login page
              url(r'^register/$', views.register,name="registration"),
              url(r'^home/$', views.home,name='home'),
              url( r'^refresh', views.update_info,name='refresh'), #to update information about all contacts.
              url( r'^friend_list/$' , views.list_ , name = 'friend_list'),    
              url(r'^profile/(?P<person_id>[0-9]+)/$', views.profile , name='profile'),  # view profile of a person both cc anf cf
              url( r'^expand_list/$' , views.expand_list , name = 'add_in_list'), # add a person in the list of friends
              url( r'^delete_list/(?P<person_id>[0-9]+)/$' , views.delete_contact , name = 'remove_from_list'), # remove a person in the list of friends
              
              url( r'^search_contest/$', views.search_contestwise ,name='contest_peformance' ),       #shows list of all contests.
              url( r'^contest_performance/$',views.SearchForThisContest,name='list_for_a_contest'),    #shows everyone performance in a contest
              url(r'^refresh/(?P<person_id>[0-9]+)/$', views.update_a_person_info , name='refresh_a_person'), #to update information of a particular contacts.
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


 
