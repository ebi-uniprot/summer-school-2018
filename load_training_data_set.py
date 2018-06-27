# from readData import Report
from constants import *
from rest_api import make_req
from rest_api import ResultsPageInfo
from load_protein_info import read_proteins
import datetime

TAXONOMY_REQ_BASE="https://www.ebi.ac.uk/proteins/api/taxonomy/path/nodes?direction=BOTTOM&pageSize=200" # &id=33090&pageNumber=1&depth=1&"

# taxonymy_url_cur =TAXONOMY_REQ_BASE + "&id={}&pageNumber={}".format(VIRIDIPLANTAE_ID, 1)

tax_processed = set([])

global proteins_printed

proteins_printed = 0


def print_proteins_table_headers():
    print('pline:ACCESSION,{},EC_present:{}'.format(
        ",".join(IPR_OF_INTEREST_LIST),EC_NUM_OF_INTEREST))
    return


def traverse_tax_tree():
    print_proteins_table_headers()
    process_tax_tree_level(VIRIDIPLANTAE_ID)
    # process_tax_tree_level(3701)
    pass


def process_tax_tree_level(parent_id):
    page_num = 1
    has_more_pages = True # initially set to true to issue the 1st request
    while has_more_pages:
        taxonymy_url_cur = TAXONOMY_REQ_BASE + "&id={}&pageNumber={}".format(parent_id, page_num)

        js_obj = make_req(taxonymy_url_cur)
        rpi = ResultsPageInfo(js_obj)
        has_more_pages = rpi.has_more_pages()
        page_num = page_num + 1
        # print("has more pages: {}".format(rpi.has_more_pages()))
        taxonomies_list = js_obj['taxonomies']
        process_tax_tree_page(taxonomies_list)


def process_tax_tree_page(taxonomies_list):
    for tax_idx, tax_node in enumerate(taxonomies_list):
        tax_id = int(tax_node['taxonomyId'])

        if tax_id not in tax_processed:
            # we need to process cur tax_id
            print("processing a new tax_id: {}".format(tax_id))
            tax_processed.add(tax_id)
            proteins = read_proteins(tax_id)

            global proteins_printed
            print("{} tax: {} has {} protein(s), {} proteins processed so far".format(
                len(tax_processed), tax_id, len(proteins), proteins_printed))
            # if len(proteins) > 0:
            #     print(proteins)
            print_proteins_table(proteins)


def print_proteins_table(proteins):
    for protein in proteins:
        ipr_codes = map(lambda cur_ipr: "1" if cur_ipr in protein.ipr_groups else "0", IPR_OF_INTEREST_LIST)
        ipr_codes_joined = ",".join(ipr_codes)

        ec_presence = '1' if EC_NUM_OF_INTEREST in protein.ec_numbers else '0'
        print_table_line = 'pline:{},{},{}'.format(
            protein.accession, ipr_codes_joined, ec_presence)
        print(print_table_line)
        global proteins_printed
        proteins_printed = proteins_printed + 1


print('beginning at: '+str(datetime.datetime.now()))
traverse_tax_tree()
print("processed {} tax IDs, {} protein(s) in total".format(len(tax_processed), proteins_printed))
print('finishing at: '+str(datetime.datetime.now()))
exit(0)
