import boto3
import json
import sys
import time

message = 'make sure your aws role has the correct permissions to run textract, see https://docs.aws.amazon.com/textract/latest/dg/api-async-roles.html to configure' 
print(message)

class ProcessType:
    DETECTION = 1
    ANALYSIS = 2    

class DocumentProcessor:
    jobId = ''
    textract = boto3.client('textract')
    sqs = boto3.client('sqs')
    sns = boto3.client('sns')
    roleArn = ''
    bucket = ''
    document = ''
    sqsQueueUrl = ''
    snsTopicArn = ''
    processType = ''


    def __init__(self, role, bucket, document):

        '''
        Initiate 'DocumentProcessor' object with TextractRole, bucket, document in bucket, and nlp_topic
        
        '''

        self.roleArn = role  #refers to roleARN, ours = 'arn:aws:iam::760515291717:role/TextractRole'
        self.bucket = bucket
        self.document = document  #refers to name of document being held in bucket


    def ProcessDocument(self,type):  #refers back to ProcessType class ^^

        '''
        Choose processing type: 1 = detection, 2 = analysis
        Returns response of chosen process
        
        '''

        jobFound = False
        self.processType=type
        validType=False
        
        #Determine which type of processing to perform
        if self.processType==ProcessType.DETECTION:
            response = self.textract.start_document_text_detection(DocumentLocation={'S3Object': {'Bucket': self.bucket, 'Name': self.document}},
                NotificationChannel={'RoleArn': self.roleArn, 'SNSTopicArn': self.snsTopicArn})

            print('Processing type: Detection')
            validType=True

        if self.processType==ProcessType.ANALYSIS:
            response = self.textract.start_document_analysis(DocumentLocation={'S3Object': {'Bucket': self.bucket, 'Name': self.document}},
                FeatureTypes=["TABLES"],
                NotificationChannel={'RoleArn': self.roleArn, 'SNSTopicArn':self.snsTopicArn})
            
            print('Processing type: Analysis')
            validType=True
        
        if validType==False:
            print("Invalid processing type. Choose Detection or Analysis.")
            return

        print('Start Job Id: ' + response['JobId'])
        dotLine=0
        
        while jobFound == False:
            sqsResponse = self.sqs.receive_message(QueueUrl=self.sqsQueueUrl, MessageAttributeNames=['ALL'], MaxNumberOfMessages=10)

            if sqsResponse:
                if 'Messages' not in sqsResponse:
                    if dotLine<40:
                        print('.', end='')
                        dotLine=dotLine+1
                    else:
                        print()
                        dotLine=0
                    sys.stdout.flush()
                    time.sleep(5)
                    continue

                for message in sqsResponse['Messages']: 
                    notification = json.loads(message['Body'])
                    textMessage = json.loads(notification['Message'])
                    print(textMessage['JobId'])
                    print(textMessage['Status'])

                    if str(textMessage['JobId']) == response['JobId']:
                        print('Matching Job Found:' + textMessage['JobId'])
                        jobFound = True
                        self.GetResults(textMessage['JobId'])
                        self.sqs.delete_message(QueueUrl=self.sqsQueueUrl, ReceiptHandle=message['ReceiptHandle'])
                    else:
                        print("Job didn't match:" + str(textMessage['JobId']) + ' : ' + str(response['JobId']))

                    # delete the unknown message. consider sending to dead letter queue
                    self.sqs.delete_message(QueueUrl=self.sqsQueueUrl, ReceiptHandle=message['ReceiptHandle'])

        print('Done!')


    def CreateTopicandQueue(self):
        millis = str(int(round(time.time() * 1000)))
        
        #Create SNS topic
        snsTopicName="AmazonTextractTopic" + millis
        topicResponse=self.sns.create_topic(Name=snsTopicName)
        self.snsTopicArn = topicResponse['TopicArn']
        
        #create SQS queue
        sqsQueueName="AmazonTextractQueue" + millis
        self.sqs.create_queue(QueueName=sqsQueueName)
        self.sqsQueueUrl = self.sqs.get_queue_url(QueueName=sqsQueueName)['QueueUrl']
        attribs = self.sqs.get_queue_attributes(QueueUrl=self.sqsQueueUrl, AttributeNames=['QueueArn'])['Attributes']
        sqsQueueArn = attribs['QueueArn']
        
        # Subscribe SQS queue to SNS topic
        self.sns.subscribe(
            TopicArn=self.snsTopicArn,
            Protocol='sqs',
            Endpoint=sqsQueueArn)

        #Authorize SNS to write SQS queue
        policy = """{{"Version":"2012-10-17", "Statement":[{{
            "Sid":"MyPolicy",
            "Effect":"Allow",
            "Principal" : {{"AWS" : "*"}},
            "Action":"SQS:SendMessage",
            "Resource": "{}",
            "Condition":{{"ArnEquals":{{"aws:SourceArn": "{}"}}
            }} }}]}}""".format(sqsQueueArn, self.snsTopicArn)
        
        response = self.sqs.set_queue_attributes(
            QueueUrl = self.sqsQueueUrl,
            Attributes = {
                'Policy' : policy
            })


    def DeleteTopicandQueue(self):
        self.sqs.delete_queue(QueueUrl=self.sqsQueueUrl)
        self.sns.delete_topic(TopicArn=self.snsTopicArn)



    def DisplayBlockInfo(self,block):

        '''
        Display information about a block
        '''

        print ("Block Id: " + block['Id'])
        print ("Type: " + block['BlockType'])
        
        if 'EntityTypes' in block:
            print('EntityTypes: {}'.format(block['EntityTypes']))
        
        if 'Text' in block:
            print("Text: " + block['Text'])
        
        if block['BlockType'] != 'PAGE':
            print("Confidence: " + "{:.2f}".format(block['Confidence']) + "%")
        
        print('Page: {}'.format(block['Page']))
        
        if block['BlockType'] == 'CELL':
            print('Cell Information')
            print('\tColumn: {} '.format(block['ColumnIndex']))
            print('\tRow: {}'.format(block['RowIndex']))
            print('\tColumn span: {} '.format(block['ColumnSpan']))
            print('\tRow span: {}'.format(block['RowSpan']))
            if 'Relationships' in block:
                print('\tRelationships: {}'.format(block['Relationships']))
        print('Geometry')
        print('\tBounding Box: {}'.format(block['Geometry']['BoundingBox']))
        print('\tPolygon: {}'.format(block['Geometry']['Polygon']))
        
        if block['BlockType'] == 'SELECTION_ELEMENT':
            print('    Selection element detected: ', end='')
            if block['SelectionStatus'] =='SELECTED':
                print('Selected')
            else:
                print('Not selected')

    def GetResults(self, jobId):
       maxResults = 1000
       paginationToken = None
       finished = False
       
       while finished == False:
           response=None
           if self.processType==ProcessType.ANALYSIS:
               if paginationToken==None:
                   response = self.textract.get_document_analysis(JobId=jobId,
                       MaxResults=maxResults)
               else:
                   response = self.textract.get_document_analysis(JobId=jobId,
                       MaxResults=maxResults,
                       NextToken=paginationToken)
           
           if self.processType==ProcessType.DETECTION:
               if paginationToken==None:
                   response = self.textract.get_document_text_detection(JobId=jobId, MaxResults=maxResults)
               else:
                   response = self.textract.get_document_text_detection(JobId=jobId, MaxResults=maxResults, NextToken=paginationToken)
           
           blocks=response['Blocks']
           print ('Detected Document Text')
           print ('Pages: {}'.format(response['DocumentMetadata']['Pages']))
           
           # Display block information
           for block in blocks:
                   self.DisplayBlockInfo(block)
                   print()
                   print()
           if 'NextToken' in response:
               paginationToken = response['NextToken']
           else:
               finished = True

    def GetResultsDocumentAnalysis(self, jobId):
       maxResults = 1000
       paginationToken = None
       finished = False
       while finished == False:
           response=None
           if paginationToken==None:
               response = self.textract.get_document_analysis(JobId=jobId,
                                           MaxResults=maxResults)
           else:
               response = self.textract.get_document_analysis(JobId=jobId,
                                           MaxResults=maxResults,
                                           NextToken=paginationToken)
           #Get the text blocks
           blocks=response['Blocks']
           print ('Analyzed Document Text')
           print ('Pages: {}'.format(response['DocumentMetadata']['Pages']))
           
           # Display block information
           for block in blocks:
               self.DisplayBlockInfo(block)
               print()
               print()
               
               if 'NextToken' in response:
                   paginationToken = response['NextToken']
               else:
                   finished = True

def main():
    roleArn = ''
    bucket = ''
    document = ''

    analyzer=DocumentProcessor(roleArn, bucket, document)
    analyzer.CreateTopicandQueue()
    analyzer.ProcessDocument(ProcessType.DETECTION)
    analyzer.DeleteTopicandQueue()

if __name__ == "__main__":
    main()