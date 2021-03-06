from django.template import RequestContext
from django.shortcuts import render_to_response
#from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from cal_util.view_util import get_common_lookup


def view_logout_page(request):

    lu = get_common_lookup(request)

    cal_user = lu.get('calendar_user', None)
    
    if not request.user.is_authenticated():
        lu.update({ 'ERR_found' : True, 'ERR_already_logged_out' : True })
        return render_to_response('hu_authz_handler/view_authz_logout.html', lu, context_instance=RequestContext(request))
    
    try:
        logout(request)
        return view_logout_success_page(request)
    except:
        return render_to_response('hu_authz_handler/view_authz_logout.html', lu, context_instance=RequestContext(request))




def view_logout_success_page(request):
    
    lu = get_common_lookup(request)

    cal_user = lu.get('calendar_user', None)

    lu.update({ 'logout_success' : True})
    
    return render_to_response('hu_authz_handler/view_authz_logout.html', lu, context_instance=RequestContext(request))
    
    #return render_to_response('login/logout_page.html', lu, context_instance=RequestContext(request))
        
