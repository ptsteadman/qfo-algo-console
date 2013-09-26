class Short(object):
    """ Short benchmark strategy.

    To instantiate a short:

    >>> short = Short()
    """
    def __call__(self,tick):
        if tick.index == 0:
            return 'sell'