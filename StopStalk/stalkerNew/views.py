from django.shortcuts import render
from django.template import RequestContext, loader
from .models import *
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from stalkerNew.helper_functions import *
from stalkerNew.forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth import login as auth_login
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


@csrf_protect
def register(request):
    '''
    To register a user, input is via RegistrationForm.
    '''
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password1'],
            email=form.cleaned_data['email']
            )
            user.save()
            user = authenticate( username = form.cleaned_data['username'], password = form.cleaned_data['password1'] )
            if user is not None:
                auth_login( request,user )
                return HttpResponseRedirect( reverse( 'stalkerNew:friend_list' ) )
            else:
                return HttpResponseRedirect( reverse('stalkerNew:login') )
            
    else:
        form = RegistrationForm()
    variables = RequestContext(request, {'form': form})
 
    return render_to_response('stalkerNew/register.html',variables,)
 

def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/stalkerNew/login/')
 

def home(request):
    '''
    Can be used as a home page, but not used now.
    '''
    if request.user.is_authenticated():
        return render( request, 'stalkerNew/home.html' )
    else:
        return render( request,'stalkerNew/home.html' , { 'error':"Not logged in" })

@csrf_protect
def login(request):
    '''
    Upon login redirects to the friend_list page.
    '''
    if request.method == "POST":
        form = Login_Form(request.POST)
        if form.is_valid():
            user = authenticate( username = form.cleaned_data['username'], password = form.cleaned_data['password'] )
            if user is not None:
                auth_login( request,user )
                return HttpResponseRedirect( reverse( 'stalkerNew:friend_list' ) )
    else:
        form = Login_Form()
    variables = RequestContext(request, { 'form': form } )
 
    return render_to_response('stalkerNew/login.html',variables,)

@csrf_protect
def update_info(request):
    '''
    For the refresh button, which updates all information about all contacts.
    '''
    if request.user.is_authenticated():
        current = HelperFunctions(request)
        current.FetchContent()
        objs = Person.objects.filter( user = request.user )
        return render( request, 'stalkerNew/list.html' , { 'people' : objs,'err_message':"" } )
    else :
        return HttpResponseRedirect( reverse( 'stalkerNew:login' ))

def list_( request ):
    if request.user.is_authenticated():
        objs = Person.objects.filter( user = request.user )
        return render( request, 'stalkerNew/list.html' , { 'people' : objs,'err_message':"" } )
    else :
        return HttpResponseRedirect( reverse( 'stalkerNew:login' ))

def expand_list( request ):
    if request.user.is_authenticated():
        if request.method == "POST":
            form   =    ListExpansionForm(request.POST)
            if form.is_valid():
                cc_han = form.cleaned_data['cc_hand']
                cf_han = form.cleaned_data['cf_hand']
                name   = form.cleaned_data['name_']
                user   = request.user
                
                try:
                    Person.objects.get( cc=cc_han, cf =cf_han, name=name, user=user )    #check if a person with same details exist or not
                except Person.DoesNotExist:
                    
                    obj = Person( cc = cc_han, cf = cf_han , name = name, user =user )  #saves a person contacts.
                    obj.save()
                    error_message=""
                else:
                    error_message="Contact already exist."                              #if the contact already exists.
            
                objs = Person.objects.filter( user = user)
                return render( request, 'stalkerNew/list.html' , { 'people' : objs,'err_message':error_message } )
        else:
            form = ListExpansionForm()
        variables = RequestContext(request, { 'form': form } )
        
        return render_to_response('stalkerNew/expand_list.html',variables,)

    else:
        return HttpResponseRedirect( reverse( 'stalkerNew:login' ))

def delete_contact( request,person_id ):
    if request.user.is_authenticated():
        p_object = Person.objects.get( pk = person_id )
        if p_object is not None:
            p_object.delete()
        objs = Person.objects.filter( user = request.user )
        return render( request, 'stalkerNew/list.html' , { 'people' : objs,'err_message':"" } ) 
    else :
        return HttpResponseRedirect( reverse( 'stalkerNew:login' ))


def profile( request,person_id ):
    if request.user.is_authenticated() :
        person = Person.objects.get(pk=person_id)
        cf_contest = Contest.objects.filter( site ='CF' )
        cf_obj=[]                                         # a list containing [[contest name,[questions]],[]] 
        for contest in cf_contest:                        # fetching all contest problems
            ques = Question.objects.filter( contest = contest, person = person )

            if len(ques) != 0:
                cf_obj.append( [contest.name,ques ] )
        
        cc_contest = Contest.objects.filter( site='CC' )
        
        cc_obj=[]
        for contest in cc_contest:
            ques = Question.objects.filter( contest = contest, person = person )
            if len(ques) != 0:
                cc_obj.append( [contest,ques ] )
            
        cf_prac = PracticeProb.objects.filter( person = person,site='CF' )     #fetching all practice problems.
        cc_prac = PracticeProb.objects.filter( person = person,site='CC' )

        return render( request, 'stalkerNew/profile.html' ,{ 'cf_data_chal' : cf_obj ,
                                                             'cc_data_chal' : cc_obj ,
                                                             'cc_data_prac' : cc_prac ,
                                                             'cf_data_prac' : cf_prac } )
    else :
        return HttpResponseRedirect( reverse( 'stalkerNew:login' ))

def search_contestwise( request ):
    '''
    Gives list of all contest when site ( CC,CF ) is provided
    '''
    if request.user.is_authenticated():
        wsite = request.POST['website']
        cons = Contest.objects.filter( site = wsite )
        return render( request, 'stalkerNew/contest.html' ,{ 'contests': cons,'website':wsite } )
    else :
        return HttpResponseRedirect( reverse( 'stalkerNew:login' ))

def SearchForThisContest(request):
    '''
    Fetches all the questions of all contacts when a contest in selected in contest.html page.
    '''
    if request.user.is_authenticated():
        questions_done_by_a_person = {}
        contest_name = request.POST.get('con','')
        contest = Contest.objects.filter(name=contest_name)
        
        persons = Person.objects.filter( user = request.user )
        for person in persons:
            ques = Question.objects.filter( person = person, contest = contest )
            questions_done_by_a_person[person] = ques

        return  render( request, 'stalkerNew/InAContest.html' ,{ 'all_questions': questions_done_by_a_person } )
    else :
        return HttpResponseRedirect( reverse( 'stalkerNew:login' ))

@login_required
def update_a_person_info(request,person_id):
    '''
    Updates information about a particular contact.
    '''
    current = HelperFunctions(request,person_id)
    current.FetchContentForAPerson()
    objs = Person.objects.filter( user = request.user )
    return render( request, 'stalkerNew/list.html' , { 'people' : objs,'err_message':"" } )

