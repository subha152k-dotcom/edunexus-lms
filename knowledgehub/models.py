from django.db import models
from django.contrib.auth.models import User



class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="course_images/", null=True, blank=True)
    is_premium = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    

class Plan(models.Model):

    name = models.CharField(max_length=100)

    price = models.DecimalField(max_digits=8, decimal_places=2)

    duration_days = models.IntegerField()

    def __str__(self):

        return self.name    
    

class Subscription(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)

    start_date = models.DateTimeField(auto_now_add=True)

    end_date = models.DateTimeField()

    status = models.CharField(max_length=20, default="active")


class Payment(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=8, decimal_places=2)

    payment_date = models.DateTimeField(auto_now_add=True)        
    

class Lesson(models.Model):

    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    title = models.CharField(max_length=200)

    content = models.TextField()

    video = models.FileField(upload_to="course_videos/", null=True, blank=True)

    def __str__(self):
        return self.title    
    
class Enrollment(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    enrolled_at = models.DateTimeField(auto_now_add=True)    


class LessonProgress(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)

    completed = models.BooleanField(default=False)


class UserActivity(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    activity_type = models.CharField(max_length=100)

    description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.activity_type}"    
    

class Notification(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    is_read = models.BooleanField(default=False)

    

    def __str__(self):
        return f"{self.user.username} - Notification"   


class CourseRating(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    rating = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)    


class CourseReview(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True) 


class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=100)
    action_detail = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)



# ---------------- CHAT SYSTEM ----------------

class ChatRoom(models.Model):
    name = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to="chat_files/", null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} - {self.text}"


class UserStatus(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {'Online' if self.is_online else 'Offline'}"   






class SocialAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.CharField(max_length=50)  
    social_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.provider}"


class OTPLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email     