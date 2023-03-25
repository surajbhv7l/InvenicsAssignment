import datetime
from django.shortcuts import render
from django.http import JsonResponse#  serializer
from getMentions.models import Mention as m
from getMentions.models import Blob as b
from getMentions.serializers import mentionSerializer as ser
from getMentions.serializers import blobSerializer as bser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django_filters.rest_framework import filters
import os
import pandas as pd
from datetime import date
import gzip
from io import BytesIO
from azure.storage.blob import BlobServiceClient as bs
from django.db.models import Q



# Created views for handling post and get request from clinets.
@api_view(['GET','POST'])
def grabMentions(request):
    if request.method == 'POST':
        try:
            # get blob id from blob table using blob name
            blobIDFromB = b.objects.filter(blob = request.data['blob']).first().id
            #get lower rank of the range from the request
            requestedRankLower = int(request.data['lower'])
            #get upper rank of the range from the request
            requestedRankUpper = int(request.data['upper'])
            # fetch corresponding entries from mention using indexes such as blob id, and rank
            mentions=m.objects.select_related('blob_id').filter(Q(blob_id__id=blobIDFromB) & Q(rank__range=(requestedRankLower,requestedRankUpper)))
            
            serializer = ser(mentions,many= True)
            
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'GET':
        try:
            blobs = b.objects.all()
            serializer = bser(blobs,many= True)
            return Response(serializer.data,status=status.HTTP_200_OK)
            
        except Exception:
            return Response(status=status.HTTP_404_NOT_FOUND)

"""
getSaveBlobData connects with the azure container
     for each blob files in the azure container: iterate
           unzip the file, encode it using utf-8
           For each line the file , split it into fileds
               grab mention and urls using fileds id
               create a list  of mention object
               bulk create if there are 3000 objets entries

            
"""


def getSaveBlobData():
    
    
    account_url = "https://casestudy01.blob.core.windows.net/"
    container_name = "wikipedia"
    # clear all previous records form the mention and blob table
    m.objects.all().delete()
    b.objects.all().delete()
    try:
        blob_service_client = bs(account_url=account_url)


        container_client = blob_service_client.get_container_client(container_name)

        blob_list = container_client.list_blobs()
        mention_id = 1
        idForBlobTable = 1

        
        for blob in blob_list:
            print(blob.name,idForBlobTable)
            
            blob_client = container_client.get_blob_client(blob)
            blob_contents = blob_client.download_blob()
            # uncompress the data
            compressed_data = BytesIO(blob_contents.content_as_bytes())


            unzipped_data = gzip.GzipFile(fileobj=compressed_data).read()


            f = BytesIO(unzipped_data)
            
            blob_obj =b.objects.create(id = idForBlobTable,blob = blob.name,date = date.today()) 
            mentionObject = []
            rank = 1
            
            for line in f:
                
                fields = line.decode('utf-8').strip().split('\t')
                if fields[0] == 'MENTION':

                    mention = fields[1].encode('utf-8')
            
                    target_url = fields[3].encode('utf-8')
                    
                    mentionObject.append(m(id = mention_id,blob_id= blob_obj,rank = rank,mention = mention,url = target_url))
                    
                    # create bulk insert having 3000 records each time
                    if rank % 3000 == 0:
                        
                        #encoded_objects = [m(mention=mentionObject[i].mention.encode('utf-8')) for i in range(len(mentionObject))]
                        m.objects.bulk_create(mentionObject) 
                        print(" Three throusands objects successfully put",rank,mention_id,idForBlobTable)
                        mentionObject = []
                    mention_id+=1    
                    rank+=1
            m.objects.bulk_create(mentionObject) # to save the last list of leftover objects
            #print("mention successfully uploaded")    
            idForBlobTable+=1   
        
    except Exception as e:
        print(e)

"""
#This portion of code schedule getSaveBlobData for a particular date
#the start time should be adjusted according to need. 

from apscheduler.schedulers.background import BackgroundScheduler
start_time = datetime.datetime.now() + datetime.timedelta(minutes=100)

scheduler = BackgroundScheduler()
    
scheduler.add_job(getSaveBlobData, 'date',run_date=start_time,replace_existing=True)
    
    
#scheduler.start()
""" 