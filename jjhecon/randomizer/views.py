# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect, QueryDict, HttpResponseNotFound
from django.shortcuts import render_to_response, get_object_or_404
from django.utils import simplejson as json
from django import forms
from jjhecon.randomizer.models import Redirection, Target, Visit
import random, urllib, cgi, string
from urlparse import urlparse, urlunparse, urljoin
import jjhecon.settings
# from google.appengine.api import datastore_errors

base_url = jjhecon.settings.BASE_URL 
# base_url = 'http://localhost:8000/'
# ip_checking = True

if jjhecon.settings.DEBUG == True:
    ip_checking = False
else:
    ip_checking = True

# TODO
# handle invalid URLs better.

# class BadUrlException(datastore_errors.BadValueError):
#     def __init__(self, value):
#         self.value = value
#     def __str__(self):
#         return repr(self.value)

class RedirectionForm(forms.Form):
    experiment_name = forms.CharField(label = "Experiment name")
    targets = forms.CharField(label = "Target URLs", widget=forms.Textarea(attrs={'rows': '10', 'cols': '70'}))
    stratify = forms.BooleanField(label = "Stratify", required = False)

def sandbox(request):
    return render_to_response("sandbox.html", {})

    
    
def json_view(request):
    # input format:
    
    # d["targets"] must be a list of 1 or more URLs. if "stratify" exists, it must be a boolean.
    d = json.loads(request.raw_post_data)
    # verify the validity of the input
    redirection_info = create_randomization(request, d)
    if isinstance(redirection_info, HttpResponse):
        return redirection_info
    return HttpResponse(json.dumps(redirection_info),
        mimetype="application/json")

def html_view(request):
    action = '/r/.html/'
    if request.method == 'POST':
        form = RedirectionForm(request.POST)
        
        if form.is_valid():
            
            d = {'targets': [target.strip() for target in form.cleaned_data['targets'].split('\n') if target.strip()],
                'stratify': True if form.cleaned_data['stratify'] == True else False,
                'experiment_name': form.cleaned_data['experiment_name']}
                
            redirection_info = create_randomization(request, d)
            if isinstance(redirection_info, HttpResponse):
                response = redirection_info #
                return response
            return render_to_response("redirection.html", {'form': form, 
                'action': action, 
                'landing_url': redirection_info['landing_url'],
                'admin_url': redirection_info['admin_url']})
    else:
        form = RedirectionForm()
        return render_to_response("redirection.html", {'form': form, 'action': action})
        
    dynamic_html = dynamic_fields_template.render(Context({'form':form}))
    return render_to_response("redirection.html", 
        {'form': form, 'dynamic_html': dynamic_html, 'action': action})
        #context_instance=RequestContext(request)) # not sure what this is for

def create_randomization(request, d):
    # input schema:
    # {'experiment_name': str, 'targets': ['url1', 'url2', 'url3', ...], 'stratify': bool}
    

    if len(d['targets']) == 0:
        return HttpResponseNotFound('You must enter at least one URL.')
        
    redirection = Redirection(experiment_name = d['experiment_name'],
            landing_hash = create_hash(),
            admin_hash = create_hash(),
            is_stratified = d.get('stratify') == True)
    redirection.save()
    for url in d["targets"]:
        try:
            target = Target(url = url, redirection = redirection)
            target.save()
        except forms.ValidationError:
            return HttpResponseNotFound('One or more of the target URLs you entered were malformed.')
    return {'landing_url': make_landing_url(redirection.landing_hash),
            'admin_url': make_admin_url(redirection.admin_hash)}
    
def visit(request, landing_hash):
    redirection = Redirection.objects.get(landing_hash=landing_hash)
    if redirection:
        # check if the person has already visited
        previous_visits = Visit.objects.filter(ip=request.META["REMOTE_ADDR"], redirection=redirection)
        if previous_visits and ip_checking:
            # they're going to the place they went last time
            target = previous_visits[0].target
        else:
            if redirection.is_stratified:
                # find the last visited URL
                this_target_index = (redirection.last_target_index + 1) % redirection.target_set.count()
                target = redirection.target_set.order_by("date")[this_target_index] # TODO: is order preserved? also, is there a more efficient way?
                redirection.last_target_index = this_target_index
                redirection.save()
            else:
                target = random.choice(redirection.target_set.all())
        
        # append any URL parameters to the URL
        reconstructed_url = combine_queries(str(target.url), request.GET)
        
        # record visit
        visit = Visit(redirection = redirection, target = target, ip = request.META["REMOTE_ADDR"])
        visit.save()
        
        return HttpResponseRedirect(reconstructed_url)

def admin(request, admin_hash):
    redirection = Redirection.objects.all().get(admin_hash=admin_hash)
    if redirection:
        # targets should be a list of dicts with stats on the different targets.
        if redirection.is_stratified:
            method = 'Stratify'
        else:
            method = 'Randomize'
        targets = []
        for target in redirection.target_set.all():
            num_visits = Visit.objects.all().filter(redirection=redirection, target=target).count()
            targets.append({'url': target.url, 'num_visits': num_visits})
        
        return render_to_response('admin.html',
            {'method': method,
            'targets': targets,
            'landing_url': make_landing_url(redirection.landing_hash)})
             
def make_landing_url(landing_hash):
    return urljoin(base_url, '/r/' + landing_hash)

def make_admin_url(admin_hash):
    return urljoin(base_url, '/r/a/' + admin_hash)

    
def combine_queries(target_url, request_get):
    target_url_parsed = list(urlparse(target_url))
    target_url_query = QueryDict(target_url_parsed[4]).copy()
    target_url_query.update(request_get)
    target_url_parsed[4] = target_url_query.urlencode()
    reconstructed_url = urlunparse(target_url_parsed)
    return reconstructed_url

def create_hash(size = 9):
	return ''.join([random.choice(string.letters + string.digits) for i in range(size)])
