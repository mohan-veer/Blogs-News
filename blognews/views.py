
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from blognews.models import User, NewsArticle
import re
import bcrypt
import requests
import json

current_user = None

def login(request):
    return render(request, 'blognews/base.html')


def loginvalidate(request):
    global current_user
    # uname = request.POST.get('email', " ")
    # password = request.POST.get('password', " ")
    errors = User.objects.login_validator(request.POST)
    if len(errors) > 0:
        print("In Erros")
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
    print('the logout method is running')
    request.session.clear()
    request.session['logged_in'] = False
    return redirect(reverse('login'))

def success(request):
    print('currently displaying the success page!')
    if request.session['logged_in'] != True:
        redirect(reverse('login'))
    else:
        news_url = 'http://newsapi.org/v2/top-headlines?sources=techcrunch&apiKey=39104155eede4068ae656e73c292b0f6'
        response = requests.get(news_url)
        json_response = json.loads(response.text)
        articles = json_response['articles']
        print("NUmber of Articles ", len(articles))
        count = 1
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
        for i,row in enumerate(all_rows):
            if count <= 9:
                params["title_" + str(count)] = all_rows[i].title
                params["des_" + str(count)] = all_rows[i].description
                params["fa_" + str(count)] = all_rows[i].url
                params["img_" + str(count)] = all_rows[i].urlToImg
                count += 1




        return render(request, 'blognews/home.html', params)


def signup(request):
    return render(request, 'blognews/register.html')


def register(request):
    print("The path is",request.get_full_path())
    errors = []
    flag= []
    fname = request.POST.get('first_name', " ")
    lname = request.POST.get('last_name', " ")
    email = request.POST.get('email', " ")
    password = request.POST.get("password", " ")
    if re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', password):
        pass
    else:
        flag.append(-1)

    address = request.POST.get("address", " ")
    phoneno = request.POST.get('phonenumber', " ")
    if len(phoneno)!=10:
        flag.append(-2)
    print("FULL NAME", fname+lname)
    print("EMAIL", email)
    print("PASSWORD", password)
    print("ADDRESS", address)
    print("PHONE", phoneno)

    params = {'title': "Password Invalid",'message': errors}

    print(flag)
    if -1 in flag:
        messages.error(request, 'Password did not match the criteria')
        return redirect('/signup/')
    elif -2 in flag:
        messages.error(request, 'Phone number must be of 10 digits. Please re-enter')
        return redirect('/signup/')
    else:
        print("inside")
        hashed = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt())
        decoded_hash = hashed.decode()
        user = User.objects.create(user_id=email, user_fname=fname, user_lname=lname, user_password=decoded_hash,
                                   user_address=address, user_phone=phoneno)

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
        print("the current author is ", current_user)
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
    print("the found blog id is ", blog_id)
    NewsArticle.objects.filter(id=blog_id,author=current_user).delete()
    return redirect(reverse('yourblogs'))


def viewblog(request):
    blog_id = request.POST.get('reference')
    print("the blog id is", blog_id)
    blog_info = NewsArticle.objects.filter(id=blog_id,author=current_user)
    return  render(request, 'blognews/viewblog.html', {'blog':blog_info[0]})







