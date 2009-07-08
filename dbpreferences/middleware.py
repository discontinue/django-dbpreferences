
from dbpreferences.models import UserSettings



class SettingsDict(dict):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        self.modified = False
        self._loaded = False
        self._model_instance = None
        super(SettingsDict, self).__init__(*args, **kwargs)
#
#    def getvalue(self, **kwargs):
#        self.load()
#        for key, value in kwargs.iteritems():
#            if not key in self:
#                self[key] = value

    def get(self, key, default):
        self.load()
        if not key in self:
            self[key] = default

        return self[key]

    def __getitem__(self, key):
        self.load()
        return dict.__getitem__(self, key)

    def __setitem__(self, key, value):
        self.modified = True
        dict.__setitem__(self, key, value)

    def load(self):
        if self._loaded:
            return

        print "load:",
        try:
            self._model_instance, settings_dict = UserSettings.objects.get_settings(self.user)
        except UserSettings.DoesNotExist:
            self.modified = True # Create it at the end
        else:
            # Use existing data
            settings_dict = self._model_instance.get_settings()
            print settings_dict
            dict.update(self, settings_dict)

    def save(self):
        """ Save the current settings into database """
        if self._model_instance == None:
            self._model_instance, created = UserSettings.objects.get_or_create(user=self.user,
                defaults={"settings": self, "createby": self.user, "lastupdateby": self.user}
            )
            if created:
                print "UserSettings created."
                return

        print "UserSettings updated."
        self._model_instance.settings = self
        self._model_instance.save()


class DBPreferencesMiddleware(object):
    def process_request(self, request):
        request.user_settings = SettingsDict(request.user)

    def process_response(self, request, response):
        """ If user settings changes -> save it into database """
        try:
            modified = request.user_settings.modified
        except AttributeError:
            pass
        else:
            if modified:
                print "was modified -> save"
                request.user_settings.save()

        return response
