import sys
#==================================================================================================================
class Printer():
    """Print things to stdout on one line dynamically"""
    def __init__(self,data):
        #print(data, end='\r')
        sys.__stdout__.write("\r"+data.__str__())
        sys.__stdout__.flush()

