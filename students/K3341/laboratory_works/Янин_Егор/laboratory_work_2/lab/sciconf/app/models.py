from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Location(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.name

class Theme(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Conference(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default="")
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    themes = models.ManyToManyField(Theme)
    start_date = models.DateField()
    end_date = models.DateField()
    participation_terms = models.TextField()

    def __str__(self):
        return self.name

class TalkSubmission(models.Model):
    title = models.CharField(max_length=200)
    abstract = models.TextField()
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE)
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    recommended_to_publish = models.BooleanField(default=None, null=True, blank=True)

    def __str__(self):
        return self.title

class ConferenceReview(models.Model):
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE)
    reviewer = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    review_text = models.TextField()
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
        )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer} for {self.conference}"

class Profile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username