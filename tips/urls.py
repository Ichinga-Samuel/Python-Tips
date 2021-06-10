from tips.views import TipsView, TipDetail, TagsView, SearchView, like
from django.urls import path


app_name = 'tips'

urlpatterns = [
    path('like/<int:pk>', like, name='like'),
    path('tags/<tag>/', TagsView.as_view(), name='tag'),
    path('search/', SearchView.as_view(), name='search'),
    path('', TipsView.as_view(), name='main'),
    path('tips/<int:pk>/', TipDetail.as_view(), name='tip'),
]

