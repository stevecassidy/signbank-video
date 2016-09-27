# -*- coding: latin-1 -*-
import datetime

from django.test import TestCase, RequestFactory
from django.conf import settings 
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import AnonymousUser, User, Permission
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib import messages

from video.views import addvideo, successpage, deletevideo
from video.models import GlossVideo
from .basetests import BaseTest

def create_request(url, method, data=None, permission=None):
    '''
    This function creates one of various requests. The type
    of request that this function creates depends on the parametres
    of the function.
    
    Call this function in a test case, and use the returned
    request object as an argument to a view. 
    '''
    factory = RequestFactory()
    # Set up the user...
    user = create_user(permission)       
    if 'GET' in method.upper():
        request = factory.get(url)        
    elif 'POST' in method.upper():
        request = factory.post(url, data)
    else:
        raise ValueError("%s is an unrecognised method. It must be one of 'post' or 'get'"%(method))
    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)      
    request.user = user      
    return request
    
    
def create_user(permission=None):
    users = User.objects.all()
    nusers = len(users)
    # If the user has already been created...
    if nusers != 1: 
        user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret')
    else:
        # If the user has already been created, use it 
        user = users[0]
    if permission is not None:
        permission = Permission.objects.get(name=permission)
        user.user_permissions.add(permission)             
    return user


class AddVideoTests(BaseTest):
    def setUp(self):
        BaseTest.setUp(self)
        self.factory = RequestFactory()
        # the url is irrelevant when RequestFactory is used...
        self.url = '/addvideo/'
        self.success_url = '/success/'
        self.data = {"gloss_id" : "3", "videofile" : self.videofile}
        
    def test_add_video_view_redirects_to_success_page_after_successful_request(self):
        '''
        The add video view should redirect 
        to the success view on succecssful upload of a video.
        '''
        request = create_request(url=self.url, method='post', data=self.data)
        response = addvideo(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(reverse('video:successpage'),response.url)
        
    def test_add_view_redirects_to_index_if_no_video_uploaded(self):
        '''
        The add video view should redirect to the index view if 
        no video is uploaded.
        '''
        request = create_request(url=self.url, method='post')
        response = addvideo(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual('/',response.url)
        
    def test_add_view_redirects_to_referer_if_referer_present_and_error(self):
        '''
        If the referer attribute in the request is present,
        then the view should redirect there on error.
        '''
        request = create_request(url=self.url, method='post')
        test_referer = 'test/test'
        request.META['HTTP_REFERER'] = test_referer
        response = addvideo(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(test_referer, response.url)
       
         
class SuccessPageTests(BaseTest):
    def setUp(self):
        BaseTest.setUp(self)
        self.factory = RequestFactory()
        # the url is irrelevant when RequestFactory is used...
        self.url = '/success/'
        
    def test_success_page_view_redirects_to_index_if_no_success_messages(self):
        '''
        The successpage view should redirect to
        index if there are no messsages.
        '''
        request = create_request(url=self.url, method='post')
        response = addvideo(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual('/', response.url)
        
    def test_success_page_view_renders_success_page_if_there_are_success_messages(self):
        '''
        The successpage view should render 'vide/success_page.html'
        if there are messages.
        '''
        request = create_request(url=self.url, method='post')
        messages.add_message(request, messages.INFO, 'TEST MESSAGE!')
        with self.assertTemplateUsed('video/success_page.html'):
            response = successpage(request)
        
    def test_success_page_view_returns_200_response_code_if_there_are_messages(self):
        '''
        The successpage view should return a response code of
        200 if there are messages.
        '''
        request = create_request(url=self.url, method='post')
        messages.add_message(request, messages.INFO, 'TEST MESSAGE!')   
        response = successpage(request)
        self.assertEqual(200, response.status_code)
          
class DeleteVideoTests(BaseTest):
    def setUp(self):
        BaseTest.setUp(self)
        self.factory = RequestFactory()
        # the url is irrelevant when RequestFactory is used...
        self.url = '/delete/1/'
        
        
    def test_deletevideo_redirects_to_index_on_successful_delete_if_no_referer(self):
        '''
        The deletevideo view should redirect to index on successful delete
        if there is no referer.
        '''
        # First, create the video
        gloss_id = 1
        vid = GlossVideo.objects.create(videofile=self.videofile, gloss_id=gloss_id)
        request = create_request(url=self.url, method='post')
        response = deletevideo(request, gloss_id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
   
    def test_deletevideo_redirects_to_referer_on_successful_delete_if_referer_given(self):
        '''
        The deletevideo view should redirect to referer if
        it's given and on success.
        '''
        # First, create the video
        gloss_id = 1
        vid = GlossVideo.objects.create(videofile=self.videofile, gloss_id=gloss_id)
        request = create_request(url=self.url, method='post')
        referer_test = '/test/test'
        request.META['HTTP_REFERER'] = referer_test
        response = deletevideo(request, gloss_id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, referer_test)
        
    def test_deletevideo_removes_video(self):
        '''
        The deletevideo view should delete the video
        '''
        # First, create the video
        gloss_id = 1
        vid = GlossVideo.objects.create(videofile=self.videofile, gloss_id=gloss_id)
        request = create_request(url=self.url, method='post')
        response = deletevideo(request, gloss_id)
        videos =  GlossVideo.objects.all()
        self.assertEqual(len(videos),0)
    
        
        
        
        
        
 
       
        
     
