from os import sep
import spacy
from spacy import displacy
from spacy.matcher import Matcher
from spacy.tokens import Doc, Token, Span
import glob, pdfToolkit
from spellchecker import SpellChecker


# Load the large English NLP model
nlp = spacy.load('en_core_web_lg')
matcher = Matcher(nlp.vocab)

# Add match ID "cd marker negative" with no callback and one pattern
pos_exp = ['+']
neg_exp = ['-']

pos_pattern = [[{"IS_PUNCT": True}, {"TEXT": '+'}, {"IS_PUNCT": True}], [{"IS_PUNCT": True}, {"TEXT": 'bright'}, {"IS_PUNCT": True}],[{'TEXT': '+'}]]
neg_pattern = [{"IS_PUNCT": True}, {"TEXT": '-'}, {"IS_PUNCT": True}] 

matcher.add('cd_positive', pos_pattern)
matcher.add('cd_negative', [neg_pattern])


def add_training_data(sentence_list):
    TRAINING_DATA = []

    for doc in nlp.pipe(sentence_list):    
        #Match on the doc and create a list of matched spans
        #print(doc)
        matches = matcher(doc)
        spans = []
        entities = []
        for match_id, start, end in matches:
            span = doc[start:end]
            string_id = nlp.vocab.strings[match_id]
            spans.append((span,string_id))
        
        for span, string_id in spans:
            #print(span, string_id)
            entities.append((span.start, span.end, string_id))
        
        # Format the matches as a (doc.text, entities) tuple
        if doc.text:
            training_example = (doc.text, {'entities': entities})
            TRAINING_DATA.append(training_example)
        else:
            pass
    
    return TRAINING_DATA





spell = SpellChecker()
files = glob.glob('/Users/corinnsmall/Documents/BPDCN/bpdcn_papers/single_case_papers/xml_output/berger_2004.tei.xml')

for file in files:   #store xml info in TEIFILE object
    f = pdfToolkit.TEIFile(file)
    name = f.filename.split('/')[-1].split('.')[0]
    print(name)
    f.text

    #clean TEIFile object text
    for k,v in f.text.items():
        #by section k
        print(k)
        v_strip = []
        for s in v:
            t = s.strip()
            v_strip.append(t)
        full_text = " ".join(v_strip)
        print('full_text ',full_text)
        print('')
        clean_text = " ".join(full_text.split())
        print('clean_text ',clean_text)
        print('')
    

        #split text into sentences
        text_sentences = clean_text.lower().split('.')
        # or later sentence_spans = list(doc.sents)
        
        misspelled = spell.unknown(text_sentences)
        for word in misspelled:
            print(word, )
            # Get the one `most likely` answer
            #print(spell.correction(word))
 
            # Get a list of `likely` options
            #print(spell.candidates(word))

        #create training data
        #t_data = add_training_data(text_sentences)
        #print(*t_data, sep="\n")



# Analyze syntax
#print("Noun phrases:", [chunk.text for chunk in doc.noun_chunks])
#print("Verbs:", [token.lemma_ for token in doc if token.pos_ == "VERB"])

#for num,sentence in enumerate(doc.sents):
  #   print(f'{num}:{sentence}')

 #for token in doc:
  #   print(token.text, token.is_punct)

 #sentence_spans = list(doc.sents)
 #displacy.serve(sentence_spans, style="dep")

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
        nlp.update(texts, annotations)'''

#save the model
#nlp.to_disk(path_to_model)


#updating model

#start with blank english model
#nlp = spacy.blank("en")
#create blank entity recognizer and add it to the pipeline
#ner = nlp.create_pipe('ner')
#nlp.add_pipe(ner)
#add a new label
#ner.add_label(LABEL)

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

























