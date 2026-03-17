from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Sum, Count
from .models import CourseRating, CourseReview
from django.db.models import Avg
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from .models import ActivityLog
from django.core.mail import send_mail
from .models import ChatRoom, Message
from .models import UserStatus

from .models import (
    Course,
    Lesson,
    Enrollment,
    LessonProgress,
    Subscription,
    Payment,
    UserActivity,
    Notification
)


def analytics_dashboard(request):

    total_users = User.objects.count()
    total_courses = Course.objects.count()
    total_enrollments = Enrollment.objects.count()
    completed_courses = LessonProgress.objects.filter(
    completed=True
).count()
    total_revenue = Payment.objects.aggregate(
        total=Sum("amount")
    )["total"] or 0
    total_messages = Message.objects.count()
    most_active_user = Message.objects.values("sender__username") \
        .annotate(total=Count("id")) \
        .order_by("-total") \
        .first()
    
    messages_per_day = Message.objects.extra(
        select={'day': "date(timestamp)"}
    ).values('day').annotate(total=Count('id')).order_by('day')

    data = {
        "total_users": total_users,
        "total_courses": total_courses,
        "total_enrollments": total_enrollments,
        "total_revenue": total_revenue,
        "completed_courses": completed_courses,
         "total_messages": total_messages,
        "most_active_user": most_active_user,
        "messages_per_day": list(messages_per_day)
    }

    return JsonResponse(data)


def admin_dashboard(request):

    total_users = User.objects.count()
    total_courses = Course.objects.count()
    total_enrollments = Enrollment.objects.count()
    

    total_revenue = Payment.objects.aggregate(
        total=Sum("amount")
    )["total"] or 0

    
    recent_activity = UserActivity.objects.order_by("-created_at")[:5]
    popular_course = Enrollment.objects.values("course__title") \
        .annotate(total=Count("id")) \
        .order_by("-total") \
        .first()

    context = {
        "users": total_users,
        "courses": total_courses,
        "enrollments": total_enrollments,
        "revenue": total_revenue,
        "popular_course": popular_course,
        "recent_activity": recent_activity,
        
    }

    return render(request, "dashboard.html", context)


# ---------------- HOME PAGE ----------------

def home(request):

    query = request.GET.get("search")

    if query:
        courses = Course.objects.filter(title__icontains=query)
    else:
        courses = Course.objects.all()

    course_data = []

    for course in courses:

        total_lessons = Lesson.objects.filter(course=course).count()
        progress = 0

        if request.user.is_authenticated:

            completed = LessonProgress.objects.filter(
                user=request.user,
                lesson__course=course,
                completed=True
            ).count()

            if total_lessons > 0:
                progress = int((completed / total_lessons) * 100)

        course_data.append({
            "course": course,
            "progress": progress
        })

    

    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
    else:
        unread_count = 0

    return render(request, "index.html", {
        "course_data": course_data,
        "unread_count": unread_count
    })
# ---------------- COURSE DETAIL ----------------

@login_required
def course_detail(request, id):

    course = get_object_or_404(Course, id=id)

    lessons = Lesson.objects.filter(course=course)

    total_lessons = lessons.count()

    completed = LessonProgress.objects.filter(
        user=request.user,
        lesson__course=course,
        completed=True
    ).count()

    avg_rating = CourseRating.objects.filter(
        course=course
    ).aggregate(avg=Avg("rating"))["avg"]

    progress = 0

    if total_lessons > 0:
        progress = int((completed / total_lessons) * 100)

    is_enrolled = Enrollment.objects.filter(
        user=request.user,
        course=course
    ).exists()

    completed_lessons = LessonProgress.objects.filter(
        user=request.user,
        lesson__course=course,
        completed=True
    ).values_list("lesson_id", flat=True)


    reviews = CourseReview.objects.filter(course=course).order_by("-created_at")

    return render(request, "course_detail.html", {
        "course": course,
        "lessons": lessons,
        "progress": progress,
        "is_enrolled": is_enrolled,
        "completed_lessons": completed_lessons,
        "total_lessons": total_lessons,
        "avg_rating": avg_rating,
        "reviews": reviews
    })


# ---------------- MY COURSES ----------------
@login_required
def my_courses(request):

    enrollments = Enrollment.objects.filter(user=request.user).select_related("course").distinct()

    courses = [en.course for en in enrollments]

    # ---- Progress Calculation ----

    course_data = []

    for en in enrollments:

        course = en.course

        total_lessons = Lesson.objects.filter(course=course).count()

        completed = LessonProgress.objects.filter(
            user=request.user,
            lesson__course=course,
            completed=True
        ).count()

        progress = 0

        if total_lessons > 0:
            progress = int((completed / total_lessons) * 100)

        course_data.append({
            "course": course,
            "progress": progress
        })

    # ---- Recommended Courses ----

    recommended_courses = Course.objects.exclude(
        id__in=[en.course.id for en in enrollments]
    )[:3]




    return render(request, "my_courses.html", {
        "courses": courses,
        "course_data": course_data,
        "recommended_courses": recommended_courses
    })




# ---------------- ENROLL COURSE ----------------

@login_required
def enroll_course(request, course_id):

    course = Course.objects.get(id=course_id)

    already = Enrollment.objects.filter(
        user=request.user,
        course=course
    ).exists()

    if not already:

        Enrollment.objects.create(
            user=request.user,
            course=course
        )

        UserActivity.objects.create(
            user=request.user,
            activity_type="Course Enroll",
            description=f"Enrolled in {course.title}"
        )

        Notification.objects.create(
            user=request.user,
            message=f"You enrolled in {course.title}"
        )

        send_mail(
            "Course Enrollment",
            f"You successfully enrolled in {course.title}",
            "subha152k@gmail.com.com",
            [request.user.email],
        )

    return redirect("/course/" + str(course_id) + "/")


# ---------------- MARK COMPLETED ----------------

@login_required
def mark_completed(request, lesson_id):

    lesson = Lesson.objects.get(id=lesson_id)

    LessonProgress.objects.update_or_create(
        user=request.user,
        lesson=lesson,
        defaults={"completed": True}
    )

    UserActivity.objects.create(
        user=request.user,
        activity_type="Lesson Completed",
        description=f"Completed lesson {lesson.title}"
    )

    Notification.objects.create(
        user=request.user,
        message=f"You completed lesson {lesson.title}"
    )

    return redirect("/course/" + str(lesson.course.id) + "/")


# ---------------- PLANS PAGE ----------------

def plans_page(request):

    subscribed = False

    if request.user.is_authenticated:
        subscribed = Subscription.objects.filter(user=request.user).exists()

    return render(request, "plans.html", {
        "subscribed": subscribed
    })


# ---------------- NOTIFICATIONS ----------------

def my_notifications(request):

    notes = Notification.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(request, "notifications.html", {"notes": notes})


# ---------------- RECOMMENDED COURSES ----------------

def recommended_courses(request):

    if request.user.is_authenticated:
        courses = Course.objects.all()
    else:
        courses = Course.objects.filter(is_premium=False)

    return render(request, "recommended.html", {"courses": courses})



def rate_course(request, course_id):

    if request.method == "POST":

        rating_value = request.POST.get("rating")

        course = Course.objects.get(id=course_id)

        
        CourseRating.objects.filter(
            user=request.user,
            course=course
        ).delete()

        # create fresh rating
        
        CourseRating.objects.create(
            user=request.user,
            course=course,
            rating=rating_value
        )

    return redirect("/course/" + str(course_id) + "/")


def add_review(request, course_id):

    if request.method == "POST":

        comment = request.POST.get("comment")

        course = Course.objects.get(id=course_id)

        CourseReview.objects.create(
            user=request.user,
            course=course,
            comment=comment
        )

    return redirect("/course/" + str(course_id) + "/")



def download_certificate(request, course_id):

    from datetime import date

    course = Course.objects.get(id=course_id)

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename="certificate.pdf"'

    p = canvas.Canvas(response)

    width = 600
    height = 800

    # Outer Border
    p.setLineWidth(6)
    p.rect(30, 30, width-60, height-60)

    # Title
    p.setFont("Helvetica-Bold", 30)
    p.drawCentredString(300, 720, "CERTIFICATE")

    p.setFont("Helvetica-Bold", 24)
    p.drawCentredString(300, 690, "OF COMPLETION")

    # Subtitle
    p.setFont("Helvetica", 16)
    p.drawCentredString(300, 640, "This certificate is proudly presented to")

    # Username
    p.setFont("Helvetica-Bold", 22)
    p.drawCentredString(300, 600, request.user.username)

    # Course text
    p.setFont("Helvetica", 16)
    p.drawCentredString(300, 560, "For successfully completing the course")

    # Course name
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(300, 530, course.title)

    # Date
    today = date.today().strftime("%d %B %Y")

    p.setFont("Helvetica", 14)
    p.drawCentredString(300, 480, f"Date: {today}")

    # Signature text
    p.setFont("Helvetica", 12)
    p.drawString(120, 420, "Instructor Signature")

    p.drawString(400, 420, "EduNexus")

    # Signature line
    p.line(100, 440, 220, 440)
    p.line(380, 440, 500, 440)

    # Footer
    p.setFont("Helvetica-Oblique", 12)
    p.drawCentredString(300, 350, "EduNexus Learning Platform")

    p.drawCentredString(300, 330, "Empowering Online Learning")

    p.save()

    return response


def notification_count(request):

    if request.user.is_authenticated:

        unread = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()

    else:
        unread = 0

    return {"unread_count": unread}



from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def save_message(request):
    if request.method == "POST":
        data = json.loads(request.body)

        user = User.objects.get(username=data["username"])
        room, _ = ChatRoom.objects.get_or_create(name=data["room"])

        Message.objects.create(
            sender=user,
            room=room,
            text=data.get("message", "")
        )

        Notification.objects.create(
    user=user,
    message=f"New message from {user.username}"
)

        return JsonResponse({"status": "saved"})
    

@csrf_exempt
def upload_file(request):
    if request.method == "POST":
        file = request.FILES.get("file")
        username = request.POST.get("username")

        user = User.objects.get(username=username)
        room, _ = ChatRoom.objects.get_or_create(name="global")

        Message.objects.create(
            sender=user,
            room=room,
            file=file
        )

        return JsonResponse({"status": "file uploaded"})
    

@csrf_exempt
def update_status(request):
    if request.method == "POST":
        data = json.loads(request.body)

        user = User.objects.get(username=data["username"])
        status, _ = UserStatus.objects.get_or_create(user=user)

        status.is_online = data["is_online"]
        status.save()

        return JsonResponse({"status": "updated"})  




def chat_page(request):
    return render(request, "chat.html")  



from django.http import JsonResponse

chat_messages = []

def send_message(request):
    if request.method == "POST":
        msg = request.POST.get("message")
        user = request.POST.get("user")

        chat_messages.append({
            "user": user,
            "message": msg
        })

        return JsonResponse({"status": "ok"})


def get_messages(request):
    return JsonResponse({"messages": chat_messages})


import requests

def attendance_page(request):
    records = []

    if request.method == "POST":
        status = request.POST.get("status")

        data = {
            "username": request.user.username,
            "course_id": 1,
            "status": status
        }

        requests.post("http://127.0.0.1:8000/attendance", json=data)

        records.append(data)

    return render(request, "attendance.html", {
        "records": records
    })

def assignment_page(request):
    assignments = []

    if request.method == "POST":
        data = {
            "title": request.POST.get("title"),
            "desc": request.POST.get("desc")
        }

        requests.post("http://127.0.0.1:8000/assignment", json=data)

        assignments.append(data)  

    return render(request, "assignment.html", {
        "assignments": assignments
    })


def submit_page(request):
    submissions = []

    if request.method == "POST":
        data = {
            "username": request.user.username,
            "title": request.POST.get("title"),
            "content": request.POST.get("content")
        }

        requests.post("http://127.0.0.1:8000/submit", json=data)

        submissions.append(data) 

    return render(request, "submit.html", {
        "submissions": submissions
    })


def grade_page(request):
    graded = []

    if request.method == "POST":
        data = {
            "username": request.POST.get("username"),
            "title": request.POST.get("title"),
            "grade": request.POST.get("grade")
        }

        requests.post("http://127.0.0.1:8000/grade", params=data)

        graded.append(data)  

    return render(request, "grade.html", {
        "graded": graded
    })





