from django.db import models
import re
from django.utils import timezone

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

# Create your models here.
class UserManager(models.Manager):
    def register_validator(self, postData):
        errors = {}
        # Validation Rules for First Name
        if len(postData['user_fname']) < 1:
            errors["first_name"] = "First name is required"
        elif len(postData['user_fname']) < 2:
            errors["first_name"] = "First name should be at least 2 characters"
        elif not postData['user_fname'].isalpha():
            errors["first_name"] = "First Name can only have letters"

        # Validation Rules for Last Name
        if len(postData['user_lname']) < 1:
            errors["last_name"] = "Last name is required"
        elif len(postData['user_lname']) < 2:
            errors["last_name"] = "Last name should be at least 2 characters"
        elif not postData['user_lname'].isalpha():
            errors["last_name"] = "Last name can only have letters"

        # Validation Rules for Email
        if len(postData['user_id']) < 1:
            errors["email"] = "Email is required"
        elif not EMAIL_REGEX.match(postData['email']):
            errors["email"] = "Invalid Email Address"
        if User.objects.filter(email=postData['email']):
            errors["email"] = "Sorry, email is already in use"

        # Validation Rules for Password
        if len(postData['user_password']) < 1:
            errors["password"] = "Password is required"
        elif len(postData['user_password']) < 8:
            errors["password"] = "Password should be at least 8 characters"

        # Validation Rules for Phone number
        if len(postData['user_phone']) < 1:
            errors["phonenumber"] = "Phone Number is required"
        elif len(postData['user_phone']) < 10 or len(postData['user_phone'])>10:
            errors["phonenumber"] = "Phone Number should have 10 digits"

        return errors


    def login_validator(self, postData):
        errors = {}
        if len(postData['email']) == 0:
            errors['email_log_empty'] = 'Please enter your email'
        if len(postData['password']) == 0:
            errors['password_log_empty'] = 'Please enter your password'
        if not EMAIL_REGEX.match(postData['email']):
            errors['email_log_invalid'] = "Please enter a valid email address"
        return errors



class User(models.Model):
    user_id = models.EmailField(max_length=100, null=False, blank=False)
    user_fname = models.CharField(max_length=100, null=False, blank=False)
    user_lname = models.CharField(max_length=100, null=False, blank=False)
    user_password = models.CharField(max_length=100, null=False, blank=False)
    user_phone = models.DecimalField(max_digits=100, decimal_places=0, null=False, blank=False)

    def __repr__(self):
        return f"<User: {self.user_id}  {self.user_fname} {self.user_lname} {self.user_password} {self.user_phone}>"

    objects = UserManager()


class NewsArticle(models.Model):
    source = models.CharField(max_length=400, null=True, blank=True)
    author = models.CharField(max_length=100, default="Anonymous", null=True, blank=True)
    title = models.CharField(max_length=300, null=True, blank=True)
    description = models.CharField(max_length=1000, null=True, blank=True)
    url = models.CharField(max_length=300, null=True, blank=True)
    urlToImg = models.CharField(max_length=800, null=True, blank=True)
    publishedAt = models.DateTimeField(default=timezone.now, null=True, blank=True)
    content = models.TextField(null=True, blank=True)

    # def __repr__(self):
    #     return f"<NewsArticle: {self.source}  {self.author} {self.title} {self.description} {self.url} {self.urlToImg} {self.publishedAt} {self.content}>"content