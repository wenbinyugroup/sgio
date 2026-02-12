import sys
#==================================================================================================================
class Printer():
    """Print things to stdout on one line dynamically"""
    def __init__(self,data):
        #print(data, end='\r')
        try:
            sys.__stdout__.write("\r"+data.__str__())
            sys.__stdout__.flush()
        except (OSError, AttributeError):
            # Handle cases where stdout is not available or invalid
            # (e.g., during pytest execution on Windows)
            pass

