import json
import boto3
import csv
import os
import logging
import logging.config
import codecs
from io import StringIO

def lambda_handler(event, context):
    
    #print(event['source_bucket'])
    
    read_bucket_name=event['source_bucket']
    write_bucket_name=event['target_bucket']
    #original_key=event['original_key']
    split_size=int(event['split_size'])
    s3 = boto3.client('s3')
    
    # read_bucket_name ='hitratetestdata'
    # write_bucket_name ='hitratetestdata'
    original_key='data.tsv'
    target_key = 'data'
    obj = s3.get_object(Bucket=read_bucket_name, Key=original_key)
    

    lines = []
    lines1= []
    line_count = 0
    file_count = 0
    counter=0
    MAX_LINE_COUNT = split_size

    def create_split_name(file_count):
        return f'{target_key}_{file_count}.tsv'

    def create_body(lines):
        return ''.join(lines)
        
    stream=codecs.getreader('utf-8')(obj['Body'])
    lines = list(csv.DictReader(stream,delimiter="\t"))
    csv_buffer = StringIO()
    out = csv.DictWriter(csv_buffer,delimiter="\t",fieldnames=['hit_time_gmt','date_time','user_agent','ip','event_list','geo_city','geo_region','geo_country','pagename','page_url','product_list','referrer'])
    out.writeheader()
    for row in lines:
        if line_count > MAX_LINE_COUNT:
            key = create_split_name(file_count)
            s3.put_object(
                Bucket=write_bucket_name,
                Key=key,
                Body=csv_buffer.getvalue().encode('utf-8')
            )
        
            lines = []
            line_count = 0
            file_count += 1
        
            
        out.writerow({'hit_time_gmt':row['hit_time_gmt'],'date_time':row['date_time'],'user_agent':row['user_agent'],'ip':row['ip'],'event_list':row['event_list'],'geo_city':row['geo_city'],'geo_region':row['geo_region'],'geo_country':row['geo_country'],'pagename':row['pagename'],'page_url':row['page_url'],'product_list':row['product_list'],'referrer':row['referrer']})
        line_count+=1
            
    
    return {
        'statusCode': 200,
        'body': { 'file_count': file_count }
    }
