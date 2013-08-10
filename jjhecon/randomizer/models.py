from django.db import models

class Redirection(models.Model):
    experiment_name = models.CharField(max_length=200)
    landing_hash = models.CharField(max_length=200)
    admin_hash = models.CharField(max_length=200)
    is_stratified = models.BooleanField()

    # the last visited target URL
    last_target_index = models.IntegerField(default=-1)

    
class Target(models.Model):
    url = models.URLField(max_length=200)
    redirection = models.ForeignKey('Redirection')
    date = models.DateField(auto_now_add=True)
    
class Visit(models.Model):
    redirection = models.ForeignKey('Redirection')
    target = models.ForeignKey('Target')
    ip = models.IPAddressField()
    