from django.shortcuts import render
from events.models import Event, Booking, Contact
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, RetrieveUpdateAPIView
from api.serializers import (CreateEventSerializer, OrganizerListSerializer, EventAttendeesSerializer,
 BookingListSerializer, UserCreateSerializer, DisplayEventListSerializer, FollowSerializer, FollowingSerializer)

from datetime import date
from django.utils import timezone
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated 
from .permissions import IsAttendee, IsOwner



class UpcomingList(ListAPIView):
	serializer_class = DisplayEventListSerializer

	def get_queryset(self):
		query= Event.objects.filter(date__gt=date.today())
		return query

class OrganizerList(ListAPIView):
	serializer_class = OrganizerListSerializer
	queryset= Event.objects.all()
	filter_backends=[SearchFilter,]
	search_fields=['organizer__first_name','organizer__last_name']

class UserList(ListAPIView):
	serializer_class = BookingListSerializer
	permission_classes = [IsAuthenticated, IsAttendee]

	def get_queryset(self):
		query = Booking.objects.filter(name=self.request.user)
		return query


class UserCreateAPIView(CreateAPIView):
	serializer_class = UserCreateSerializer

class CreateView(CreateAPIView):
	serializer_class = CreateEventSerializer
	permission_classes = [IsAuthenticated,]

class UpdateView(RetrieveUpdateAPIView):
	queryset = Event.objects.all()
	serializer_class = DisplayEventListSerializer
	permission_classes = [IsAuthenticated, IsOwner]
	lookup_field = 'id'
	lookup_url_kwarg = 'event_id'

class BookView(CreateAPIView):
	serializer_class = BookingListSerializer
	permission_classes = [IsAuthenticated,]

	def perform_create(self,serializer):
		serializer.save(name=self.request.user, event_id=self.kwargs['event_id'])

	
class AttendeesView(RetrieveAPIView):
	serializer_class = EventAttendeesSerializer
	permission_classes = [IsAuthenticated, IsOwner]
	lookup_field = 'id'
	lookup_url_kwarg = 'event_id'
	queryset=Event.objects.all()

class FollowingList(ListAPIView):
	serializer_class = FollowSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		query = Contact.objects.filter(follower=self.request.user)
		return query

class FollowView(CreateAPIView):
	serializer_class = FollowingSerializer
	permission_classes = [IsAuthenticated,]