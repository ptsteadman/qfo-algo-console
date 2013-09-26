class Buy(object):
    """ Buy and hold benchmark strategy.

    To instantiate a 30 tick monkey:

    >>> buy = Buy()
    """
    def __call__(self,tick):
            return 'buy'