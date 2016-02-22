from django.views.generic.edit import FormMixin
from django.views.generic.edit import ProcessFormView
from django.views.generic.base import View
from django.views.generic.base import TemplateResponseMixin

class MultiFormMixin(FormMixin):
    """
    A mixin that provides a way to show and handle a form in a request
    """
    form_class_list = {}
    def get_form_class_list(self):
        """
        Returns the classes to use in this view
        """
        return self.form_class_list

    def get_form_list(self, form_class_list):
        forms = {}
        print self.get_form_kwargs()
        for form_name, form in form_class_list.iteritems():
            forms[form_name] = form(**self.get_form_kwargs()[form_name])
        return forms

    def forms_valid(self, forms):
        """
        If the forms are valid, redirect to the supplied url. No modification
        here, use inherited method. This method is here in case one wants to
        return a different url based on content.
        """
        return super(MultiFormMixin, self).form_valid(forms)

    def forms_invalid(self, forms):
        """
        If the forms are invalid, re-render the context data with the
        data-filled form and errors.
        """
        print "forms_invalid"
        print self.get_context_data(**forms)
        return self.render_to_response(self.get_context_data(**forms))

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instatitating the form.
        """
        initial = self.get_initial()
        prefix = self.get_prefix()
        kwargs = {}
        form_class_list = self.get_form_class_list()
        for form_name in form_class_list:
            kwargs[form_name] = {}
            if initial:
                kwargs[form_name]["initial"] = initial.get(form_name)
            if prefix:
                kwargs[form_name]["prefix"] = prefix.get(form_name)

        if self.request.method in ('POST', 'PUT'):
            for form_name in form_class_list:
                kwargs[form_name].update({
                    "data": self.request.POST,
                    "files": self.request.FILES,
                })

        return kwargs
class ProcessMultiFormView(ProcessFormView):
    """
    A mixin that renders forms on GET and processes them on POST.
    """

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests and instantiates a blank version of the form.
        """
        form_class_list = self.get_form_class_list()
        forms = self.get_form_list(form_class_list)

        return self.render_to_response(self.get_context_data(**forms))

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests and instantiates a form instance with the passed
        POST variables and then checked for validity
        """
        form_class_list = self.get_form_class_list()
        forms = self.get_form_list(form_class_list)
        invalid = False
        for name, form in forms.iteritems():
            if form.is_valid():
                pass
            else:
                invalid = True
        if invalid:
            return self.forms_invalid(forms)
        else:
            return self.forms_valid(forms)

class MultiBaseFormView(MultiFormMixin, ProcessMultiFormView):
    """
    A base view for displaying multiple forms
    """

class MultiFormView(TemplateResponseMixin, MultiBaseFormView):
    """
    A view for displaying multiple forms, and rendering a template response
    """
