from django.contrib import admin
from .models import Course
from .models import Course, Lesson
from .models import LessonProgress
from .models import Enrollment
from .models import Plan, Subscription, Payment
from .models import UserActivity
from .models import Notification
from .models import ChatRoom, Message, UserStatus

admin.site.register(Course)
admin.site.register(Lesson)
admin.site.register(LessonProgress)
admin.site.register(Enrollment)
admin.site.register(Plan)
admin.site.register(Subscription)
admin.site.register(Payment)
admin.site.register(UserActivity)
admin.site.register(Notification)
admin.site.register(ChatRoom)
admin.site.register(Message)
admin.site.register(UserStatus)