from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views import View
from .forms import UserSignup, UserLogin, EventForm, UserForm, ProfileUpdate, ProfileUser
from django.contrib import messages
from .models import Event, UserEvent, Profile, Contact
from datetime import date
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail

@login_required
def profile(request, user_id):
	profile= Profile.objects.get(user_id=user_id)
	user= User.objects.get(id=user_id)
	events= Event.objects.filter(organizer=user)
	check=None

	try:
		obj = Contact.objects.get(following=user, follower=request.user)

	except Contact.DoesNotExist:
		if request.POST.get('follow'):
			try:
				obj = Contact.objects.get(following=user, follower=request.user)
				check = True
			except Contact.DoesNotExist:
				Contact.objects.create(following=user,follower=request.user)
				check = True
		elif request.POST.get('unfollow'):
			try:
				obj = Contact.objects.get(following=user, follower=request.user)
				check=False
			except Contact.DoesNotExist:
				Contact.objects.get(following=user,follower=request.user).delete()
				check=False
	else:

		if request.user == obj.follower:
			check= True
		else: 
			check= False

		if request.POST.get('follow'):
			try:
				obj = Contact.objects.get(following=user, follower=request.user)
				check = True
			except Contact.DoesNotExist:
				Contact.objects.create(following=user,follower=request.user)
				check = True
		elif request.POST.get('unfollow'):
			try:
				obj = Contact.objects.get(following=user, follower=request.user)
				check=False
			except Contact.DoesNotExist:
				Contact.objects.get(following=user,follower=request.user).delete()
				check=False
				
	context = {
		'profile':profile,
		'events':events,
		'followers_of_user':check,
	}
	return render(request, 'profile.html', context)

def organizers_list(request):
	if request.user.is_anonymous :
		messages.warning(request, "You need to sign in first")
		return redirect('events:signin')
	profiles = Profile.objects.all()
	orglist=[]
	for p in profiles:
		try:
			Event.objects.get(organizer=p.user)
			orglist.append(p)
		except Event.DoesNotExist:
			pass

	context={

		'organizers':orglist,

	}
	return render(request, 'organizers_list.html', context)

def home(request):
	return render(request, 'home.html')

def UpdateProfile(request, user_id):		# update_profile, ~profile_id~
	# redundant
	
	if request.user.is_anonymous :
		messages.warning(request, "You need to sign in first")
		return redirect('events:signin')
	profile=Profile.objects.get(user_id=user_id)
	form= ProfileUpdate(instance=profile)
	form2= ProfileUser(instance=request.user)
	if request.method == "POST":
		form = ProfileUpdate(request.POST,request.FILES, instance=profile)
		form2= ProfileUser(request.POST, instance=request.user)
		if form.is_valid() and form2.is_valid():
			form.save()
			form2.save()
			messages.success(request, "Successfully Edited!")
			return redirect('events:profile', user_id)
	context = {
	"form": form,
	"profile": profile,
	"form2": form2,
	}
	return render(request, 'profile_update.html', context)



def event_list(request):
	events=Event.objects.filter(date__gte=date.today())
	query=request.GET.get("q")
	if query:
		events=events.filter(
			Q(title__icontains=query)|
			Q(description__icontains=query)|
			Q(organizer__username__icontains=query)
		).distinct()

	context={
		'events':events,
	}
	return render(request, 'event_list.html', context)


def create_event(request):
	if request.user.is_anonymous:
		messages.warning(request, "You need to sign in first")
		return redirect('events:signin')
	form = EventForm()
	if request.method == "POST":
		form = EventForm(request.POST, request.FILES or None)
		if form.is_valid():
			event = form.save(commit=False)
			event.organizer = request.user
			event.save()
			messages.success(request, "Successfully Created!")
			return redirect('events:dashboard')
	context = {
	"form": form,
	}
	return render(request, 'event_create.html', context)


def dashboard(request):
	if request.user.is_anonymous:
		messages.warning(request, "You need to sign in first")
		return redirect('events:signin')
	
	events=request.user.events.all()
	past_events=request.user.attended.filter(event__date__lt=date.today())
	future_events=request.user.attended.filter(event__date__gte=date.today())
	context={

		'events':events,
		'past':past_events,
		'future':future_events,
	
	}
	return render(request,'dash.html',context)


def event_detail(request, event_id):
	context={
		'event':Event.objects.get(id=event_id)
	}
	return render(request,'event_detail.html',context)


def event_update(request, event_id):
	event = Event.objects.get(id=event_id)
	if (request.user.is_anonymous) or (request.user != event.organizer):
		messages.warning(request, "You need to sign in first")		# add new message
		return redirect('events:home')
	form = EventForm(instance=event)
	if request.method == "POST":
		form = EventForm(request.POST,request.FILES, instance=event)
		if form.is_valid():
			form.save()
			messages.success(request, "Successfully Edited!")
			return redirect('events:dashboard')
	context = {
	"form": form,
	"event": event,
	}
	return render(request, 'event_update.html', context)


def event_delete(request, event_id):
	event=Event.objects.get(id=event_id)
	if (request.user.is_anonymous) or (request.user != event.organizer):
		messages.warning(request, "You need to sign in first")		# add new message
		return redirect('events:home')
	event.delete()
	messages.success(request, "Successfully Deleted!")
	return redirect('events:dashboard')


class Signup(View):
	form_class = UserSignup
	template_name = 'signup.html'

	def get(self, request, *args, **kwargs):
		form = self.form_class()
		return render(request, self.template_name, {'form': form})

	def post(self, request, *args, **kwargs):
		form = self.form_class(request.POST)
		if form.is_valid():
			user = form.save(commit=False)
			user.set_password(user.password)
			user.save()
			messages.success(request, "You have successfully signed up.")
			login(request, user)
			return redirect("events:home")
		messages.warning(request, form.errors)
		return redirect("events:signup")

def event_book(request, event_id):
	form = UserForm()
	event = Event.objects.get(id=event_id)
	if request.user.is_anonymous:
		return redirect('events:signin')
	if request.method == "POST":
		form = UserForm(request.POST)
		if form.is_valid():
			user_event = form.save(commit=False)
			user_event.event = event
			user_event.name = request.user
			if user_event.seats <= event.seats_left():
				user_event.save()
				send_mail(
					'[NO-REPLY]: UNTITLED. Booking Confirmation',
					"""
					This is a automated email to confirm your booking, please do not reply.

					Review the below information:
					
					Event Title: %s
					Date: %s
					Time: %s
					Seats Reserved: %s seats


					Best UNTITLED. regards,

					© UNTITLED. Event Agency 2020
					""" % (event.title, event.date, event.time, user_event.seats),
					'untitled.events.2020@gmail.com',
					[request.user.email],
					fail_silently=False,
					)
				messages.success(request, "Your seats are booked!")
			else:
				messages.success(request, "requested seats exceeded the available capacity!")
			
		return redirect('events:event-detail', event_id)
	context = {
		"form":form,
		"event": event,
	}
	return render(request, 'book_event.html', context)

class Login(View):
	form_class = UserLogin
	template_name = 'login.html'



	def get(self, request, *args, **kwargs):
		form = self.form_class()
		return render(request, self.template_name, {'form': form})

	def post(self, request, *args, **kwargs):
		form = self.form_class(request.POST)
		if form.is_valid():

			username = form.cleaned_data['username']
			password = form.cleaned_data['password']

			auth_user = authenticate(username=username, password=password)
			if auth_user is not None:
				login(request, auth_user)
				messages.success(request, "Welcome Back!")
				return redirect('events:dashboard')
			messages.warning(request, "Wrong email/password combination. Please try again.")
			return redirect("events:signin")
		messages.warning(request, form.errors)
		return redirect("events:signin")


class Logout(View):
	def get(self, request, *args, **kwargs):
		logout(request)
		messages.success(request, "You have successfully logged out.")
		return redirect("events:home")



