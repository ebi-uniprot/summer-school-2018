import json
from rest_api import make_req
from constants import IPR_OF_INTEREST_LIST


PROTEIN_REQ_BASE = "https://www.ebi.ac.uk/proteins/api/proteins?offset=0&size=-1&reviewed=true"  # &taxid=3702"


class UniProtProtein:
    def __init__(self, accession):
        self.accession = accession
        self.ipr_groups = set([])
        self.ec_numbers = set([])
        # self.ec_numbers = []

    def add_interpro_xref(self, ipr_grp):
        self.ipr_groups.add(ipr_grp)

    def add_ec_number(self, ec_number):
        # self.ec_numbers.append(ec_number)
        self.ec_numbers.add(ec_number)

    def __str__(self):
        ip_groups = 'InterPro groups: {}'.format(self.ipr_groups)
        ec_nums = 'EC Numbers: {}'.format(self.ec_numbers)
        return '{}. {} {}'.format(
            self.accession, ec_nums, ip_groups)

    def __repr__(self):
        return self.__str__()


def read_protein(accession):
    PROTEIN_URL_BASE = 'https://www.ebi.ac.uk/proteins/api/proteins/'
    protein_url = PROTEIN_URL_BASE + accession
    js_obj = make_req(protein_url)
    return parse_protein_json(js_obj)


def read_proteins(tax_id):
    proteins = []
#    if 3702 == tax_id:
#        print("skipping proteins of tax id: {}".format(tax_id))
#        return proteins

    protein_url = PROTEIN_REQ_BASE + "&taxid={}".format(tax_id)

    js_obj = make_req(protein_url)

    for protein_data in js_obj:
        cur_protein = parse_protein_json(protein_data)
        # print(protein_data)
        proteins.append(cur_protein)

    return proteins


def parse_protein_json(protein_data):
    # print(protein_data)
    cur_protein = UniProtProtein(protein_data['accession'])
    db_ref_node = 'dbReferences'
    if db_ref_node in protein_data:
        for db_ref in protein_data[db_ref_node]:
            if 'InterPro' == db_ref['type']:
                cur_protein.add_interpro_xref(db_ref['id'])

    ec_numbers = extract_protein_ecs_2(protein_data)

    for ec_number in ec_numbers:
        cur_protein.add_ec_number(ec_number)

    return cur_protein

def extract_protein_ecs_2(protein_data):
    ec_numbers = []
    PROT_NODE_NAME = 'protein'
    if PROT_NODE_NAME in protein_data:
        prot_node = protein_data[PROT_NODE_NAME]
        ectract_rec_alt_name_ecs(ec_numbers, prot_node)

        extract_deblock_ecs('domain', ec_numbers, prot_node)
        extract_deblock_ecs('component', ec_numbers, prot_node)
    return ec_numbers


def extract_deblock_ecs(de_block_name, ec_numbers, prot_node):
    if de_block_name in prot_node:
        for deblock_subnode in prot_node[de_block_name]:
            ectract_rec_alt_name_ecs(ec_numbers, deblock_subnode)


def ectract_rec_alt_name_ecs(ec_numbers, prot_subnode):
    REC_NODE_NAME='recommendedName'
    ALT_NODE_NAME='alternativeName'
    if REC_NODE_NAME in prot_subnode:
        add_ecs_from_ecnum_node(ec_numbers, prot_subnode[REC_NODE_NAME])
    if ALT_NODE_NAME in prot_subnode:
        for alt_subnode in prot_subnode[ALT_NODE_NAME]:
            add_ecs_from_ecnum_node(ec_numbers, alt_subnode)


def add_ecs_from_ecnum_node(ec_numbers, ec_node):
    EC_NUM_NODE_NAME = 'ecNumber'
    if EC_NUM_NODE_NAME in ec_node:
        for ec_val in ec_node[EC_NUM_NODE_NAME]:
            ec_numbers.append(ec_val['value'])
    return ec_numbers



def extract_protein_ecs_old(protein_data):
    ec_numbers = []

    add_ecs_from_ecnum_node(ec_numbers, select_node(protein_data, ['protein', 'recommendedName']))

    add_ecs_from_ecnum_node_iter(ec_numbers, select_node(protein_data, ['protein', 'alternativeName']))

    extract_ec_from_multinode(ec_numbers, protein_data, 'domain')
    #
    # extract_ec_from_multinode(ec_numbers, protein_data, 'component')

    return ec_numbers

def extract_ec_from_multinode(ec_numbers, protein_data, name_node_prefix, name_node_name):
    name_nodes = ['protein']
    if name_node_prefix is not None:
        name_nodes.append(name_node_prefix)
        node1 = select_node(protein_data, name_nodes)
        for sub_node in node1:
            ec_numbers.extend(extract_ecs_from_node(sub_node))




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
    if name_block_name in seq_item:
        tbn = type(seq_item[name_block_name])
        is_seq = is_sequence(seq_item[name_block_name])
        # print("blk name: {}, type: {}, is_seq", name_block_name, type(seq_item[name_block_name]), is_sequence(seq_item[name_block_name]))
        if name_block_name in seq_item and 'ecNumber' in seq_item[name_block_name]:
            ec_num_block = seq_item[name_block_name]['ecNumber']
            ec_numbers.extend(extract_ecs_from_node(ec_num_block))
    else:
        print("no block name: {}".format(name_block_name))
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

def add_ecs_from_ecnum_node_iter(ec_numbers, ecnum_nodes):
    for ecnum_node in ecnum_nodes:
        ec_numbers.extend(add_ecs_from_ecnum_node(ecnum_node))




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


def print_accession_interpro_groups_csv(protein):
    ipr_codes = map(lambda cur_ipr: "1" if cur_ipr in protein.ipr_groups else "0", IPR_OF_INTEREST_LIST)
    ipr_codes_joined = ",".join(ipr_codes)
    protein_ac_iprs = '{},{}'.format(protein.accession, ipr_codes_joined)
    return protein_ac_iprs
