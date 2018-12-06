import itertools

def bin_combinations(bin_str_len):
    """ Returns list of strings of all of the possible binary combinations """
    
    # Get all of the binary possibilities of bin_str_len bits
    bin_possibilities = list(itertools.product(["0", "1"], repeat=bin_str_len))
    bin_possibilities = [''.join(i) for i in bin_possibilities]

    return bin_possibilities

def quad_to_bin_str(quad):
    """ Returns binary string representation of a dotted quad string. """

    bin_str_final = ''
    for quad in quad.split('.'):
        bin_str = "{0:b}".format(int(quad))

        # Pad each binary representation to 8 bits
        if len(bin_str) != 8:
            bin_str = "0" * (8 - len(bin_str)) + bin_str

        bin_str_final += bin_str

    return bin_str_final

def bin_to_dotted_quad(bin_in):
    """ Returns the dotted quad representation of a binary string. """

    if len(bin_in) != 32:
        raise Exception("Binary string input to bin_to_dotted_quad must be 32 bits.")

    IP_addr = ""
    # Build dotted quad by partitioning bits into the four quads  
    for i in range(0, 25, 8):
        if i != 24:
            IP_addr += str(int(bin_in[i:i+8], 2)) + "."
        else:
            IP_addr += str(int(bin_in[i:i+8], 2))

    return IP_addr

def logical_AND_dotted_quads(quad1, quad2):
    """ Returns dotted quad of two anded dotted quad addresses """

    quad1_split = [int(i) for i in quad1.split('.')]
    quad2_split = [int(i) for i in quad2.split('.')]

    anded_quads_bin = []
    for a, b in zip(quad1_split, quad2_split):
        anded_quads_bin.append(a & b)

    anded_quads_dotted = ''
    for i in range(len(anded_quads_bin)):
        if i != len(anded_quads_bin) - 1:
            anded_quads_dotted += str(int(anded_quads_bin[i])) + '.'
        else:
            anded_quads_dotted += str(int(anded_quads_bin[i]))

    return anded_quads_dotted

def subnet_size_to_bin(subnet_size):
    one_bits = '1' * subnet_size
    zero_bits = '0' * (32 - subnet_size)
    return one_bits + zero_bits