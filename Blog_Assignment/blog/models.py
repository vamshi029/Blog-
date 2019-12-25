from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class MyAccountManager(BaseUserManager):
	def create_user(self, email, username, password=None):
		if not email:
			raise ValueError('Users must have an email address')
		if not username:
			raise ValueError('Users must have a username')

		user = self.model(
			email=self.normalize_email(email),
			username=username,
		)

		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, email, username, password):
		user = self.create_user(
			email=self.normalize_email(email),
			password=password,
			username=username,
		)
		user.is_admin = True
		user.is_staff = True
		user.is_superuser = True
		user.save(using=self._db)
		return user


class Account(AbstractBaseUser):
	email = models.EmailField(verbose_name="email", max_length=60, unique=True)
	username = models.CharField(max_length=30, unique=True)
	date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
	last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
	is_admin = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)
	is_superuser = models.BooleanField(default=False)


	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username']

	objects = MyAccountManager()

	def __str__(self):
		return self.username

	# For checking permissions. to keep it simple all admin have ALL permissons
	def has_perm(self, perm, obj=None):
		return self.is_admin

	# Does this user have permission to view this app? (ALWAYS YES FOR SIMPLICITY)
	def has_module_perms(self, app_label):
		return True

class Post(models.Model):
    author = models.ForeignKey('Account',on_delete=models.CASCADE,)
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    likes= models.IntegerField(default=0)
    dislikes= models.IntegerField(default=0)

    def no_of_comments(self):
        return self.comments
    def no_of_likes(self):
        return self.likes
    def no_of_dislikes(self):
        return self.dislikes
    def people_liked(self):
        return self.preferences
    def save_post(self):
        self.save()
        return reverse("post_detail",kwargs={'pk':self.pk})

#once we create a instance of a post ,go to detail page of that post
    def get_absolute_url(self):
        return reverse("post_list")


    def __str__(self):
        return self.title



class Comment(models.Model):
    post = models.ForeignKey('blog.Post', related_name='comments',on_delete=models.CASCADE,)
    author = models.ForeignKey('Account',related_name='comments',on_delete=models.CASCADE)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)


#once comment is posted ,go to homepage of all the posts
    def get_absolute_url(self):
        return reverse("post_list")

    def __str__(self):
        return self.text

class Preference(models.Model):
    user= models.ForeignKey('Account',related_name='preferences',on_delete=models.CASCADE)
    post= models.ForeignKey(Post,related_name='preferences',on_delete=models.CASCADE,)
    value= models.IntegerField()


    def __str__(self):
        return str(self.user) + ':' + str(self.post) +':' + str(self.value)

    class Meta:
       unique_together = ("user", "post", "value")
