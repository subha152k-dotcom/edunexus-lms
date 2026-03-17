from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from knowledgehub import views

from knowledgehub.views import (
    home, course_detail, my_courses, enroll_course, mark_completed,
    plans_page, my_notifications, recommended_courses,
    rate_course, add_review, download_certificate,
    analytics_dashboard, admin_dashboard,
)

urlpatterns = [

    path('admin/', admin.site.urls),

    path('', home),

    path("course/<int:id>/", course_detail),

    path("my-courses/", my_courses),

    path("enroll/<int:course_id>/", enroll_course),

    path("complete/<int:lesson_id>/", mark_completed),

    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),

    path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),

    path("plans/", plans_page),

    path("analytics/", analytics_dashboard),

    path("dashboard/", admin_dashboard),

    path("notifications/", my_notifications),

    path("rate/<int:course_id>/", rate_course),

    path("review/<int:course_id>/", add_review),

    path("certificate/<int:course_id>/", download_certificate),

    path("recommended/", recommended_courses),

    path("api/save-message/", views.save_message),

    path("api/upload-file/", views.upload_file),

    path("api/update-status/", views.update_status),

    path("chat/", views.chat_page),

    path("send-message/", views.send_message),

    path("get-messages/", views.get_messages)
    

  

    

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)