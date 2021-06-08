from django.db import models
from django.urls import reverse


class Tips(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    tip = models.TextField(unique_for_date='timestamp', max_length=400)
    email = models.EmailField(max_length=254, blank=True)
    account = models.CharField(max_length=200, blank=True)
    likes = models.IntegerField(blank=True, null=True)
    retweets = models.IntegerField(blank=True, null=True)
    tags = models.ManyToManyField('Tags', blank=True)

    def __str__(self):
        return f"{' '.join(self.tip.split(' ', 2)[:2]).strip().title()}"

    def get_absolute_url(self):
        return reverse('tips:tip', kwargs={'pk': self.pk})

    class Meta:
        ordering = ('-likes', '-retweets', '-timestamp')


class Links(models.Model):
    name = models.CharField(max_length=256)
    tip = models.ForeignKey(Tips, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return f'{self.name}'


class Tags(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return f'{self.name}'
