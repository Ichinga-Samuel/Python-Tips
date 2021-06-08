from django.shortcuts import render
from django.views.generic import ListView, TemplateView, DetailView
from tips.models import Tips, Tags, Links


class TipsView(ListView):
    template_name = 'tips/home.html'
    context_object_name = 'tips'
    model = Tips
    paginate_by = 20


class TipDetail(DetailView):
    template_name = 'tips/tip_detail.html'
    model = Tips

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        tags = self.object.tags.all()
        if tags:
            tags = [Tags.objects.filter(name__exact='%s' %tag.name) for tag in tags]
            tips_set = [i.tips_set.all() for tag in tags for i in tag]
            tips_ = [tip for tips in tips_set for tip in tips]
            context['rel_tips'] = tips_[:10]
        context['recent'] = Tips.objects.all()[:5]

        return context


class TagsView(TemplateView):

    context_object_name = 'tips'
    template_name = 'tips/tags.html'

    def get_queryset(self):
        tag = self.kwargs['tag']
        try:
            self.tags = Tags.objects.filter(name__iregex=r'.*%s.*' %tag)
            self.tips = Tips.objects.filter(tip__iregex=r'.*%s.*' %tag)
        except Exception as err:
            self.tags, self.tips = [], []
            print(err)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.get_queryset()
        tips = [i.tips_set.all() for i in self.tags]
        s1 = [tip for tipq in tips for tip in tipq]
        context['tips'] = {*s1, *self.tips}
        context['tag'] = self.kwargs['tag']

        return context


class SearchView(TemplateView):

    template_name = 'tips/search.html'

    def get_queryset(self):
        tag = self.request.GET.get('q', '')
        self.query = tag
        try:
             self.tags = Tags.objects.filter(name__iregex=r'.*%s.*' % tag)   # No search Results for
             self.tips = Tips.objects.filter(tip__iregex=r'.*%s.*' % tag)
        except Exception as err:
            self.tags, self.tips = [], []
            print(err)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.get_queryset()
        tips = [i.tips_set.all() for i in self.tags]
        s1 = [tip for tipq in tips for tip in tipq]
        tips = {*s1, *self.tips}
        context['tips'] = tips
        context['query'] = self.query
        if not tips:
            context['res'] = Tips.objects.all()[:20]
        return context
