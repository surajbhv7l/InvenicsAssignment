from django.db import models

"""
Blob class:- to store records  of blobs file
Mention class: to store records of mentions and urls
"""

class Blob(models.Model):
    id = models.IntegerField(primary_key=True)
    blob = models.CharField(max_length=100,unique=True,null=False)
    date = models.DateField()

    def __str__(self):
        return f'Blob Name = {self.blob } Date = {self.date }'

class Mention(models.Model):
    id = models.IntegerField(primary_key=True)
    blob_id = models.ForeignKey(Blob,db_column='blob_id',null=False,on_delete=models.CASCADE)
    rank = models.IntegerField(null=False)
    mention = models.TextField(null=False)
    
    url = models.TextField(null=False)

    class Meta:
        indexes = [models.Index(fields=['blob_id','rank'])]


    def __str__(self):
        return f'Blob Name = {self.blob} Mention = {self. menthion} Position = {self.position} Url = {self.url}'



