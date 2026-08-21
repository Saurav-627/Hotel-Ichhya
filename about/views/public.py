from django.shortcuts import render
from django.views.generic import View
from about.models import AboutPage, TeamMember, AboutFacility


class AboutPageView(View):
    def get(self, request):
        about_page = AboutPage.objects.first()
        if not about_page:
            about_page = AboutPage.objects.create()
            
        team_members = TeamMember.objects.filter(is_published=True).order_by('order', 'id')
        facilities = AboutFacility.objects.filter(is_published=True).order_by('order', 'id')

        return render(request, 'about/about.html', {
            'about_page': about_page,
            'team_members': team_members,
            'facilities': facilities,
        })
