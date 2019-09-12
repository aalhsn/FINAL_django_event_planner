from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from PIL import Image
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

class Event(models.Model):
	title=models.CharField(max_length=100)
	image=models.ImageField(null=True, blank=True)	# image
	description=models.TextField()
	location=models.CharField(max_length=100)
	date=models.DateField()
	time=models.TimeField()
	capacity=models.PositiveIntegerField()
	organizer=models.ForeignKey(User, default=1, on_delete=models.CASCADE, related_name='events')

	def seats_left(self):
		total=0
		for x in self.bookings.all():
			print(x)
			total += x.seats
		return self.capacity - total


	def __str__(self):
		return "%s - %s" % (self.title, self.location)

	def get_absolute_url(self):
		return reverse('event-details', kwargs={'event_id':self.id})


class UserEvent(models.Model):
	name=models.ForeignKey(User, default=1, on_delete=models.CASCADE, related_name='attended')	#naming
	seats=models.PositiveIntegerField()
	event=models.ForeignKey(Event, default=1, on_delete=models.CASCADE, related_name='bookings')


	def __str__(self):
		return "%s - %s" % (self.name, self.event.title)

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
	image = models.ImageField(default='default-avatar_tcWonAu_iaqxAtf.png')

	def __str__(self):
		return '%s profile'% (self.user.username)






@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
	instance.profile.save()


class Contact(models.Model):
	following= models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
	follower= models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
	created= models.DateTimeField(auto_now_add=True, db_index=True)

	class Meta:
		ordering=('-created',)

	def __str__(self):
		return '{} follows {}'.format(self.follower, self.following)
 


