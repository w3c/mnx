from spectools.models import SiteOptions

def docs_global_variables(request):
    try:
        so = SiteOptions.objects.all()[0]
    except IndexError:
        so = None
    return {
        'SITE_OPTIONS': so,
    }
