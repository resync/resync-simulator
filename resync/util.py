"""
util.py: A collection of common util functions used in source and/or client.

"""

from logging import Formatter
from datetime import datetime

class UTCFormatter(Formatter):
    # based on http://bit.ly/T2n3Xk
    def formatTime(self, record, datefmt=None):
        timestamp = record.created
        return datetime.utcfromtimestamp(timestamp).isoformat() + 'Z'