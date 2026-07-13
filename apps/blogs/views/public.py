from django.views.generic import ListView, DetailView
from ..models.post import BlogPost

class BlogListView(ListView):
    model = BlogPost
    template_name = 'blogs/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        return BlogPost.objects.filter(is_active=True)

class BlogDetailView(DetailView):
    model = BlogPost
    template_name = 'blogs/blog_detail.html'
    context_object_name = 'post'
    slug_url_kwarg = 'slug'
