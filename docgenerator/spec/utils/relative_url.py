def get_relative_url(from_path, to_path):
    """
    >>> get_relative_url('/', '/mnx/')
    'mnx/'
    >>> get_relative_url('/elements/', '/elements/mnx/')
    'mnx/'
    >>> get_relative_url('/elements/mnx/', '/elements/')
    '../'
    >>> get_relative_url('/elements/', '/')
    '../'
    >>> get_relative_url('/elements/', '/concepts/')
    '../concepts/'
    >>> get_relative_url('/elements/', '/concepts/2/')
    '../concepts/2/'
    >>> get_relative_url('/elements/mnx/', '/elements/sequence/')
    '../sequence/'
    >>> get_relative_url('/elements/', '/static/styles.css')
    '../static/styles.css'
    >>> get_relative_url('/', '/')
    './'
    >>> get_relative_url('/elements/', '/elements/')
    './'
    """
    # For simplicity, this code assumes both from_path
    # and to_path start with a slash (which is always
    # the case in this project).
    if from_path == to_path:
        return './'
    from_bits = from_path.split('/')[1:-1] # Assumed to end with slash.
    to_bits = to_path.split('/')[1:]
    if to_bits[-1] == '':
        ends_in_slash = True
        to_bits.pop()
    else:
        ends_in_slash = False

    common = 0
    for from_bit, to_bit in zip(from_bits, to_bits):
        if from_bit == to_bit:
            common += 1
        else:
            break

    result = '/'.join(
        ['..' for x in from_bits[common:]] +
        to_bits[common:]
    )
    if ends_in_slash:
        result += '/'
    return result

if __name__ == "__main__":
    import doctest
    doctest.testmod()
