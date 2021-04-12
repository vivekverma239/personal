# Create your models here.
import uuid
from django.db import models

from django.contrib.postgres.fields import JSONField, ArrayField
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from rest_framework.decorators import action


# User = get_user_model()

# class Constant(models.Model): 
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     key = models.CharField(max_length=255)
#     data = JSONField(default=dict)  
#     createdAt = models.DateTimeField(db_column='createdAt', auto_now_add=True)
#     updatedAt = models.DateTimeField(db_column='updatedAt', auto_now=True)


# class StockData(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     datetime  = models.DateTimeField(db_column='datetime')
#     res = models.CharField(max_length=10)
#     stock_symbol = models.CharField(max_length=255)
#     open = models.DecimalField(max_digits=20, decimal_places=2)
#     close = models.DecimalField(max_digits=20, decimal_places=2)
#     low = models.DecimalField(max_digits=20, decimal_places=2)
#     high = models.DecimalField(max_digits=20, decimal_places=2)
#     volume = models.BigIntegerField()
#     createdAt = models.DateTimeField(db_column='createdAt', auto_now_add=True)
#     updatedAt = models.DateTimeField(db_column='updatedAt', auto_now=True)


# class StrategyConfig(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     key = models.CharField(max_length=10)
#     data = JSONField(default=dict) 

# class StrategySignal(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     datetime  = models.DateTimeField(db_column='datetime')
#     stock_symbol = models.CharField(max_length=255)
#     res = models.CharField(max_length=10)
#     strategy_name = models.CharField(max_length=100)
#     createdAt = models.DateTimeField(db_column='createdAt', auto_now_add=True)
#     updatedAt = models.DateTimeField(db_column='updatedAt', auto_now=True)
#     signal = models.CharField(max_length=10)
#     data = JSONField(default=dict) 
#     score = models.DecimalField(max_digits=20, decimal_places=2)

# class SearchFile(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     file = models.FileField(blank=False, null=True)
#     parsed_data = JSONField(default=dict)
#     policy_doc = JSONField(default=dict)
#     name = models.CharField(max_length=1000)
#     status = models.CharField(max_length=1000, default='pending')
#     metadata = JSONField(default=dict) 


#     createdAt = models.DateTimeField(db_column='createdAt', auto_now_add=True)
#     updatedAt = models.DateTimeField(db_column='updatedAt', auto_now=True)

#     def __str__(self):
#         return self.file.name

