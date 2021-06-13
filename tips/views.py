from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.shortcuts import render
from django.db.models import Q
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
            tips_set = [tag.tips_set.all() for tag in tags]
            tips_ = [*{tip for tips in tips_set for tip in tips}]  # use set to remove duplicates
            context['rel_tips'] = tips_[:10]
        context['recent'] = Tips.objects.all()[:5]
        return context


class TagsView(TemplateView):

    context_object_name = 'tips'
    template_name = 'tips/tags.html'

    def get_queryset(self):
        tag = self.kwargs['tag']
        try:
            self.tips = Tips.objects.filter(Q(tip__iregex=r'.*%s.*' %tag)|Q(tags__name__iregex=r'.*%s.*' %tag)).distinct()
        except Exception as err:
            self.tips = []
            print(err)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.get_queryset()
        context['tips'] = self.tips
        context['tag'] = self.kwargs['tag']

        return context


class SearchView(TemplateView):

    template_name = 'tips/search.html'

    def get_queryset(self):
        tag = self.request.GET.get('q', '')
        self.query = tag
        try:
             self.tips = Tips.objects.filter(Q(tip__iregex=r'.*%s.*' %tag)|Q(tags__name__iregex=r'.*%s.*' %tag)).distinct()
        except Exception as err:
            self.tips = []
            print(err)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.get_queryset()
        context['tips'] = self.tips
        context['query'] = self.query
        if not self.tips:
            context['res'] = Tips.objects.all()[:20]
        return context


@login_required
def like(request, pk):
    pro = request.user.profile
    tip = Tips.objects.get(pk=pk)
    if tip not in pro.favourites.all():
        pro.favourites.add(tip)
        pro.save()
        tip.likes += 1
        tip.save()
    return JsonResponse({'update': tip.likes})


@login_required
def dislike(request, pk):
    pro = request.user.profile
    tip = Tips.objects.get(pk=pk)
    if tip in pro.favourites.all():
        pro.favourites.remove(tip)
        pro.save()
    tip.retweets += 1
    tip.save()
    return JsonResponse({'update': tip.retweets})

