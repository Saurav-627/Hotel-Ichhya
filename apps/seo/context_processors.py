from django.db.utils import ProgrammingError, OperationalError
from .models.seo_data import SEOData

def seo_meta(request):
    meta = {
        'title': 'Hotel Ichha | Premium Five-Star Luxury Hotel & CMS',
        'description': 'Experience ultimate luxury, fine dining, and elite wellness spas at Hotel Ichha, a five-star international standard resort.',
        'canonical': request.build_absolute_uri(),
        'og_title': 'Hotel Ichha | Five-Star Luxury Hotel',
        'og_description': 'Experience ultimate luxury, fine dining, and elite wellness spas.',
        'og_image': '',
        'twitter_card': 'summary_large_image',
        'structured_data': ''
    }
    
    try:
        # Match current path (e.g. /rooms/ or /contact/)
        seo_obj = SEOData.objects.filter(path=request.path).first()
        if not seo_obj and request.path != '/':
            # Try to match fallback home path '/'
            seo_obj = SEOData.objects.filter(path='/').first()

        if seo_obj:
            meta['title'] = seo_obj.meta_title
            meta['description'] = seo_obj.meta_description
            meta['canonical'] = seo_obj.canonical_url or request.build_absolute_uri()
            meta['og_title'] = seo_obj.og_title or seo_obj.meta_title
            meta['og_description'] = seo_obj.og_description or seo_obj.meta_description
            if seo_obj.og_image:
                meta['og_image'] = request.build_absolute_uri(seo_obj.og_image.url)
            meta['twitter_card'] = seo_obj.twitter_card
            meta['structured_data'] = seo_obj.structured_data
    except (ProgrammingError, OperationalError):
        pass

    return {'seo': meta}
