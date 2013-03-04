from django.conf import settings

# Look for Metadata subclasses in appname/seo.py files
for app in settings.INSTALLED_APPS:
    try:
        module_name = '%s.observers' % str(app)
        __import__(module_name)
    except ImportError:
        pass
