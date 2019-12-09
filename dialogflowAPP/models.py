from django.db import models

# Create your models here.

class InfraLog(models.Model):
    '''Infra Log'''
    action = models.CharField(max_length=50)
    content = models.CharField(max_length=33)

class ApplicationLog(models.Model):
    '''Application Log'''
    lineuserid = models.CharField(max_length=33)
    action = models.CharField(max_length=50)
    country = models.CharField(max_length=2)
    keyword = models.CharField(max_length=500)
    result_num = models.DecimalField(max_digits=2, decimal_places=0)

class BusinessLog(models.Model):
    '''Business Log'''
    lineuserid = models.CharField(max_length=33)
    action = models.CharField(max_length=50)

class OperationLog(models.Model):
    '''Operation Log'''
    server = models.CharField(max_length=33)
    deploy_time = models.DateTimeField()
