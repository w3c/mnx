from spec.models import SiteOptions

def site_options(request):
    try:
        so = SiteOptions.objects.all()[0]
    except IndexError:
        so = None
    return {'SITE_OPTIONS': so}
