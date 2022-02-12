from django.urls import path
from Hub import views

urlpatterns = [
    path('', views.index, name='home'),
    path('register1', views.register_step1, name='register1'),
    path('register2', views.register_step2, name='register2'),
    path('login', views.loginUser, name='login'),
    path('glogin', views.googleLogin, name='glogin'),
    path('role', views.role, name='role'),
    path('profile<str:af>', views.profile, name='profile'),
    path('logout', views.logoutUser, name='logout'),
    path('forgotpassword', views.forgotpassword, name='forgotpassword'),
    path('forgotpassword2', views.forgotpassword2, name='forgotpassword2'),
    path('changePassword', views.changePassword, name = 'changePassword'),
    path('editProfile', views.editProfile, name='editProfile'),
    path('location', views.location_eligibility, name="location"),
    path('category/<str:city>', views.category, name="category"),
    path('allfromCat/<str:cat>', views.allfromCat, name="allfromCat"),
    path('appointment/<str:pid>', views.appointment, name="appointment"),
    path('createAppointment/<str:city>', views.createAppointment, name="createAppointment"),
    path('pagination<str:bnum>', views.pagination, name="pagination"),
    path('blog/<str:pid>', views.blog, name='blog'),
    path('deletePost/<int:pid>', views.deletePost, name='deletePost'),
    path('editPost/<int:pid>', views.editPost, name='editPost'),
    path('addPost/<int:pid>', views.addPost, name='addPost'),
    path('changeStatus', views.changeStatus, name='changeStatus'), 
    path('reschedule/<int:flag>', views.rescheduleAppointment, name='reschedule'), 
    path('feedback/<int:ap_id>', views.feedbackForm, name='feedbackForm')
]