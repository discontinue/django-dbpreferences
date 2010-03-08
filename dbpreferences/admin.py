# coding: utf-8

"""
    dbpreferences.admin
    ~~~~~~~~~~~~~~~~~~~


    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
from django.contrib import admin
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.conf.urls.defaults import patterns, url
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, render_to_response

from dbpreferences.models import Preference
from dbpreferences.tools import forms_utils

#------------------------------------------------------------------------------

class PreferenceAdmin(admin.ModelAdmin):
    list_display = ("site", "app_label", "form_name", "lastupdatetime", "lastupdateby", "edit_link")
    list_display_links = ("form_name",)
    list_filter = ("site", "app_label",)
    search_fields = ("site", "app_label", "form_name",)

    def has_add_permission(self, request):
        """
        Deny add permission for every user. Becuase manually adding a
        preferences makes no sence, yet. (This hides the add button)
        
        Every user can only change existing preferences. Preferences entry are
        added automatically by first accessing the preferences form.
        
        TODO: If the forms must be registered, we can create all preferences
        into database on first startup.
        see also:
        http://code.google.com/p/django-dbpreferences/issues/detail?id=5
        """
        return False

    def edit_link(self, instance):
        """ For adding a edit link into django admin interface """
        context = {
            "instance": instance,
        }
        return render_to_string('dbpreferences/model_admin_edit_link.html', context)
    edit_link.allow_tags = True

    def edit_form(self, request, pk):
        """ edit a preference entry using the associated form """

        obj = get_object_or_404(Preference, pk=pk)
        form_class = obj.get_form_class()

        if request.method == 'POST':
            form = form_class(request.POST)
            if form.is_valid():
                # save new preferences
                obj.preferences = form.cleaned_data
                obj.lastupdateby = request.user
                obj.save()

                msg = "Preferences %s updated." % obj
                self.log_change(request, obj, msg)

                if request.POST.has_key("_continue"):
                    msg += ' ' + _("You may edit it again below.")

                    if request.REQUEST.has_key('_popup'):
                        next_url = request.path + "?_popup=1"
                    else:
                        next_url = request.path
                else:
                    next_url = reverse("admin:dbpreferences_preference_changelist")

                self.message_user(request, msg)
                return HttpResponseRedirect(next_url)
        else:
            preferences = obj.preferences
            form = form_class(preferences)

        # Append initial form values into all field help_text
        forms_utils.setup_help_text(form)

        context = {
            "title": _('Change %s') % obj,
            "obj": obj,
            "form_url": request.path,
            "form": form,
        }
        return render_to_response("dbpreferences/edit_form.html", context,
            context_instance=RequestContext(request))

    def get_urls(self):
        """ add own edit view into urls """
        urls = super(PreferenceAdmin, self).get_urls()
        my_urls = patterns('',
            url(r'^(?P<pk>\d+)/edit_form/$', self.admin_site.admin_view(self.edit_form),
            name="dbpref_edit_form")
        )
        return my_urls + urls



admin.site.register(Preference, PreferenceAdmin)
