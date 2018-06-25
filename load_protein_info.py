import json
from rest_api import make_req

PROTEIN_REQ_BASE="https://www.ebi.ac.uk/proteins/api/proteins?offset=0&size=-1&reviewed=true" # &taxid=3702"
IPR_OF_INTEREST_LIST=[   'IPR000070', 'IPR000772','IPR001574','IPR006501',
                    'IPR011050','IPR012334','IPR016138','IPR016139',
                    'IPR016331','IPR017988','IPR017989','IPR018040',
                    'IPR033131','IPR035513','IPR035992','IPR036041' ]

IPR_OF_INTEREST = set(IPR_OF_INTEREST_LIST) # for a faster access


class UniProtProtein:
    def __init__(self, accession):
        self.accession = accession
        self.ipr_groups = set([])

    def add_interpro_xref(self, ipr_grp):
        self.ipr_groups.add(ipr_grp)

    def __str__(self):
        return '{}: [{}]'.format(self.accession, self.ipr_groups)

    def __repr__(self):
        return '{}: [{}]'.format(self.accession, self.ipr_groups)


def read_proteins(tax_id):
    if 3702 == tax_id:
        print("skipping proteins of tax id: {}".format(tax_id))
        return

    protein_url = PROTEIN_REQ_BASE + "&taxid={}".format(tax_id)

    js_obj = make_req(protein_url)

    proteins = []

    if 63677 == tax_id:
        for protein_data in js_obj:
            cur_protein = UniProtProtein(protein_data['accession'])
            for db_ref in protein_data['dbReferences']:
                if 'InterPro' == db_ref['type']:
                    cur_protein.add_interpro_xref(db_ref['id'])
                    pass
                pass

            # print(protein_data)
            proteins.append(cur_protein)
            pass

    # protein_data

    print("tax: {} has {} protein(s)".format(tax_id, len(proteins)))
    if len(proteins) > 0:
        print(proteins)
    return proteins
