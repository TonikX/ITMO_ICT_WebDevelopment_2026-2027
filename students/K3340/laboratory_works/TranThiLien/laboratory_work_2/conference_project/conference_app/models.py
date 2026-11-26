from django.db import models
from django.conf import settings


class Conference(models.Model):
    title       = models.CharField(max_length=200)
    topics      = models.ManyToManyField('Topic', through='ConferenceTopic', blank=True)
    venue       = models.CharField(max_length=200)
    venue_ref   = models.ForeignKey('Venue', on_delete=models.SET_NULL, null=True, blank=True)
    start_date  = models.DateField()
    end_date    = models.DateField()
    description = models.TextField()
    venue_desc  = models.TextField()
    conditions  = models.TextField()

    def __str__(self):
        return self.title


class Topic(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Venue(models.Model):
    name    = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    desc    = models.TextField(blank=True)

    def __str__(self):
        return self.name


class ConferenceTopic(models.Model):
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE)
    topic      = models.ForeignKey(Topic, on_delete=models.CASCADE)
    order      = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']


class Registration(models.Model):
    STATUS_CHOICES = (
        ('pending',  'Ожидает утверждения'),
        ('approved', 'Утверждено'),
        ('rejected', 'Отклонено'),
    )
    conference   = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name='registrations')
    author       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    report_title = models.CharField(max_length=300)
    abstract     = models.TextField()
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    recommended  = models.BooleanField(default=False, help_text='Đề xuất công bố')
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('conference', 'author')

    def __str__(self):
        return f'{self.author} — {self.report_title}'


class Review(models.Model):
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name='reviews')
    author     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text       = models.TextField()
    rating     = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 11)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.author} — {self.rating}/10'