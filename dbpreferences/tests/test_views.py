
from django.db.models import signals
from django.http import HttpResponse
from dbpreferences.models import UserSettings

save_count = 0
def post_save_handler(sender, **kwargs):
    global save_count
    save_count += 1

init_count = 0
def pre_init_handler(*args, **kwargs):
    global init_count
    init_count += 1

def test_user_settings(request, test_name, key, value):
    if test_name == "base_test":
        output = key + value
    elif test_name == "get":
        output = request.user_settings.get(key, value)
    elif test_name == "setitem":
        output = request.user_settings[key] = value
    else:
        raise

    return HttpResponse(output, mimetype="text/plain")



def test_user_settings_cache(request, no):
    signals.post_save.connect(post_save_handler, sender=UserSettings)
    signals.pre_init.connect(pre_init_handler, sender=UserSettings)

    should_value = "initial value"
    value = request.user_settings.get("test", "initial value")

    if no == "0":
        # First call
        should_save_count = 0
        should_init_count = 0
    elif no == "1":
        # second call
        should_save_count = 1
        should_init_count = 1
    elif no in ("2", "3", "4"):
        # Use cached Version
        should_save_count = 1
        should_init_count = 1
    elif no == "5":
        # Change the value
        request.user_settings["test"] = "new value"
        should_value = "new value"
        should_save_count = 1
        should_init_count = 1
    else:
        # After 5
        should_value = "new value"
        should_save_count = 2
        should_init_count = 1

    global save_count
    assert save_count == should_save_count, "Wrong save count %r (should %r) in no %r" % (
        save_count, should_save_count, no
    )

    global init_count
    assert init_count == should_init_count, "Wrong init count %r (should %r) in no %r" % (
        init_count, should_init_count, no
    )

    return HttpResponse(no, mimetype="text/plain")
