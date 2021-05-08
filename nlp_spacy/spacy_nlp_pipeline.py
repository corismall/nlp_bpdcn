import spacy
from spacy import displacy
from spacy.matcher import Matcher
from spacy.tokens import Doc, Token, Span

# Load the large English NLP model
nlp = spacy.load('en_core_web_lg')
matcher = Matcher(nlp.vocab)

# The text we want to examine from PDF_PAGE_FILE

#file = PDF_PAGE_FILE

def get_text(file):
    '''opens text file and returns text'''
    
    with open(file, 'r') as f:
        text = f.read().replace('\n', '')
        return text

#def get_doi(FILE_RESPONSE.JSON):
    #doi = something
    #return doi

#def get_page(PDF_PAGE_FILE)
    #page = something
    #return page

#for later:
# Doc.set_extension('id', default=None)
# Doc.set_extension('page_number', default=None)
#
# data = list(get_text(file), {"id": doi, "page_number: page"})

'''for doc, context in nlp.pipe(data, as_tuples=True):
    doc._.id = context["id"]
    doc._.page_number = context["page_number"]'''


# Parse the text with spaCy. This runs the entire pipeline.

#file = '/Users/corinnsmall/Documents/Github/nlp/textractor_outputs/agapidou_2014-pdf-page-1-text-inreadingorder.txt'

text = '''A 78-year-old Caucasian female patient presented
to our department with a cutaneous lesion on her right
shoulder (Figure la). Bone marrow aspiration showed 5% infiltration of
immature blast cells with the following immunophenotype:
CD45 (+), CD123 (+), CD85k (+), CD33 (-), CD14 (-), CD16
(-), CD19 (-), CD5 (-), CD10 (-), CD20 (-), CD56 (+) 20%,
CD4 (+), NG2 (+). No chromosomal alterations were detected
by cytogenetic analysis of the bone marrow (46,XX).'''

clean_text = " ".join(text.split())
#print(text, clean_text)

#create doc

doc = nlp(clean_text)
 

# Use matcher to create training data!
# Add match ID "cd marker negative" with no callback and one pattern
pos_exp = ['+']
neg_exp = ['-']

pos_pattern = [{"IS_PUNCT": True}, {"TEXT": '+'}, {"IS_PUNCT": True}]
neg_pattern = [{"IS_PUNCT": True}, {"TEXT": '-'}, {"IS_PUNCT": True}]

matcher.add('cd positive', [pos_pattern])
matcher.add('cd negative', [neg_pattern])


matches = matcher(doc)
#print(matches)

for match_id, start, end in matches:
    string_id = doc.vocab.strings[match_id]  # look up string hash id
    span = Span(doc, start, end)
    print(span)


print(Doc.doc.ents)


'''print(doc)
print('')
print("Noun phrases:", [chunk.text for chunk in doc.noun_chunks])
print('')
print("Verbs:", [token.lemma_ for token in doc if token.pos_ == "VERB"])'''



#for token in doc:
 #   print(token.text)
  #  if token.text == '(+)' or '(-)':
   #     print('yes')
    #else:
     #   pass    
    #print(token.text, token._.is_expression, token.pos_)

#sentence_spans = list(doc.sents)
#print(sentence_spans)
#displacy.serve(sentence_spans, style="dep")

# 'doc' now contains a parsed version of text. We can use it to do anything we want!

# Analyze syntax
#print("Noun phrases:", [chunk.text for chunk in doc.noun_chunks])
#print("Verbs:", [token.lemma_ for token in doc if token.pos_ == "VERB"])


# For example, this will print out all the named entities that were detected:
#for entity in doc.ents:
#    print(f"{entity.text} ({entity.label_})")





#where I got my infos: https://www.youtube.com/watch?v=THduWAnG97k

#How training works:
#1) initialize the model weights randomly with nlp.begin_training
#2) predict labels (text category, or an entity span and its type) with a few examples with the current weights by calling nlp.update
#3) compare prediction with true labels
#4) Calculate how to change weights to improve predictions
#5) update weights slightly
#6) go back to step 2

'''TRAINING_DATA = [
    ("TEXT", {"entities":[(position, "LABEL")]}),
    (),
    (), etc

]'''









#Steps of a training loop
#1) loop for a number of times
#2) shuffle the training data
#3) divide the data into batches : 'mini-batching'
#4) update the model for each batch
#5) save the updated model

#loop for 10 iterations
'''for i in range(10):
    #shuffle the training data
    random.shuffle(TRAINING_DATA)
    #create batches and iterate over them
    for batch in spacy.util.minibatch(TRAINING_DATA):
        #split the batch in texts and annotations
        texts = [text for text, annotation in batch]
        annotations = [annotation for text, annotation in batch]
        #update the model
        nlp.update(texts, annotations)

#save the model
nlp.to_disk(path_to_model)'''


#updating model

#start with blank english model
nlp = spacy.blank("en")
#create blank entity recognizer and add it to the pipeline
ner = nlp.create_pipe('ner')
nlp.add_pipe(ner)
#add a new label
ner.add_label(LABEL)

#start the training
#nlp.begin_training()
#train for 10 iterations
'''for itn in range(10):
    random.shuffle(examples)
    #divide examples into batches
    for batch in spacy.util.minibatch(examples, size=2):
        texts = [texts for text, annotation in batch]
        annotations = [annotation for text, annotation in batch]
        #update the model
        nlp.update(texts, annotations)'''


###########
#Best practices
#to overcome the 'Catastrophic Forgetting' problem:
#mix in previously correct preditcions, just keep adding entities to your previous training dataset

#models cant learn everything
#spacy models make predictions based on a local context
#decisions are also difficult to make base on context alone
#label scheme needs to be consistent and not too specific
#plan label scheme: pick categories that are reflected in local context, more generic, use rule to go from generic to specific

























