from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from blog.models import Post, Comment,Preference,Account
from django.utils import timezone
from blog.forms import PostForm, CommentForm,RegistrationForm, AccountAuthenticationForm, AccountUpdateForm
#Importing the generic Views
from django.views.generic import (TemplateView,ListView,
                                  DetailView,CreateView,
                                  UpdateView,DeleteView)

from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, authenticate, logout

#on calling /register this view will be called and a registrationform will be rendered to the browser
#if the request is get or if request is post check for validation of the form and login the registered
#user and redirect to home
def registration_view(request):
	context = {}
	if request.POST:
		form = RegistrationForm(request.POST)
		if form.is_valid():
			form.save()
			email = form.cleaned_data.get('email')
			raw_password = form.cleaned_data.get('password1')
			account = authenticate(email=email, password=raw_password)
			login(request, account)
			return redirect('/')
		else:
			context['registration_form'] = form

	else:
		form = RegistrationForm()
		context['registration_form'] = form
	return render(request, 'blog/register.html', context)


#this view handles the logout functionality
def logout_view(request):
	logout(request)
	return redirect('/')

#this view renders the login form if the request is get and for a post request
#authenticated the user and allow him to login
def login_view(request):
	context = {}
	user = request.user
	if user.is_authenticated:
		return redirect("/")
	if request.POST:
		form = AccountAuthenticationForm(request.POST)
		if form.is_valid():
			email = request.POST['email']
			password = request.POST['password']
			user = authenticate(email=email, password=password)

			if user:
				login(request, user)
				return redirect("/")

	else:
		form = AccountAuthenticationForm()

	context['login_form'] = form

	# print(form)
	return render(request, "blog/login.html", context)



#About page for the blog
class AboutView(TemplateView):
    template_name = 'about.html'

#This view lists all the posts in the posts model ,sorting them with their created date
# and the response is rendered in post_list.html template
class PostListView(ListView):
    model = Post

    def get_queryset(self):
        return Post.objects.filter(created_date__lte=timezone.now()).order_by('-created_date')


#This view gives details of the specific post and the response is rendered in the post_detail.html template
class PostDetailView(DetailView):
    model = Post

#This view is used to create a newpost by using postform and after the post is created redirects to postdetail view
class CreatePostView(LoginRequiredMixin,CreateView):
    login_url = '/login/'
    redirect_field_name = 'blog/post_detail.html'

    form_class = PostForm

    model = Post


#This view is used to edit the post created and redirects to post_detail view
class PostUpdateView(LoginRequiredMixin,UpdateView):
    login_url = '/login/'
    redirect_field_name = 'blog/post_detail.html'

    form_class = PostForm

    model = Post



#This view is used to delete the existing post and redirects to list of all posts
class PostDeleteView(LoginRequiredMixin,DeleteView):
    model = Post
    success_url = reverse_lazy('post_list')

#######################################
## Functions that require a pk match ##
#######################################


#This view is used to add a comment to a particular post
@login_required
def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/comment_form.html', {'form': form})

#This view keeps track of likes and dislikes for a particular post
@login_required
def postpreference(request, postid, userpreference):
        if request.method == "POST":
                eachpost= get_object_or_404(Post, id=postid)
                obj=''
                valueobj=''
                try:
                        obj= Preference.objects.get(user= request.user, post= eachpost)
                        valueobj= obj.value #value of userpreference
                        valueobj= int(valueobj)
                        userpreference= int(userpreference)
                        print('HI')
                        if valueobj != userpreference:
                                obj.delete()
                                upref= Preference()
                                upref.user= request.user
                                upref.post= eachpost
                                upref.value= userpreference
                                if userpreference == 1 and valueobj != 1:
                                        eachpost.likes += 1
                                        eachpost.dislikes -=1
                                elif userpreference == 2 and valueobj != 2:
                                        eachpost.dislikes += 1
                                        eachpost.likes -= 1

                                upref.save()
                                eachpost.save()

                                context= {'post': eachpost,
                                  'postid': postid}

                                return render (request, 'blog/post_detail.html', context)

                        elif valueobj == userpreference:
                                obj.delete()
                                if userpreference == 1:
                                        eachpost.likes -= 1
                                elif userpreference == 2:
                                        eachpost.dislikes -= 1
                                eachpost.save()
                                context= {'post': eachpost,
                                  'postid': postid}
                                return render (request, 'blog/post_detail.html', context)

                except Preference.DoesNotExist:
                        upref= Preference()
                        upref.user= request.user
                        upref.post= eachpost
                        upref.value= userpreference
                        userpreference= int(userpreference)
                        if userpreference == 1:
                                eachpost.likes += 1
                        elif userpreference == 2:
                                eachpost.dislikes +=1
                        upref.save()
                        eachpost.save()
                        context= {'post': eachpost,
                          'postid': postid}
                        return render (request, 'blog/post_detail.html', context)

        else:
                eachpost= get_object_or_404(Post, id=postid)
                context= {'post': eachpost,
                          'postid': postid}
                return render (request, 'blog/post_detail.html', context)
