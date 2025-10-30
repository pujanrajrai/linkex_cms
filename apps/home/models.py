from django.db import models
from base.models import BaseModel

# Create your models here.
class MyCompany(BaseModel):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=255)
    mobile = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=255)
    facebook = models.URLField(max_length=255)
    slogan = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='company/logo/')

    # aboutus
    about_us_short_description = models.TextField()
    about_us_long_description = models.TextField()
    mission = models.TextField()
    vision = models.TextField()
    goal = models.TextField()

    why_choose_us_card1_title = models.CharField(max_length=255, null=True, blank=True)
    why_choose_us_card1_description = models.TextField(null=True, blank=True)
    why_choose_us_card1_icon = models.CharField(max_length=255, null=True, blank=True)
    why_choose_us_card1_icon_color = models.CharField(max_length=255, null=True, blank=True)
    why_choose_us_card2_title = models.CharField(max_length=255, null=True, blank=True)
    why_choose_us_card2_description = models.TextField(null=True, blank=True)
    why_choose_us_card2_icon = models.CharField(max_length=255, null=True, blank=True)
    why_choose_us_card2_icon_color = models.CharField(max_length=255, null=True, blank=True)   
    why_choose_us_card3_title = models.CharField(max_length=255, null=True, blank=True)
    why_choose_us_card3_description = models.TextField(null=True, blank=True)
    why_choose_us_card3_icon = models.CharField(max_length=255, null=True, blank=True)
    why_choose_us_card3_icon_color = models.CharField(max_length=255, null=True, blank=True)


class Service(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='company/services/')

class FAQ(BaseModel):
    question = models.TextField()
    answer = models.TextField()


