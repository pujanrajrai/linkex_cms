from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from base.models import BaseModel

# Create your models here.
class MyCompany(BaseModel):
    name = models.CharField(max_length=255)
    address = CKEditor5Field('Content', config_name='default')
    phone = models.CharField(max_length=255)
    mobile = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=255)
    facebook = models.URLField(max_length=255)
    slogan = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='company/logo/')
    location = models.CharField(max_length=255, null=True, blank=True)

    # aboutus
    about_us_short_description = CKEditor5Field('Content', config_name='default')
    about_us_long_description = CKEditor5Field('Content', config_name='default')
    mission = CKEditor5Field('Content', config_name='default')
    vision = CKEditor5Field('Content', config_name='default')
    goal = CKEditor5Field('Content', config_name='default')

    why_choose_us_card1_title = models.CharField(max_length=255, null=True, blank=True)
    why_choose_us_card1_description = CKEditor5Field('Content', config_name='default', null=True, blank=True)
    why_choose_us_card1_icon = models.CharField(max_length=255, null=True, blank=True)
    why_choose_us_card1_icon_color = models.CharField(max_length=255, null=True, blank=True)
    why_choose_us_card2_title = models.CharField(max_length=255, null=True, blank=True)
    why_choose_us_card2_description = CKEditor5Field('Content', config_name='default', null=True, blank=True)
    why_choose_us_card2_icon = models.CharField(max_length=255, null=True, blank=True)
    why_choose_us_card2_icon_color = models.CharField(max_length=255, null=True, blank=True)   
    why_choose_us_card3_title = models.CharField(max_length=255, null=True, blank=True)
    why_choose_us_card3_description = CKEditor5Field('Content', config_name='default', null=True, blank=True)
    why_choose_us_card3_icon = models.CharField(max_length=255, null=True, blank=True)
    why_choose_us_card3_icon_color = models.CharField(max_length=255, null=True, blank=True)


class Service(BaseModel):
    name = models.CharField(max_length=255)
    description = CKEditor5Field('Content', config_name='default')
    image = models.ImageField(upload_to='company/services/')

class FAQ(BaseModel):
    question = CKEditor5Field('Content', config_name='default')
    answer = CKEditor5Field('Content', config_name='default')


class ProhibitedItems(BaseModel):
    name = models.CharField(max_length=255)
