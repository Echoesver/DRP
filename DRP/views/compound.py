'''A module containing views pertinent to compound objects'''

from django.contrib.auth.models import User
from django.views.generic import CreateView, ListView
from DRP.models import Compound
from DRP.forms import CompoundForm, LabGroupSelectionForm
from django.utils.decorators import method_decorator
from decorators import userHasLabGroup, hasSignedLicense
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy as reverse
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.utils.http import urlencode


class CreateCompound(CreateView):
  '''A view managing the creation of compound objects'''

  model=Compound
  form_class = CompoundForm
  template_name='compound_form.html'
  success_url=reverse('compoundguide')
 
  def get_form_kwargs(self):
    '''Overridden to add the request.user value into the kwargs'''
    kwargs = super(CreateCompound, self).get_form_kwargs() 
    kwargs['user']=self.request.user
    return kwargs

  @method_decorator(login_required)
  @method_decorator(hasSignedLicense)
  @method_decorator(userHasLabGroup)
  def dispatch(self, request, *args, **kwargs):
    '''Overridden with a decorator to ensure that a user is at least logged in'''
    return super(CreateCompound, self).dispatch(request, *args, **kwargs)

  def get_context_data(self, **kwargs):
    context = super(CreateCompound, self).get_context_data(**kwargs)
    context['page_heading'] = 'Add a New Compound'
    return context
    
class ListCompound(ListView):
  '''A view managing the viewing of the compound guide'''

  template_name='compound_list.html'
  context_object_name='compounds'

  @method_decorator(login_required)
  @method_decorator(hasSignedLicense)
  @method_decorator(userHasLabGroup)
  def dispatch(self, request, *args, **kwargs):
    '''Overriden with a decorator to ensure that user is logged in and has at least one labGroup
    Relates the queryset of this view to the logged in user.
    '''
    
    self.lab_form = LabGroupSelectionForm(request.user)
    if request.user.labgroup_set.all().count() > 1:
      if 'labgroup_id' in request.session and request.user.labgroup_set.filter(pk=request.session['labgroup_id']).count() > 1:
        self.queryset = request.user.labgroup_set.get(pk=request_session['labgroup_id']).compound_set.all()
        self.lab_form.fields['labGroup'].initial = request.session['labgroup_id']
      else:
        return redirect(reverse('selectGroup') + '?{0}'.format(urlencode({'next':request.path_info})))
    else:
      #user only has one labgroup, so don't bother asking which group's compoundlist they want to look at.
      self.queryset = request.user.labgroup_set.all()[0].compound_set.all()
    return super(ListCompound, self).dispatch(request, *args, **kwargs)

  def get_context_data(self, **kwargs):
    context = super(ListCompound, self).get_context_data(**kwargs)
    context['lab_form'] = self.lab_form
    return context

