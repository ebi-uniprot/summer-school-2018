import json
from rest_api import make_req


PROTEIN_REQ_BASE = "https://www.ebi.ac.uk/proteins/api/proteins?offset=0&size=-1&reviewed=true"  # &taxid=3702"


class UniProtProtein:
    def __init__(self, accession):
        self.accession = accession
        self.ipr_groups = set([])
        # self.ec_numbers = set([])
        self.ec_numbers = []

    def add_interpro_xref(self, ipr_grp):
        self.ipr_groups.add(ipr_grp)

    def add_ec_number(self, ec_number):
        self.ec_numbers.append(ec_number)

    def __str__(self):
        return '{}. InterPro groups: {} EC Numbers: {}'.format(
            self.accession, self.ipr_groups, self.ec_numbers)

    def __repr__(self):
        return self.__str__()


def read_protein(accession):
    PROTEIN_URL_BASE = 'https://www.ebi.ac.uk/proteins/api/proteins/'
    protein_url = PROTEIN_URL_BASE + accession
    js_obj = make_req(protein_url)
    return parse_protein_json(js_obj)


def read_proteins(tax_id):
    if 3702 == tax_id:
        print("skipping proteins of tax id: {}".format(tax_id))
        return

    protein_url = PROTEIN_REQ_BASE + "&taxid={}".format(tax_id)

    js_obj = make_req(protein_url)

    proteins = []

    if 63677 == tax_id:
        for protein_data in js_obj:
            cur_protein = parse_protein_json(protein_data)
            # print(protein_data)
            proteins.append(cur_protein)
            pass

    # protein_data

    print("tax: {} has {} protein(s)".format(tax_id, len(proteins)))
    if len(proteins) > 0:
        print(proteins)
    return proteins


def parse_protein_json(protein_data):
    print(protein_data)
    cur_protein = UniProtProtein(protein_data['accession'])
    for db_ref in protein_data['dbReferences']:
        if 'InterPro' == db_ref['type']:
            cur_protein.add_interpro_xref(db_ref['id'])

    ec_numbers = extract_protein_ecs(protein_data)

    for ec_number in ec_numbers:
        cur_protein.add_ec_number(ec_number)

    return cur_protein


def extract_protein_ecs(protein_data):
    ec_numbers = []

    ec_numbers.extend(extract_ecs_from_node(select_node(protein_data, ['protein', 'recommendedName', 'ecNumber'])))

    ec_numbers.extend(extract_ecs_from_node(select_node(protein_data, ['protein', 'alternativeName', 'ecNumber'])))

    extract_ec_from_multinode(ec_numbers, protein_data, 'domain')

    extract_ec_from_multinode(ec_numbers, protein_data, 'component')

    return ec_numbers


def extract_ec_from_multinode(ec_numbers, protein_data, multi_node_name):
    protein_domain_node = select_node(protein_data, ['protein', multi_node_name])
    if is_sequence(protein_domain_node):
        for seq_item in protein_domain_node:
            ec_numbers.extend(ec_from_name_blocks(seq_item))


def ec_from_name_blocks(seq_item):
    ec_numbers = []
    ec_numbers.extend(ec_from_name_block('recommendedName', seq_item))
    ec_numbers.extend(ec_from_name_block('alternativeName', seq_item))
    return ec_numbers


def ec_from_name_block(name_block_name, seq_item):
    ec_numbers = []
    print("blk name: {}, type: {}, is_seq", name_block_name, type(seq_item[name_block_name]), is_sequence(seq_item[name_block_name]))
    if name_block_name in seq_item and 'ecNumber' in seq_item[name_block_name]:
        ec_num_block = seq_item[name_block_name]['ecNumber']
        ec_numbers.extend(extract_ecs_from_node(ec_num_block))
    return ec_numbers



def select_node(root_node, node_subnames):
    cur_node = root_node
    for subname in node_subnames:
        if subname in cur_node:
            cur_node = cur_node[subname]
        else:
            return None
    return cur_node


def extract_ecs_from_node(ec_node):
    ec_numbers = []
    if ec_node:
        for ec_val in ec_node:
            ec_numbers.append(ec_val['value'])
    return ec_numbers


def is_sequence(arg):
    if arg is None:
        return False

    if isinstance(arg, str):
        return False

    return (hasattr(arg, "__getitem__") or
            hasattr(arg, "__iter__"))


def walk(node):
    if hasattr(node, "items"):
        for key, item in node.items():
            if is_sequence(item):
                walk(item)
            else:
                pass
