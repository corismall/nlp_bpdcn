import boto3

# make sure your aws role has the correct permissions to run textract, see https://docs.aws.amazon.com/textract/latest/dg/api-async-roles.html 
# to configue 
    
client = boto3.client('textract')
for m in dir(client): print(m)  # what are the function attached to the client object?... _ = 'private' function meaning dont call it

#have to set up a aws account s3 bucket... (cloud object storage)
#for s3object, you need to specify bucket, name and version:
s3_obj =  {"Bucket": bpdcnpdfbucket, "Name": 'agapidou_2014.pdf'}  #creating dictionary obj

response = client.start_document_text_detection(
    DocumentLocation={'S3Object': s3_obj},
    ClientRequestToken = '',
    JobTag = '', 
    NotificationChannel={
        'SNSTopicArn': 'string',
        'RoleArn': 'string'
    },
    OutputConfig={
        'S3Bucket': 'string',
        'S3Prefix': 'string'
    },
    KMSKeyId='string')  #for detecting and analyzing text in multipage docs (asynchronous op), I would try both syncrhonous and asynchronous, maybe the synchronous works for pdfs with just a couple of pages?



#response = client.GetDocumentTextDetection(Document = {'S3Object': s3_obj})  #nesting dictionary s3_obj inside document dictionary and giving that to the client function 
#get results returned, we want an s3object dictionary to be returned 

#response is a dictionary type: you can look at the document page that specifies the basic the s3 object metadata to get fields that you can query from the dict

#detect = response.copy()  #save output as detection (of the pdf output)

#now to analyze all the gibberish (output = list of block objects) this is the synchronous version:
#response2 = client.analyze_document(Document = {'S3Object': s3_obj}, FeatureTypes = ['TABLES'])
#document = s3object
#observation: of required syntax: the layout is confusing to you, the request syntax that the boto3 doc specifies is telling you what type of ojbect to pass the client.function and the naming convention of the returned object! thats it! dont worry, just keep in mind the indendation and parentheses
#featuretypes is required
#response2['Blocks'][0].keys()  # print name of each block

#for b in response2['Blocks']:
    #if b['BlockType'] == 'LINE':
        #print("{}\t{}".format(b['Text'], b['Confidence']))  # for everytime line is found, what is that word and the confidence at which its identified, it's important/critical to check the confidence scores!