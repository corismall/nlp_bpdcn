import boto3

# make sure your aws role has the correct permissions to run textract, see https://docs.aws.amazon.com/textract/latest/dg/api-async-roles.html 
# to configue 
    
client = boto3.client('textract')
#for m in dir(client): print(m)  # what are the function attached to the client object?... _ = 'private' function meaning dont call it

f_name = 'agapidou_2014'

#have to set up an aws account s3 bucket... (cloud object storage)
#for s3object, you need to specify bucket, name and version:
s3_obj =  {"Bucket": 'bpdcnpdfbucket', "Name": 'agapidou_2014.pdf'}  #creating dictionary obj

detect = client.start_document_text_detection(
    DocumentLocation={'S3Object': s3_obj},
    NotificationChannel={
        'SNSTopicArn': 'arn:aws:sns:us-west-1:760515291717:nlp_topic',
        'RoleArn': 'arn:aws:iam::760515291717:role/TextractRole'
    },
    OutputConfig={
        'S3Bucket': 'bpdcnpdfbucket',
        'S3Prefix': f_name
    })  #for detecting and analyzing text in multipage docs (asynchronous op), I would try both syncrhonous and asynchronous, maybe the synchronous works for pdfs with just a couple of pages?

print('detect: \n', detect['JobId']) 
detect_jobid = detect['JobId']


doc_text = client.get_document_text_detection(
    JobId = detect_jobid)

print(doc_text['JobStatus'])
#,'\n',doc_text['Blocks'].keys())

#response is a dictionary type: you can look at the document page that specifies the basic the s3 object metadata to get fields that you can query from the dict

#doc_text_copy = doc_text.copy()  #save output as detection (of the pdf output)

#now to analyze all the gibberish (output = list of block objects) this is the synchronous version:

#response = client.start_document_analysis(DocumentLocation = {'S3Object': s3_obj})

#print('response: \n',response)

#document = s3object
#observation: of required syntax: the layout is confusing to you, the request syntax that the boto3 doc specifies is telling you what type of ojbect to pass the client.function and the naming convention of the returned object! thats it! dont worry, just keep in mind the indendation and parentheses
#featuretypes is required

#response2 = client.get_document_analysis(JobId='1c2142394bb10a48270d569e74930757b95d33492b2281c6fa6a8705b6aee88f')

#response2['JobStatus']
#response2['Blocks'][0].keys()  # print name of each block

#for b in response2['Blocks']:
    #if b['BlockType'] == 'LINE':
        #print("{}\t{}".format(b['Text'], b['Confidence']))  # for everytime line is found, what is that word and the confidence at which its identified, it's important/critical to check the confidence scores!