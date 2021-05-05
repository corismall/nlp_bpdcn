import spacy
from spacy import displacy
from spacy.matcher import Matcher

# Load the large English NLP model
nlp = spacy.load('en_core_web_lg')
matcher = Matcher(nlp.vocab)

# The text we want to examine

def get_text(file):
    '''opens text file and returns text'''
    
    with open(file, 'r') as f:
        text = f.read().replace('\n', '')
        return text

# Add match ID "cd marker negative" with no callback and one pattern
pos_exp = ['+']
neg_exp = ['-']

pos_pattern = [{"IS_PUNCT": True}, {"TEXT": '+'}, {"IS_PUNCT": True}]
neg_pattern = [{"IS_PUNCT": True}, {"TEXT": '-'}, {"IS_PUNCT": True}]

matcher.add('cd positive', [pos_pattern])
matcher.add('cd negative', [neg_pattern])


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

#spacy tokenize

doc = nlp(clean_text)

matches = matcher(doc)
for match_id, start, end in matches:
    string_id = doc.vocab.strings[match_id]  # look up string id
    span = doc[start:end]
    print(string_id, span.text)

#for num,sentence in enumerate(doc.sents):
 #   print(f'{num}:{sentence}')

#for token in doc:
 #   print(token.text, token.is_punct)

#sentence_spans = list(doc_spacy.sents)
#displacy.serve(sentence_spans, style="dep")

# 'doc' now contains a parsed version of text. We can use it to do anything we want!

# Analyze syntax
#print("Noun phrases:", [chunk.text for chunk in doc.noun_chunks])
#print("Verbs:", [token.lemma_ for token in doc if token.pos_ == "VERB"])


# For example, this will print out all the named entities that were detected:
#for entity in doc.ents:
#    print(f"{entity.text} ({entity.label_})")