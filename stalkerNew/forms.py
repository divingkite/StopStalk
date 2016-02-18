import re
import json
from django import forms
from .stalkerNew.helper_functions import get_link_fileptr
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
 
class RegistrationForm(forms.Form):
    '''
    Form for registering.
    username,email,password all required.
    '''
    username  = forms.RegexField(regex=r'^\w+$', widget=forms.TextInput(attrs=dict( max_length=30)), label=_("Username"),       error_messages={ 'invalid': _("This value must contain only letters, numbers and underscores.") })
    email     = forms.EmailField(widget=forms.TextInput(attrs=dict( max_length=30)), label=_("Email address"))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=dict( max_length=30, render_value=False)), label=_("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=dict( max_length=30, render_value=False)), label=_("Password (again)"))
 
    def clean_username(self):
        '''
        To check if a user with same username exists or not.
        '''
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(_("The username already exists. Please try another one."))
 
    def clean_email(self):
        '''
        To check if a user with same e-mail address exists or not.
        '''
        try:
            user = User.objects.get(email__iexact=self.cleaned_data['email'])
        except User.DoesNotExist:
            return self.cleaned_data['email']
        raise forms.ValidationError(_("The email already registered. Please try another one."))
 
    def clean(self):
        '''
        To check if both the passwords entered by a user matches or not.
        '''
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields did not match."))
        return self.cleaned_data

class Login_Form(forms.Form):
    '''
    Form for logging in a user.
    '''
    username = forms.CharField(widget=forms.TextInput(attrs=dict( max_length=30)), label=_("User-name"))
    password = forms.CharField(widget=forms.PasswordInput(attrs=dict( max_length=30, render_value=False)), label=_("Password"))
    

    def clean(self):
        try:
            User.objects.get( username=self.cleaned_data['username'] )
            
        except User.DoesNotExist:
            raise forms.ValidationError( _( "You are not a registered user, Register and visit again!" ) )
        else:
            user = User.objects.get( username=self.cleaned_data['username'] )
            if user.check_password( self.cleaned_data['password'] ):
                return self.cleaned_data
            else:
                raise forms.ValidationError( _("The password entered does not match your account password.")) 
            
class ListExpansionForm(forms.Form):
    '''
    Form for adding new contacts.
    name_ is required,others feilds are not compulsory.
    '''
    cc_hand = forms.CharField( required=False,widget= forms.TextInput( attrs=dict(max_length=30)),label=("Codechef Handle Name") )
    cf_hand = forms.CharField( required=False,widget= forms.TextInput( attrs=dict(max_length=30)),label=("Codeforces Handle Name") )
    name_   = forms.CharField( widget= forms.TextInput( attrs=dict( max_length=50)),label=("Name") )
    
    def clean_cf_hand(self):
        '''
        Raises a Validation error when the codeforces handle entered by a user doesn't exist.
        '''
        #print type(self.cleaned_data['cf_hand']),self.cleaned_data['cf_hand']
        if self.cleaned_data['cf_hand'] != "":

            cf_url = 'http://www.codeforces.com/api/user.status?handle=%s'%self.cleaned_data['cf_hand']
            link_file = get_link_fileptr(cf_url)
            
            if link_file == None:
                raise forms.ValidationError( _("Either leave blank or enter correct Codeforces handle name"))
            else:
                
                data = link_file.read()
                data = json.loads(data)
                if data['status'] == 'failed':
                    raise forms.ValidationError( _("Either leave blank or enter correct Codeforces handle name"))
                else:
                    return self.cleaned_data['cf_hand']
    
    def clean_cc_hand(self):
        '''
        Raises a Validation error when the codechef handle entered by a user doesn't exist.
        '''
        
        if self.cleaned_data['cc_hand'] != "":

            cc_url = 'https://www.codechef.com/users/%s'%self.cleaned_data['cc_hand']
            link_file = get_link_fileptr(cc_url)
        
            if "Programming Competition,Programming Contest" in BeautifulSoup(link_file.read()).title.string: 
                # "...." is title of codechef home page, the page of redirection when a codechef url fetched doesn't exist.
                raise forms.ValidationError( _("Either leave blank or enter correct Codechef handle name") )
            else:
                return self.cleaned_data['cc_hand']
