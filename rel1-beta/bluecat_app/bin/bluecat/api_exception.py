"""
A class representing API exceptions. Most of these are things returned by the BAM SOAP API but 
other errors (e.g. the failure to ssh to server, non-zero exit from nsupdate etc.) can also
result in exceptions being raised.
"""


class api_exception(BaseException):
    """
    Create a new instance with a message and, optionall, some extra details. The contents of these fields
    are not intended to be interpretted by software rather, the intention is that they're caught somewhere
    near the top of a program and then displayed to a user in some way.

    :param message: Primary string describing why the exception was raised.
    :param details: Details, where available, of the specific exception .

    """

    def __init__(self, message, details=None):
        self._message = message
        self._details = details

    """
    Return a string representation of the exception including the message and details (if any)
    """

    def __str__(self):
        res = "BlueCat API exception:" + self._message
        if self._details is not None:
            res += ":" + self._details
        return res

    """
    Get the exception main message.
    """

    def get_message(self):
        """Get a message describing the exception.
        """
        return self._message

    """
    Get the exception details where available.
    """

    def get_details(self):
        """Get further details about the exception (may be None)
        """
        return self._details
