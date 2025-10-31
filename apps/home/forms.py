from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import MyCompany, ProhibitedItems, Service, FAQ


BASE_INPUT_CLASS = 'peer block w-full max-w-full appearance-none border border-gray-300 bg-white px-3 md:px-4 pt-3 pb-2 text-sm md:text-base text-gray-800 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500 rounded-md placeholder-transparent'
BASE_INPUT_STYLE = 'text-transform: none;'
BASE_TEXTAREA_STYLE = 'text-transform: none;'
class MyCompanyForm(forms.ModelForm):
    
    class Meta:
        model = MyCompany
        fields = [
            'name', 'address', 'phone', 'mobile', 'email', 'facebook', 'location', 'slogan', 'logo',
            'about_us_short_description', 'about_us_long_description', 'mission', 'vision', 'goal',
            'why_choose_us_card1_title', 'why_choose_us_card1_description', 'why_choose_us_card1_icon',
            'why_choose_us_card1_icon_color', 'why_choose_us_card2_title', 'why_choose_us_card2_description',
            'why_choose_us_card2_icon', 'why_choose_us_card2_icon_color', 'why_choose_us_card3_title',
            'why_choose_us_card3_description', 'why_choose_us_card3_icon', 'why_choose_us_card3_icon_color'
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={'class': BASE_INPUT_CLASS, 'style': BASE_INPUT_STYLE}),
            'address': CKEditor5Widget(attrs={'class': "django_ckeditor_5"}, config_name='default'),
            'phone': forms.TextInput(attrs={'class': BASE_INPUT_CLASS, 'style': BASE_INPUT_STYLE}),
            'mobile': forms.TextInput(attrs={'class': BASE_INPUT_CLASS, 'style': BASE_INPUT_STYLE}),
            'email': forms.EmailInput(attrs={'class': BASE_INPUT_CLASS, 'style': BASE_INPUT_STYLE}),
            'facebook': forms.URLInput(attrs={'class': BASE_INPUT_CLASS, 'style': BASE_INPUT_STYLE}),
            'slogan': forms.TextInput(attrs={'class': BASE_INPUT_CLASS, 'style': BASE_INPUT_STYLE}),
            'location': forms.TextInput(attrs={'class': BASE_INPUT_CLASS, 'style': BASE_INPUT_STYLE}),
            'logo': forms.FileInput(attrs={'class': BASE_INPUT_CLASS, 'style': BASE_INPUT_STYLE}),
            'about_us_short_description': CKEditor5Widget(attrs={'class': "django_ckeditor_5"}, config_name='default'),
            'about_us_long_description': CKEditor5Widget(attrs={'class': "django_ckeditor_5"}, config_name='default'),
            'mission': CKEditor5Widget(attrs={'class': "django_ckeditor_5"}, config_name='default'),
            'vision': CKEditor5Widget(attrs={'class': "django_ckeditor_5"}, config_name='default'),
            'goal': CKEditor5Widget(attrs={'class': "django_ckeditor_5"}, config_name='default'),
            'why_choose_us_card1_title': forms.TextInput(attrs={'class': BASE_INPUT_CLASS, 'style': BASE_INPUT_STYLE}),
            'why_choose_us_card1_description': CKEditor5Widget(attrs={'class': "django_ckeditor_5"}, config_name='default'),
            'why_choose_us_card1_icon': forms.TextInput(attrs={'class': BASE_INPUT_CLASS, 'style': BASE_INPUT_STYLE}),
            'why_choose_us_card1_icon_color': forms.TextInput(attrs={'class': BASE_INPUT_CLASS, 'style': BASE_INPUT_STYLE}),
            'why_choose_us_card2_title': forms.TextInput(attrs={'class': BASE_INPUT_CLASS, 'style': BASE_INPUT_STYLE}),
            'why_choose_us_card2_description': CKEditor5Widget(attrs={'class': "django_ckeditor_5"}, config_name='default'),
            'why_choose_us_card2_icon': forms.TextInput(attrs={'class': BASE_INPUT_CLASS, 'style': BASE_INPUT_STYLE}),
            'why_choose_us_card2_icon_color': forms.TextInput(attrs={'class': BASE_INPUT_CLASS, 'style': BASE_INPUT_STYLE}),
            'why_choose_us_card3_title': forms.TextInput(attrs={'class': BASE_INPUT_CLASS, 'style': BASE_INPUT_STYLE}),
            'why_choose_us_card3_description': CKEditor5Widget(attrs={'class': "django_ckeditor_5"}, config_name='default'),
            'why_choose_us_card3_icon': forms.TextInput(attrs={'class': BASE_INPUT_CLASS, 'style': BASE_INPUT_STYLE}),
            'why_choose_us_card3_icon_color': forms.TextInput(attrs={'class': BASE_INPUT_CLASS, 'style': BASE_INPUT_STYLE}),
        }


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': BASE_INPUT_CLASS, 'style': BASE_INPUT_STYLE}),
            'description': CKEditor5Widget(attrs={'class': "django_ckeditor_5"}, config_name='default'),
            'image': forms.FileInput(attrs={'class': BASE_INPUT_CLASS, 'style': BASE_INPUT_STYLE}),
        }


class FaqForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ['question', 'answer']
        widgets = {
            'question': CKEditor5Widget(attrs={'class': "django_ckeditor_5"}, config_name='default'),
            'answer': CKEditor5Widget(attrs={'class': "django_ckeditor_5"}, config_name='default'),
        }


class ProhibitedItemForm(forms.ModelForm):
    class Meta:
        model = ProhibitedItems
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': BASE_INPUT_CLASS, 'style': BASE_INPUT_STYLE}),
        }
