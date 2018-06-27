import datetime

from load_protein_info import *

print('beginning at: '+str(datetime.datetime.now()))

print(read_protein('P0CK01'))
print(read_protein('Q9FBI2'))
print(read_protein('P46854'))
print(read_protein('P36843'))
print(read_protein('P19560'))

print('finishing at: '+str(datetime.datetime.now()))
