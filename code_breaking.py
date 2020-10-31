from code_breaking_utils import *
from enigma import *

#   This is the basic Enigma brute force code breaking that runs in a single process
#
#   Use the CLI to try the code breaking:
#       python3 enigma-cli.py --module interactive
#   Select 2 for code breaking, then 1 for predefined demo job,
#   then 1 for the single process code breaker
#
#   Function decrypt_cipher finds Enigma configuration based on encrypted
#   text, crib and a partially known configuration:
#
#       decrypt_cipher(encrypted_text, crib, config_string, sample_size = 500)
#
#
#   Function decrypt_cipher_reflector_scrambled (special case related to my uni project
#   finds Enigma configuration based on encrypted text, crib and a partially
#   known configuration and knowing that two wires of the Reflector had been swapped.
#
#       decrypt_cipher_reflector_scrambled(encrypted_text, crib, enigma_config)
#

def decrypt_cipher(encrypted_text, crib, config_string, sample_size = 500):
    """Attempt to break Enigma cypher with a known crib and partially known config

    Example input:
       encrypted_text:
       ABSKJAKKMRITTNYURBJFWQGRSGNNYJSDRYLAPQWIAGKJYEPCTAGDCTHLCDRZRFZHKNRSDLNPFPEBVESHPY
       cribs: THOUSANDS
       enigma_config
       C III-?-["II","I"]-V [4,5,6]-24-?-7 ABGZ-?-Q-F AQ-?S-ED-["ZU","ZF","ZK"]

    To understand how to specify the partially known or unknown Enigma config
    read the description of the all_enigma_settings_candidates() function.

    After all possible Enigma settings are constructed each setting is tried on a crib
    until such Enigma setting is found that the complete crib matches the encoded text.
    Such Enigma setting is put on a list of possible candidates along with the decrypted
    text. A human must then go through this list to decide if any of the potential settings
    are correct.

    :param encrypted_text:
    :param crib:
    :param config_string:
    :param sample_size: size of the sample to predict remaining time from
    :return:
    """
    time_start = time.time()

    if encrypted_text is None or len(encrypted_text) < len(crib):
        raise ValueError('Expected some code to break.')
    if not crib:
        raise ValueError('Expected a crib.')

    # Construct all possible Enigma settings based on unknown / partially known
    # Enigma configuration provided:
    enigma_configs = all_possible_settings(config_string)
    # Slide the crib under the encrypted text and determine all positions in
    # which the letter of the crib does not match the encrypted text
    # (Enigma can never encode a letter into itself)
    crib_positions = possible_crib_positions(encrypted_text, crib)

    print("\nRunning a single process to find solutions.")
    print("{0} settings to search".format(len(enigma_configs)*len(crib_positions)))

    # Loop through all potential Enigma settings and try to decrypt the crib:
    configs_to_check = []
    for pos in crib_positions:
        for cnf in enigma_configs:
            configs_to_check.append((cnf,pos))

    result = check_enigma_config(configs_to_check,
                                 crib,
                                 encrypted_text,
                                 sample_size)

    return result, time.time() - time_start


# ------------------------------------------------------------------------
#           Scrambled Reflector Case
#
# All methods below this line are for breaking a specific case
# which is imaginary, where an Enigma reflector had it's
# connections scrambled. So a reflector has been meddled with
# by swapping two wires (4 pairs changed)
# ------------------------------------------------------------------------


def decrypt_cipher_reflector_scrambled(encrypted_text, crib, enigma_config):
    """Attempt to break Enigma cypher with a known crib and a reflector that
    had been hacked (2 wires in the reflector were swapped)

    Example input:
       encrypted_text:
       HWREISXLGTTBYVXRCWWJAKZDTVZWKBDJPVQYNEQIOTIFX
       cribs: INSTAGRAM
       enigma_config
       "? V-II-IV 6-18-7 A-J-L UG-IE-PO-NX-WT"

    To understand how to specify the partially known or unknown Enigma config
    read the description of the all_enigma_settings_candidates() function.

    After all possible Enigma settings are constructed additionally all possible
    permutations of every possible reflector is added. Every reflector has been
    meddled with by swapping two wires (4 pairs changed). Details on how these
    permutations were constructed in docstring here:
        permutate_reflector_by_wire_swap()

    Every Enigma setting with every possible reflector permutation will be tried
    until the encoded crib matches the encoded text. Such Enigma setting is put
    on a list of possible candidates along with the decrypted text. A human must
    then go through this list to decide if any of the potential settings are
    correct.

    :param encrypted_text:
    :param crib:
    :param config_string:
    :return:
    """
    time_start = time.time()

    crib_positions = possible_crib_positions(encrypted_text, crib)
    enigma_configs = all_possible_settings(enigma_config)

    print("\nRunning a single process to find solutions")
    print("\nReflector has two wires swapped.")
    print("{0} settings (4290 reflector wirings) to search".format(len(enigma_configs) * 4290 * len(crib_positions)))

    potential_configs = []
    for cnf in enigma_configs:
        enigma_instance = Enigma(cnf)
        l = permutate_reflector_by_wire_swap("".join(enigma_instance.rotors[-1].left_pins), 2)
        #print("Checking enigma config={0} with {1} reflector wirings".format(enigma_instance.print_state(), len(l)))
        for pos in crib_positions:
            for reflector_option in l:
                enigma_instance = Enigma(cnf)
                # Replace standard reflector with a hacked one:
                enigma_instance.rotors[-1].left_pins = reflector_option
                enigma_instance.rotate_n_steps(pos)
                potential_config = True
                for inx in range(len(crib)):
                    if enigma_instance.encode_character(crib[inx]) != encrypted_text[pos + inx]:
                        potential_config = False
                        break
                if potential_config:
                    e = Enigma(cnf)
                    e.rotors[-1].left_pins = reflector_option
                    potential_configs.append((str(cnf), e.encode_string(encrypted_text), reflector_option))
    return potential_configs, time.time() - time_start