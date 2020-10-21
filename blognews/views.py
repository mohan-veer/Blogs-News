from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.core.mail import EmailMessage
from blognews.models import User, NewsArticle
import re
import bcrypt
import requests
import json
import random

current_user = None
token = None

def login(request):
    return render(request, 'blognews/base.html')


def loginvalidate(request):
    global current_user
    # uname = request.POST.get('email', " ")
    # password = request.POST.get('password', " ")
    errors = User.objects.login_validator(request.POST)
    if len(errors) > 0:
        #print("In Erros")
        for key, value in errors.items():
            messages.error(request, value, extra_tags="login")
        return redirect(reverse('login'))
    else:
        user_matches = User.objects.filter(user_id=request.POST['email'])
        if len(user_matches) == 0:
            messages.error(request, 'Email not found, please register')
            return redirect(reverse('login'))
        else:
            if bcrypt.checkpw(request.POST['password'].encode(), user_matches[0].user_password.encode()):
                request.session['new_user_id'] = user_matches[0].user_id
                request.session['name'] = user_matches[0].user_fname
                request.session['logged_in'] = True
                current_user = user_matches[0].user_id
                return redirect('/success/')
            else:
                messages.error(request, 'Password is incorrect')
                return redirect(reverse('login'))


def logout(request):
    #print('the logout method is running')
    request.session.clear()
    request.session['logged_in'] = False
    return redirect(reverse('login'))

def success(request):
    #print('currently displaying the success page!')
    if request.session['logged_in'] != True:
        redirect(reverse('login'))
    else:
        news_url = 'http://newsapi.org/v2/top-headlines?sources=techcrunch&apiKey=39104155eede4068ae656e73c292b0f6'
        response = requests.get(news_url)
        json_response = json.loads(response.text)
        articles = json_response['articles']
        #("NUmber of Articles ", len(articles))
        params = {}
        for i, article in enumerate(articles):
            source = article['source']['name']
            author = article['author']
            title = article['title']
            description = article['description']
            url = article['url']
            imageUrl = article['urlToImage']
            publishedAt = article['publishedAt']
            content = article['content']
            matched_title = NewsArticle.objects.filter(title=title)
            if len(matched_title)==0:
                news = NewsArticle.objects.create(source=source, author=author, title=title, description=description,
                                                  url=url, urlToImg=imageUrl, publishedAt=publishedAt, content=content)
            elif matched_title[0].author == author:
                pass
            else:
                news = NewsArticle.objects.create(source=source, author=author, title=title, description=description,
                                                  url=url, urlToImg=imageUrl, publishedAt=publishedAt, content=content)
        all_rows = NewsArticle.objects.all()
        params = {'blogs': all_rows}



        return render(request, 'blognews/home.html', params)


def signup(request):
    return render(request, 'blognews/register.html')


def register(request):
    #print("The path is",request.get_full_path())
    errors = []
    flag= []
    fname = request.POST.get('first_name', " ")
    lname = request.POST.get('last_name', " ")
    email = request.POST.get('email', " ")
    password = request.POST.get("password", " ")
    if re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', password):
        pass
    else:
        flag.append(2)
    cpassword = request.POST.get("cpassword", " ")
    phoneno = request.POST.get('phonenumber', " ")
    if len(phoneno) != 10:
        flag.append(3)
    if cpassword != password:
        flag.append(4)

    urecord = User.objects.filter(user_id=email)
    if len(urecord)>0:
        flag.append(1)
    #print(flag)
    # if -1 in flag:
    #     messages.error(request, "Can't Create. User already exists.")
    #     return redirect('/signup/')
    # elif -2 in flag:
    #     messages.error(request, 'Password did not match the criteria')
    #     return redirect('/signup/')
    # elif -3 in flag:
    #     messages.error(request, 'Phone number must be of 10 digits. Please re-enter')
    #     return redirect('/signup/')
    # elif -4 in flag:
    #     messages.error(request, "Confirm-password and Password didn't match")
    #     return redirect('/signup/')
    full_message = ""
    for f in flag:
        if f == 1:
            full_message = "Can't Create. User already exists."
            break
        elif f == 2:
            full_message += 'Password did not match the criteria \n'
        elif f == 3:
            full_message += 'Phone number must be of 10 digits. \n'
        elif f == 4:
            full_message += 'Confirm-password and Password did not match \n'


    if len(flag)>0:
        messages.error(request, full_message)
        return redirect('/signup/')
    else:
        #print("inside")
        hashed = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt())
        decoded_hash = hashed.decode()
        user = User.objects.create(user_id=email, user_fname=fname, user_lname=lname, user_password=decoded_hash,
                                    user_phone=phoneno)
        messages.success(request, "Account Created")

        return redirect(reverse('login'))


def create(request):
    return render(request, 'blognews/createblog.html')


def savenews(request):
    global current_user;
    title = request.POST.get('title'," ")
    description = request.POST.get('description'," ")
    content = request.POST.get('content', " ")

    if len(title)==0 or len(description)==0 or len(content)==0:
        messages.error(request, "Fields shouldn't be empty")
        return redirect(reverse('create'))
    else:
        #print("the current author is ", current_user)
        author = current_user
        news_created = NewsArticle.objects.create(author=author, title=title, description=description, content=content)
        messages.success(request,"Blog Created")
        return redirect(reverse('create'))


def yourblogs(request):
    all_blogs = NewsArticle.objects.filter(author=current_user)
    context = {'blogs':all_blogs}
    return render(request, 'blognews/blogs.html', context)


def deleteblog(request):
    blog_id = request.POST.get('delete')
    #print("the found blog id is ", blog_id)
    NewsArticle.objects.filter(id=blog_id,author=current_user).delete()
    return redirect(reverse('yourblogs'))


def viewblog(request):
    blog_id = request.POST.get('reference')
    #print("the blog id is", blog_id)
    blog_info = NewsArticle.objects.filter(id=blog_id)
    #print("Trtying to send", blog_info)
    return render(request, 'blognews/viewblog.html', {'blog':blog_info[0]})


def forgot(request, newContext={}):
    context = {'usage':'enteremail'}
    context.update(newContext)
    return render(request, 'blognews/forgot.html', context)


def reset(request):
    global  token, current_user
    user_email = request.POST.get('user_email')
    user_record = User.objects.filter(user_id=user_email)
    if len(user_record)==0:
        messages.error(request, "User doesn't exist" )
        return redirect('forgot')
    else:
        current_user = user_record[0].user_id
        #print("THE CURRENT USER IS", current_user)
        subject = 'Password Reset'
        from_email = 'newsblogservice@gmail.com'
        token = random.randint(1000, 10000)
        message = "Please enter the given one time secret token to reset your password : "+str(token)
        msg = EmailMessage(subject, message, from_email, [user_email])
        msg.send()
        #print("THE RESULT OF SEND AMIL", msg)
        context = {
            'usage' : 'entertoken'
        }
        response = forgot(request, context)
        return response


def tokenVerification(request):
    global token
    entered_token = int(request.POST.get('token'))
    print("ENTERED TOKEN IS ", entered_token)
    print("GLOBAL TOKEN IS ",token)
    print("ENTERED TOKEN IS Type", type(entered_token))
    print("GLOBAL TOKEN IS Type", type(token))
    if entered_token == token:
        context = {
            'usage' : 'passwordReset'
        }
        response = forgot(request, context)
        return  response
    else:
        messages.error(request, "Invalid Token")
        return redirect('login')

def resetPassword(request):
    new_password = request.POST['password']
    confirm_password = request.POST['cpassword']
    # print("THE NEW PASSWORD", new_password)
    # print("THE NEW CONFIRM PASSWORD", confirm_password)
    if new_password != confirm_password:
        messages.error(request, "Confirm password and New Password are not same")
        return redirect('resetPassword')
    else:

        user_record = User.objects.get(user_id=current_user)
        hashed = bcrypt.hashpw(request.POST.get('password').encode(), bcrypt.gensalt())
        decoded_hash = hashed.decode()
        user_record.user_password = decoded_hash
        user_record.save()
        messages.success(request, "Password updated successfully")
        return redirect('login')



