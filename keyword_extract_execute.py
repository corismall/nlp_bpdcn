#Pdf Keyword Extraction
#Corinn Small corinn.small@ucsf.edu


import pdfToolkit


#convert pdfs to xml, need to connect to grobid api to use convert_text() (only need to run once)
path = '/Users/corinnsmall/Documents/BPDCN/bpdcn_papers/'
outpath = path + 'xml_output/'
convert_text(path,outpath)


################################
## Select files and keywords

cases = 'summary'
path = '/Users/corinnsmall/Documents/BPDCN/bpdcn_papers/' + cases +'_case_papers/'
key = 'wgs'
output = 'output_' + cases + '_cases_' + key

associated_diseases_keywords = ['acute myeloid leukemia', 'AML', 'acute lymphoblastic leukemia', 'ALL', 'leukemia', 'non-hodgkin lymphoma', 'Hodgkin lymphoma',
                                'lymphoma','myelogenous leukemia', 'multiple myeloma', 'myeloma', 'chronic myelogenous leukemia', 'CML', 'chronic lymphocytic leukemia', 
                                'CLL', 'carcinoma','Pleuropulmonary blastoma', 'blastoma', 'neuroblastoma', 'melanoma', 'sarcoma', 'skin cancer', 'hairy cell leukemia',
                                'ependymoma', 'chordoma','bone cancer', 'bladder', 'AIDS-related lymphoma', 'thyroid cancer', 'colon cancer', 'rectal cancer',
                                'prostate cancer', 'chronic myeloid leukemia', 'myeloproliferative', 'myelodysplastic', 'mast cell', 'mastocytosis', 'lymphoblastic', 
                                'follicular lymphoma', 'marginal zone lymphoma', 'langerhan', 'polycythemia vera', 'essential thrombocythemia', 'myelofibrosis', 
                                'mycosis fungoides', 'sezary', 'burkitt', 'cmml', 'chronic myelomonocytic leukemia']

morphology_keywords = ['Vacuoles','Vacuolated','Microvacuoles','Lymphoid','Eccentrically','Eccentric','Prominent nucleoli', 'Small nucleoli','Large nucleoli',
                       'Medium nucleoli','azurophilic','Blast','Blastoid','Agranular','Basophilic','Eosinophilic','Perivascular','Periadnexal','Pseudopodia','Hairy','Rosary beads',
                       'Large nucleolus','Monoblastic','Monocytic','Histiocytic','Histiocytoid','Small granules','Large granules','Granulated','Granular','Condensed chromatin',
                       'Dispersed chromatin','Fine chromatin','Pale cytoplasm','Poorly differentiated', 'Large sized','Medium sized','Small sized','Plasmablast', 
                       'Plasmacytoid','plasmacytic','Immature','lymphoblast']

nuclei_keywords = ['convoluted nuclei','convoluted','convolutions','nuclear folds','folds','membrane irregularities','slightly irregular','round nuclei','oval nuclei','vesicular chromatin','cleaved nuclei']

gene_keywords = ['ABL1','AKT1','ALK','APC','ARF','ARID1A','ASH1L','ASXL1','ASXL3','ATM','ATR','AXIN2','BRAF','BCORL1','CAL-1','CCND3','CEBPA','CHD8','CHP2','CDH1','CDKN2A',
                 'CDKN1B','CDKN2B','CIC','CREBBP','CSF1R','CTNNB1','CPS1','CROCC','CXCR4','DAXX','DIP2A','DNMT3A','EGFR','EGR1','EP300','ERBB2','ERBB4','ERCC4','ETV6','EYA2',
                 'EZH2','FBXW7','FGFR1','FGFR2','FGFR3','FLT3','FLT3-ITD','FLT3-other','GNA11','GNAS','GNAQ','GPR160','HES6','HNF1A','HOXB9','HRAS','IDH1','IDH2','IKZF1',
                 'IKZF2','IKZF3','IVL','JAK2','JAK3','KDM40','KDR','KIT','cKIT','KRAS','MAD1L1','MAPK1','MCL1','MET','MLH1','MLL','MLL2','MLL3','MPL','MSH6','MYB','MYBL1',
                 'MYC','MYST3','MYST4','NF1','NOTCH1','NPM1','NR3C1','NRAS','PALB2','PARK2','PBRM1','PDGFRA','PHF2','PHF6','PIK3CA','PMDC05','PLCXD3','PLP1','PTEN','PTPN11',
                 'PTPN23','PVT1','RAD52','RANBP2','RAS','RB1','RET','RFPL1','RHOA','RUNX1','RUNX2','SARDH','SIGLEC6','SLC25A10','SMAD4','SMARCB1','SMARCD1','SMO','SRC','SRCAP',
                 'SRSF2','STK3','STK11','SUPT3H','SUZ12','TCF3','TCL1A','TEL','TET2','TRMT61B','TP53','U2AF1','UBE2G2','VHL','WNT3','WNT7B','WNT10A','WT1','ZEB2','ZRSR2']

wgs_keywords = ['whole exome sequencing', 'whole genome sequencing', 'wes', 'wgs', 'sequencing', 'exome', 'whole genome', 'whole-genome', 'whole-exome', 'genome-wide']

keylist = [i.lower() for i in wgs_keywords]   #make all keywords lower case


##############################################################################
## get xml files from path and write data to file_list for dataframe


files = glob.glob(path + 'xml_output/' + '*.xml')
files_list = []

for file in files:   #store xml info in TEIFILE object
    file_list = []
    f = TEIFile(file)
    name = f.filename.split('/')[-1].split('.')[0]
    f.text
    print('-----------------------------------------------------------\n')
    f.keytext(keylist)
    
    for k,v in f._keytext.items():   #write data to file_list for dataframe
        for d in v:
            #print('subsection dict: ', d)
            for i,j in d.items():
                #print(i, '\n', j)
                
                if len(j) == 0 and f._check == None:
                    file_list = [name, f.filename, f.doi, 'NA', k, i, 'NA']

                elif f._check == None:
                    file_list = [name, f.filename, f.doi, 'NA', k, i, j]   

                else:
                    file_list = [name, f.filename, f.doi, f._check, k, i, j]

                files_list.append(file_list)


df = pd.DataFrame(files_list, columns = ['pdf_name','pdf_location','doi', 'check_paper_content','keywords', 'section', 'text'])



#############################################################################
## write dataframe to excel spreadsheet

try:
    with open(path + output + '.xlsx', 'wb') as out:
        df.to_excel(out)
        
    if out.closed:
        print('Data Ahoy!')

except IOError:
        print('I/O error')