__author__ = 'Dr Giusy Mariano'
__email__ = 'giusy.mariano@ncl.ac.uk'
__license__ = "GPL"
#!/usr/bin/env python
# coding: utf-8
import sys
import csv
from http.client import IncompleteRead
import pandas as pd
from Bio import Entrez
Entrez.email = sys.argv[1]

    

# get from WPs accession, corresponding assembly, NC IDs, strains names. Write a csv table with all these as final data tablee,
#+ a table with WPs and Assembly IDs for inputting in FLAG

list_of_accession = []
with open (sys.argv[2], 'r', encoding='utf-8-sig') as csvfile:
    efetchin=csv.reader(csvfile, delimiter = ',')
    for row in efetchin:
        list_of_accession.append(str(row[0]))
        
with open('efetch_output.txt', mode = 'w') as efetch_output:
    efetch_output = csv.writer(efetch_output, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    efetch_output.writerow(['ID','Source', 'Nucleotide Accession', 'Start', 'Stop', 'Strand', 'Protein', 'Protein Name', 'Organism', ' Strain', 'Assembly'])

input_handle = Entrez.efetch(db="protein", id= list_of_accession, rettype="ipg", retmode="tsv")
for line in input_handle:
    print(line, file=open('efetch_output.txt','a'))
input_handle.close()
#process file in pandas
file_name = "efetch_output.txt"
file_name_output = "final_output.tsv"
df = pd.read_csv(file_name, sep="\t", low_memory=False)
# Get names of indexes for which rows have to be dropped
indexNames = df[ df['Source'] == 'INSDC'].index
# Delete these row indexes from dataFrame
df.drop(indexNames , inplace=True)
# Get names of indexes for which rows have to be dropped
indexNames2 = df[ df['Source'] == 'PAT'].index
# Delete these row indexes from dataFrame
df.drop(indexNames2 , inplace=True)
#rearrange table columns
df = df[['ID', 'Source', 'Nucleotide Accession', 'Protein', 'Protein Name', 'Start', 'Stop', 'Strand', 'Organism',' Strain', 'Assembly']]
#Sort table on Assembly number ignoring GCF_
df['sort'] = df['Assembly'].str.extract('(\d+)', expand=False).astype(float)
df.sort_values('sort',inplace=True, ascending=True)
df = df.drop('sort', axis=1)
#drop all duplicates that're similar in indicated subset fields
df3=df.drop_duplicates(subset=['Start', 'Stop', 'Strand', 'Organism',' Strain', 'Assembly'],keep='first')
dff3= df3.drop_duplicates(subset=['Start', 'Stop', 'Organism',],keep='first')

#sorts dataframe alphabetically by Organism

dff4 = dff3.sort_values(by = "Organism", axis=0, ascending=True, inplace=False)
#parse again to make sure all the replicates are gone
df4 = dff4.sort_values(by = [" Strain",'Start'], axis=0, ascending=True, inplace=False).drop_duplicates(subset=[' Strain'],keep='last')
#Write in a csv file
df5 = df4.sort_values(by = ["Organism", " Strain"], axis=0, ascending=True, inplace=False).to_csv("final_parsed_output.tsv", "\t", index=False)

#get WP_X and GFC_X IDs in a tsv for further analysis
new_dataframe1 = df3[['Assembly', 'Protein']]
new_dataframe2 = df3[['Organism',' Strain', 'Assembly', 'Protein']]
new_dataframe1.sort_values(by = "Protein", axis=0, ascending=True, inplace=False).to_csv('neigh_analysis_input.tsv', '\t', header=False, columns = ['Assembly', 'Protein'])
new_dataframe2.sort_values(by = "Organism", axis=0, ascending=True, inplace=False).to_csv('neigh_analysis_input_wstrains.tsv', '\t', header=False, columns = ['Organism',' Strain', 'Assembly', 'Protein'])

print ('program finished')
