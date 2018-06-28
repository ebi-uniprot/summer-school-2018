from load_protein_info import read_protein
from load_protein_info import print_accession_interpro_groups_csv
import argparse
from constants import IPR_OF_INTEREST_LIST
from constants import EC_NUM_OF_INTEREST


def process_proteins(accessions_string):
    accessions = [ac.strip() for ac in accessions_string.split(',')]
    proteins_processed = 0
    for ac in accessions:
        protein_json = read_protein(ac)
        p_line = print_accession_interpro_groups_csv(protein_json)
        print (p_line+',?')
        proteins_processed += 1
    print("*** processed {} protein(s) in total".format(proteins_processed))


def print_target_proteins_table_headers():
    print('ACCESSION,{},EC_present:{}'.format(",".join(IPR_OF_INTEREST_LIST),EC_NUM_OF_INTEREST))
    return


parser = argparse.ArgumentParser(description='load UniProt accessions in Weka format for target data set')
parser.add_argument('accessions', metavar='AC1[,AC2]', type=str,
                    help='comma-separated list of UniProt accessions, e.g.: Q6JKS0,E3P8I9,A0A2H4WRG2,A0A2H4WRJ3')


args = parser.parse_args()
print_target_proteins_table_headers()
process_proteins(args.accessions)
