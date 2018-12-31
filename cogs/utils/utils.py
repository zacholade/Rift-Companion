async def calc_checksum(s):
    """
    Calculates checksum for sending commands to the ELKM1.
    Sums the ASCII character values mod256 and returns
    the lower byte of the two's complement of that value.
    """
    return '%2X' % (-(sum(ord(c) for c in s) % 256) & 0xFF)