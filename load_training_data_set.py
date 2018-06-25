# from readData import Report
from constants import *
import json
from rest_api import make_req
from rest_api import ResultsPageInfo
from load_protein_info import read_proteins

TAXONOMY_REQ_BASE="https://www.ebi.ac.uk/proteins/api/taxonomy/path/nodes?direction=BOTTOM&pageSize=3" # &id=33090&pageNumber=1&depth=1&"

# taxonymy_url_cur =TAXONOMY_REQ_BASE + "&id={}&pageNumber={}".format(VIRIDIPLANTAE_ID, 1)

tax_processed = set([])


def traverse_tax_tree():
    # process_tax_tree_level(VIRIDIPLANTAE_ID)
    process_tax_tree_level(3701)

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
            read_proteins(tax_id)
            pass
    pass


traverse_tax_tree()
print("processed {} tax IDs in total".format(len(tax_processed)))
exit(0)
