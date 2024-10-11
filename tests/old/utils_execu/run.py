# import os
# import sys
# import pprint
# import sgio
import sgio.utils.execu as sue
# from sgio import SwiftCompIOError
import logging

logging.basicConfig(level=logging.DEBUG)

# fn = sys.argv[1]
# file_format = sys.argv[2]
# smdim = int(sys.argv[3])

logger = logging.getLogger(__name__)

# code = 'vabs'
code = 'swiftcomp'
fn_sg = 'sg12_line5_sc2.1.sg'
# fn_sg = 'sg12_line5_sc2.2.sg'
# fn_sg = 'sg21_tri3_vabs.sg'
# fn_sg = 'sg21_tri3_vabs_error_more_nodes_than_nnode.sg'

# cmd = [code, fn_sg]
cmd = [code, fn_sg, '2D', 'H']

timeout = 600

# try:
sue.run(cmd, timeout)
# except SwiftCompIOError as e:
#     print()
