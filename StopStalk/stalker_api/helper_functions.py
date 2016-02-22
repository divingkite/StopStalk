import urllib2
import bs4
import json
import socks
import socket
from thread import start_new_thread as new_thread
from stalker_api.models import *


def connectTor():
    '''
    If you want your http/https conection is through tor.
    '''
    socks.setdefaultproxy( socks.PROXY_TYPE_SOCKS5, "127.0.0.1",9050,True )
    socket.socket = socks.socksocket

def get_link_fileptr(url):
    '''
    For fetching content from a url.
    '''
    connectTor()
        
    #proxy = urllib2.ProxyHandler( { 'http' : 'http://Username:Password@ProxyServer:Port' , 'https' : 'https://Username:Password@ProxyServer:Port' })
    auth = urllib2.HTTPBasicAuthHandler()
    opener = urllib2.build_opener( auth, urllib2.HTTPHandler )       #select an opener as required.
    #opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler )
    urllib2.install_opener(opener)
    try:
        link_file = urllib2.urlopen(url)
    except urllib2.URLError as e:
        if e.code == 400:                # if bad request error occurs, It occurs when a codeforces url which
                                         # doesn't exist is fetched, A invalid cf_handle will raise this error.     
            return None 
    
        return get_link_fileptr(url)     #if any other error occurs, then fetch again.
    else:
        return link_file                 #Success

def get_cc_contest_list():
    '''
    Fetches list of all contest hosted on/by codechef.

    In codechef page, a contest name/url exists as:
    <td><a href="Contest_url">Contest_Name</a></td>

    parsed using bs4.
    '''
    cc_contest_list = []
    data = get_link_fileptr('https://www.codechef.com/contests').read()
    soup = bs4.BeautifulSoup( data )
    
    tds = soup.find_all('td')                       
    for td in tds:
        links = td.find_all('a')
        for link in links:
            link = link.get('href')   #data is like written below
            if link.count('/') == 1:
                cc_contest_list.append(link[1:])     #link is "/Contest-Name"
    cc_contest_list =  cc_contest_list[1:-2]         #some non-useful urls exist so removed those.
    for contest in cc_contest_list:
        try:
            Contest.objects.get( site="CC",name = contest )
        except Contest.DoesNotExist:
            cont = Contest( site="CC",name = contest )
            cont.save()

def get_cf_contest_list():
    '''
    Fetches list of all fineshed contest hosted on/by codeforces.
    '''

    all_contest_url = 'http://codeforces.com/api/contest.list'
    link_file = get_link_fileptr(all_contest_url)
    data = link_file.read()
    data = json.loads(data)
    
    if data['status'] != "OK" :
        get_cf_contest_list()
    else:
        for contest in data['result']:
            if contest['phase'] == 'FINISHED' :
                try:
                    Contest.objects.get( name = contest['name'], site ="CF",contestId=contest['id'] )
                except Contest.DoesNotExist:
                    cont = Contest( name = contest['name'] , site ="CF",contestId = contest['id'] )
                    cont.save()


class codechef:
    def __init__(self,person):
        self.person = person         
        self.handle_name = person.cc   #codechef handle name of the contact.
        self.link_list = []            #links of all questions done by the contact.

    def get_list_of_links(self):
        '''
        Fetches links of all questions done by the contact.

        <a href="Question Url">Question Name</a>
        '''
        url = 'https://www.codechef.com/users/%s'%self.handle_name
        file_ptr = get_link_fileptr(url)
        if file_ptr is not None:
            soup = bs4.BeautifulSoup( file_ptr.read() )
            for link in soup.find_all('a'):
                link = link.get('href')   #data is like written below
                if '/status/' in link:
	                self.link_list.append(link)
        
    
    def get_list_of_ques(self):

        '''
        "/status/TEST,handlename"          for practice problems
        "/OCT14/status/CHEFGR,handlename"  for challenge problems.
        '''
        link_list = self.get_list_of_links()
        for link in self.link_list:
            link_data = link.split('/')
            
            if len(link_data) == 3 :
                '''
                Practice Problem
                '''
                name = link_data[2][0:link_data[2].find(',')]
                try:
                    PracticeProb.objects.get( name = name,person = self.person,site='CC',link=link )
                except PracticeProb.DoesNotExist:
                    prac_prob = PracticeProb( name = name,person = self.person,site='CC',link=link )
                    prac_prob.save()
                    
            elif len(link_data) == 4 :
                '''
                Contest Problem
                '''
                contest_name = link_data[1]
                cont = Contest.objects.filter( name=contest_name,site="CC" )
                name = link_data[3][0:link_data[3].find(',')]
                
                try:
                    Question.objects.get( name=name, person=self.person, contest=cont[0] )
                except Question.DoesNotExist:
                    chal_prob = Question( site='CC', name=name, link=link, person=self.person, contest=cont[0] )
                    chal_prob.save()
                    
    def do_everything(self):
        
        self.get_list_of_ques()
        # you can add functions here to obtain score afterwards

 
class HelperFunctions:
    def __init__(self,request,person_id=None):
        self.request = request

    def FetchContent(self):
        '''
        To update information of all contacts.
        Used by update_info view.
        '''
        people = Person.objects.all()
        if people == []:
            cc_obj = {}
            cf_obj = {}
        else:
            get_cc_contest_list()
            get_cf_contest_list()
            for person in people:
                cc_obj = codechef(person) 
                #new_thread(cc_obj.do_everything,())      #use when multithreading is used.
                if person.cc != None:
                    cc_obj.do_everything()
                cf_obj = codeforces(person)
                #new_thread(cf_obj.do_everything,())     #use when multithreading is used.
                if person.cf != None:
                    cf_obj.do_everything()
    
    def FetchContentForAPerson(self):
        '''
        To update information of a particular contacts accessed by person_id.
        Used by update_a_person_info view.
        '''
        get_cc_contest_list()
        get_cf_contest_list()
        person = Person.objects.filter( pk=person_id )
        cc_obj = codechef( person ) 
        cc_obj.do_everything()
        cf_obj = codeforces(person)
        cf_obj.do_everything()
        
######################################################################

class codeforces:
    def __init__(self,person):
        self.person = person
        self.handle_name = person.cf
        #self.rating_url = 'http://codeforces.com/api/user.rating?handle=%s'%self.handle_name
        self.prob_url = 'http://codeforces.com/api/user.status?handle=%s'%self.handle_name
        
    def get_data(self,url):
        connectTor()
        #proxy = urllib2.ProxyHandler( { 'http' : 'http://Username:Password@ProxyServer:Port' , 'https' : 'https://Username:Password@ProxyServer:Port' })
        auth = urllib2.HTTPBasicAuthHandler()
        opener = urllib2.build_opener( auth, urllib2.HTTPHandler )       #select the opener as required.
        #opener = urllib2.build_opener( proxy,auth, urllib2.HTTPHandler )
        urllib2.install_opener(opener)
        try:
            link_file = urllib2.urlopen(url)
        except urllib2.URLError:
            self.get_data(url)
        else:
            data = link_file.read()
            data = json.loads(data)
            return data
        
    
    
    def finding_problems(self):
        data = self.get_data( self.prob_url )
        
        if data['status'] != "OK" :
            self.finding_problems()
        else:
            for i in data['result']:
                contest_id = i['contestId'] 
                if i['verdict'] == "OK" or i['verdict'] == "PARTIAL" :
                    name = i['problem']['name']
                    index = i['problem']['index']
                    if i['author']['participantType'] == "PRACTICE":
                        try:
                            PracticeProb.objects.get( name = name, person = self.person,site='CF', index =index )
                        except PracticeProb.DoesNotExist:
                            prac_prob = PracticeProb( name = name, person = self.person,site='CF', index =index )
                            prac_prob.save()
                    else:
                        cont = Contest.objects.get( contestId = contest_id )
                        try:
                            Question.objects.get(  index =index, name =name, person =self.person, contest =cont )
                        except Question.DoesNotExist:
                            chal_prob = Question(  index =index, name =name, person =self.person, contest =cont ) 
                            chal_prob.save()
                            

    def do_everything(self):
        self.finding_problems()
        # you can add functions here to obtain score afterwards



# codes for some extra features can be added later
'''
 def contest_timing_(self):
        link_file = self.get_link_fileptr( self.all_contest_url )
        data = link_file.read()
        data = json.loads(data)
        if data['status'] != 'OK' :
            print data['content']      #change has to be made here  i think its comment
        else:
            for i in data['result']:
                self.contest_timing[ i['id'] ] = i['startTimeSeconds'] + i['durationSeconds']  #has info abount when the contest ended.
    
    def finding_rating(self):       #gives rating of all participated contests
        link_file = self.get_link_fileptr( self.rating_url )
        data = link_file.read()
        data = json.loads(data)
        if data['status'] != 'OK':
            print data['comment']
        else:
            for i in data['result']:
                self.contest_rating.append((i['contestId'],i['contestName'],i['newRating']))
        print 'last done'

'''
