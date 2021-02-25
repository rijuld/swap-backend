# views.py
from rest_framework import viewsets

from .serializers import CoursesSerializer,NewUserSerializer,requireSerializer,authtokSerializer
from .models import courses,NewUser,require,authtok
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework.views import APIView
import firebase_admin
from firebase_admin import credentials
from fcm_django.models import FCMDevice
from firebase_admin import messaging
from swapbackend2 import settings
from swapbackend2.settings import SWAPFOLDER

if not firebase_admin._apps:
	cred = credentials.Certificate(SWAPFOLDER+"swapbackend2/a.json")
	firebase_admin.initialize_app(cred)

def verifyauth(idtoken):
	try:
		idinfo = id_token.verify_oauth2_token(idtoken, requests.Request(), "75980394763-bj0hr3nhh40qk6qaoeh6ddi4p0svhfa0.apps.googleusercontent.com")
		if idinfo['hd'] != "hyderabad.bits-pilani.ac.in":
			raise ValueError('Wrong hosted domain.')  
		userid = idinfo['email']
		return userid
	except ValueError:
		# Invalid token
		pass

def send_multicast(u1,u2):
	token1=u1.cloudToken
	token2=u2.cloudToken
	registration_tokens = [token1,token2]
	phno1=u1.phone_number
	phno2=u2.phone_number
	message = messaging.MulticastMessage(
		data={'uid1': u1.userid, 'uid2': u2.userid,'phno1': phno1,'phno2': phno2},
		tokens=registration_tokens,
		notification=messaging.Notification(
        title='Hurray course matched',
        body=' email 1 '+u1.userid+'phoneno 1'+' email 2'+u2.userid+' phno1: '+phno1+' phno2: '+phno2,
    )
	)
	response = messaging.send_multicast(message)
	print('{0} messages were sent successfully hurray'.format(response.success_count))

class authtokViewSet(viewsets.ModelViewSet):
	
	queryset = authtok.objects.all().order_by('id')
	serializer_class = authtokSerializer
	http_method_names = ['get', 'post', 'head','delete']
	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		self.perform_create(serializer)
		phone_number=serializer.data['phone_number']
		idToken=serializer.data['idToken']
		cloudToken=serializer.data['cloudToken']
		userid=verifyauth(idToken)
		k=NewUser(userid=userid, phone_number=phone_number,cloudToken=cloudToken)
		k.save()
		headers = self.get_success_headers(serializer.data)
		return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class CoursesViewSet(viewsets.ModelViewSet):
	
	queryset = courses.objects.all().order_by('coursename')
	serializer_class = CoursesSerializer
	http_method_names = ['get', 'post', 'head','delete']

class NewUserViewSet(viewsets.ModelViewSet):
	queryset = NewUser.objects.all()
	serializer_class = NewUserSerializer
	http_method_names = ['get', 'post', 'head','delete']

class RequireViewSet(viewsets.ModelViewSet):
	queryset = require.objects.all().order_by('id')
	serializer_class = requireSerializer
	http_method_names = ['get', 'post', 'head','delete']
	
	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		self.perform_create(serializer)
		coursereq=serializer.data['coursereq']
		coursegiv=serializer.data['coursegiv']
		user=serializer.data['user']
		if require.objects.filter(coursereq__courseid=coursegiv,coursegiv__courseid=coursereq).exists():
			user2=require.objects.filter(coursereq__courseid=coursegiv,coursegiv__courseid=coursereq).first().user
			require.objects.filter(coursereq__courseid=coursegiv,coursegiv__courseid=coursereq).first().delete()
			require.objects.filter(coursereq__courseid=coursereq,coursegiv__courseid=coursegiv,user__userid=user).delete()
			user = NewUser.objects.get(userid=user)
			user.course.remove(courses.objects.get(courseid=coursegiv))
			user2.course.remove(courses.objects.get(courseid=coursereq))
			user2.course.add(courses.objects.get(courseid=coursegiv))
			user.course.add(courses.objects.get(courseid=coursereq))
			send_multicast(user,user2)
		headers = self.get_success_headers(serializer.data)
		return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
#there has to be something written here to notify both the users            
# (Receive token by HTTPS POST) 
# ...
class Test(APIView):
	def post(self, request):
		idToken = request.data['idToken']
		phonenumber = request.data['phone_number']
		userid=verifyauth(idToken)
		k=User(userid=userid, phone_number=phonenumber)
		k.save()
		return Response("hello")
""" try:
	CLIENT_ID="676954385087-tp09jf7ave2790d930uam9m4ke3dvdqs.apps.googleusercontent.com"
	# Specify the CLIENT_ID of the app that accesses the backend:
	idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

	# Or, if multiple clients access the backend server:
	# idinfo = id_token.verify_oauth2_token(token, requests.Request())
	# if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
	#     raise ValueError('Could not verify audience.')

	# If auth request is from a G Suite domain:
	 if idinfo['hd'] != "hyderabad.bits-pilani.ac.in":
		 raise ValueError('Wrong hosted domain.')

	# ID token is valid. Get the user's Google Account ID from the decoded token.
	userid = idinfo['sub']
except ValueError:
	# Invalid token
	pass """