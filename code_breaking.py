import itertools
import time # for measuring time to break the code
import multiprocessing as mp
from enigma import *

def all_enigma_settings_candidates(config_string):
    """Return all possible settings for un- or partially known Enigma configuration

     Description:
       An Enigma config string can contain a valid configuration or a question mark
       character where the setting is unknown. For the unknown setting all (supported)
       settings combinations will be listed. Instead of a question mark a list of
       possible values can also be listed, then the settings will be limited only to
       values in that list.

     Example input:
       'C III-?-["II","I"]-V [4,5,6]-24-?-7 ABGZ-?-Q-F AQ-?S-ED-["ZU","ZF","ZK"]'
     Interpreted as:
       - Reflector is C.
       - Rotors:
            - 1 is V
            - rotor 2 is either I or II
            - rotor 3 is unknown and can be any supported rotor
            - rotor 4 is III
       - Ring settings:
            - first rotor = 7
            - second rotor unknown (all 26 possible)
            - third rotor = 24
            - fourth rotor is on of [4, 5 or 6]
       - Rotor positions:
            - first rotor = F
            - second rotor = Q
            - third is unknown and can be any position
            - fourth rotor position is one of [A, B, G or Z]
       - Plugs:
            - AQ
            - ED
            - ?S one lead connects to S, but the other end is not known
            - ["ZU","ZF","ZK"] last lead is one of [ZU,ZF or ZK]

    :param config_string: An Enigma config string with marked unknown settings
    :return: A dictionary of all possible Enigma settings
    """

    # Determine known / unknown reflector settings:
    config_options = {}
    config_parts = config_string.split()
    config_reflector = config_parts[0]
    if config_reflector == "?":
        #config_options["reflectors"] = ["A", "B", "C", "B_thin", "C_thin"]
        config_options["reflectors"] = ["A", "B", "C"]
    elif "[" in config_reflector:
        config_options["reflectors"] = eval(config_reflector)
    else:
        config_options["reflectors"] = [config_reflector]

    # Determine known / unknown rotor settings:
    config_options["rotors"] = []
    for rotor_label in config_parts[1].split('-')[::-1]:
        if rotor_label == "?": # all supported rotors will be tried
            config_options["rotors"] .append(["I","II","III","IV","V","Beta","Gamma"])
        elif "[" in rotor_label: # given a list of rotors to try
            config_options["rotors"] .append(eval(rotor_label))
        else:
            config_options["rotors"] .append([rotor_label])

    # Determine known / unknown rotor position settings:
    config_options["rotor_positions"]  = []
    for rotor_position in config_parts[3].split('-')[::-1]:
        if rotor_position == "?":
            config_options["rotor_positions"].append("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        else:
            config_options["rotor_positions"].append(rotor_position)

    # Determine known / unknown rotor ring settings:
    config_options["ring_settings"] = []
    for ring_setting in config_parts[2].split('-')[::-1]:
        if ring_setting == "?": # try all ring settings for this rotor
            config_options["ring_settings"].append(list(range(1,27,1)))
        elif "[" in ring_setting: # list of ring settings to try for this rotor
            config_options["ring_settings"].append(eval(ring_setting))
        else: # exact ring setting known for this rotor
            config_options["ring_settings"].append([int(ring_setting)])

    # Determine known / unknown plugboard settings:
    # TODO: could be improved based on crib loops
    config_options["plugboard"] = []
    if len(config_parts) > 4:
        for bind in config_parts[4].replace('-', ' ').split():
            if "?" in bind: # one end of the lead unknown
                options_list = []
                known_plug = bind.replace('?','')
                for letter in list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
                    if letter != known_plug:
                        options_list.append(letter+known_plug)
                config_options["plugboard"].append(options_list)
            elif "[" in bind: # list of connections to try
                config_options["plugboard"].append(eval(bind))
            else: # exact swap known
                config_options["plugboard"].append([bind])
    return config_options

def all_possible_settings(config_string):
    """Construct a list of all possible settings for un- or partially known Enigma

         Description:
           An Enigma config string can contain a valid configuration or a question mark
           character where the setting is unknown. For the unknown setting all (supported)
           settings combinations will be listed. Instead of a question mark a list of
           possible values can also be listed, then the settings will be limited only to
           values in that list.

         Example input:
           'C III-?-["II","I"]-V [4,5,6]-24-?-7 ABGZ-?-Q-F AQ-?S-ED-["ZU","ZF","ZK"]'
         Interpreted as:
           - Reflector is C.
           - Rotors:
                - 1 is V
                - rotor 2 is either I or II
                - rotor 3 is unknown and can be any supported rotor
                - rotor 4 is III
           - Ring settings:
                - first rotor = 7
                - second rotor unknown (all 26 possible)
                - third rotor = 24
                - fourth rotor is on of [4, 5 or 6]
           - Rotor positions:
                - first rotor = F
                - second rotor = Q
                - third is unknown and can be any position
                - fourth rotor position is one of [A, B, G or Z]
           - Plugs:
                - AQ
                - ED
                - ?S one lead connects to S, but the other end is not known
                - ["ZU","ZF","ZK"] last lead is one of [ZU,ZF or ZK]

        :param config_string: An Enigma config string with marked unknown settings
        :return: A dictionary of all possible Enigma settings
        """

    # first replace unknown Enigma settings with all possible
    # Enigma settings values that could occur:
    enigma_config_options = all_enigma_settings_candidates(config_string)
    # Construct all possible rotor setting permutations for all 3+1 or 4+1 rotors:
    # (Uniqueness is enforced)
    rotor_perms = [list(c) for c in itertools.product(*enigma_config_options["rotors"]) if len(set(c))==len(c)]
    # Construct all possible rotor positions setting permutations:
    rotor_position_perms = [list(c) for c in itertools.product(*enigma_config_options["rotor_positions"])]
    # Construct all possible rotor ring settings permutations:
    rotor_ring_setting_perms = [list(c) for c in itertools.product(*enigma_config_options["ring_settings"])]
    # Construct all possible plugboard setting permutations:
    # (Uniqueness is enforced)
    plugboard_perms = [list(c) for c in itertools.product(*enigma_config_options["plugboard"])  if len(set(c))==len(c)]

    # Construct all possible Enigma settings:
    enigma_configurations = set()
    enigma_config_options = all_enigma_settings_candidates(config_string)
    for reflector_setting in enigma_config_options["reflectors"]:
        for rotor_settings in rotor_perms:
            for rotors_position_settings in rotor_position_perms:
                for rings_settings in rotor_ring_setting_perms:
                    for plugboard_settings in plugboard_perms:
                        cnf = EnigmaConfig(reflector_setting, rotor_settings, rotors_position_settings, rings_settings, plugboard_settings)
                        if cnf.is_valid_configuration():
                            enigma_configurations.add(cnf)

    return enigma_configurations


def decrypt_cipher(encrypted_text, crib, config_string):
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
    :return:
    """

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

    # Loop through all potential Enigma settings and try to decrypt the crib:
    potential_configs = []
    for pos in crib_positions:
        for cnf in enigma_configs:
            enigma_instance = Enigma(cnf)
            # in case the crib is not at the beginning of the text rotate Enigma
            # forward to find the correct rotor positions
            enigma_instance.rotate_n_steps(pos)
            potential_config = True
            for inx in range(len(crib)):
                if enigma_instance.encode_character(crib[inx]) != encrypted_text[pos + inx]:
                    # if any character does not match this Enigma setting can be discarded
                    # and further decryption can be stopped
                    potential_config = False
                    break
            if potential_config:
                # all characters of the crib could be encoded correctly
                potential_configs.append((str(cnf), Enigma(cnf).encode_string(encrypted_text)))
    return potential_configs

def possible_crib_positions(encrypted_text, crib):
    """Exclude impossible crib positions.

    Enigma can never encode a character into itself. Therefore it
    is possible to exclude certain positions of the crib. For example:
    For an encrypted string: DMEXBMKYCVPNQBEDHXVPZGKMTFFBJRPJTLHLCHOTKOYXGGHZ
    and a crib: SECRETS we know that the word secrets cannot be at position 01:
        DMEXBMKYCVPNQBEDHXVPZGKMTFFBJRPJTLHLCHOTKOYXGGHZ
        -SECRETS
    because in this position E would be encoded as E which is impossible. This
    function will only return possible positions.

    :param encrypted_text:
    :param crib: A crib to slide under the encrypted text
    :return:
    """

    if not encrypted_text or not crib or len(encrypted_text) < len(crib):
        return []

    positions = []
    for pos in range(len(encrypted_text)+1-len(crib)):
        potential_position = True
        for plaintext_char, encrypted_char in zip(list(crib),
                                                  list(encrypted_text[pos:pos+len(crib)])):
            if plaintext_char == encrypted_char:
                potential_position = False
                break
        if potential_position:
            positions.append(pos)
    return positions

def swap_tuples(t1, t2):
    """Two pairs can be swapped in 3 ways (two new ways).

    e.g. (A,C), (B,E) (existing way)
        - (A,B), (C,E)
        - (A,E), (C,B)
    and only the new ways will be returned, e.g. [(A,B),(C,E)] and [(A,E),(C,B)]

    :param t1: pair1
    :param t2: pair2
    :return: 2 new possible swaps
    """

    result = []
    result.append([(t1[0],t2[0]), (t1[1],t2[1])])
    result.append([(t1[0],t2[1]), (t1[1],t2[0])])
    return result


def convert_reflector_to_pairs_notation(reflector_wiring):
    """Convert the string notation to a set of pairs, e.g. BADC => (A,B), (C,D)"""

    # this alphabet slicing is here for unit testing with shorter reflector definitions:
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:len(reflector_wiring)]
    unique_pairs = set()
    # reflector has only 13 pairs, so if A maps to E,
    # then E to A mapping can be assumed so it is excluded:
    exclude = set()
    for c in reflector_wiring:
        if not reflector_wiring.index(c) in exclude:
            unique_pairs.add((c, alphabet[reflector_wiring.index(c)]))
            exclude.add(alphabet.index(c))
    return unique_pairs

def convert_reflector_to_string_notation(reflector_pairs):
    """Convert the pairs notation to the string notation, e.g. (A,B), (C,D) => BADC"""

    # this alphabet slicing is here for unit testing with shorter reflector definitions:
    abc = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:len(reflector_pairs)*2])
    for t in reflector_pairs:
        i1 = abc.index(t[0])
        i2 = abc.index(t[1])
        abc[i1], abc[i2] = abc[i2], abc[i1]
    return ''.join(abc)

def permutate_reflector_by_wire_swap(reflector_wiring, num_swaps):
    """Returns permutations of reflector wirings.

    This will only work with reflector type of rotor, that has 13 pairs instead
    of the regular rotor with 26 pairs. Unlike a regular rotor a reflector has
    only 13 pairs (so if A is mapped to E, then E is also mapped to A). A swap
    means swapping of the wire. Each swap affects two pairs, e.g. (A,D), (B,C),
    so if A is swapped with B then (A,B), (C,D). A single wire can only be swapped
    once in case multple swaps are required. Two swaps e.g. means swapping 2 wires,
    which affects 4 pairs, since a single swap of each wire affects two pairs.
    Two swaps produce !13/4!(13-4)! = 715 combinations of picking up 4 pairs out
    of all the pairs. Out of the four possible combinations, 3 are new.
    e.g.: (A,C), (B,E), (D,F), (G,H):
        - (A,C), (B,E) and (D,F), (G,H)
        - (A,C), (D,F) and (B,E), (G,H)
        - (A,C), (G,H) and (B,E), (D,F)

    Each of these combinations of four pairs, gives 3 ways to swap the wires
    between them, (two new ways).
    e.g. (A,C), (B,E) (existing way)
        - (A,B), (C,E)
        - (A,E), (C,B)
    and only the new ways will be returned, e.g. [(A,B),(C,E)] and [(A,E),(C,B)]

    So in turn each combination of four pairs will give:
        - 3 ways to pick a couple of pairs out of four pairs
        - 2 ways to swap wires between a couple of pairs * 2 pairs
    gives 12 permutations for every combination of four pairs.
    In total for 2 swaps this should produce 4290 (!13/4!(13-4)! * 3 * 4)
    different reflector wirings


    :param reflector_wiring: original wiring of reflector as EJMZALYXVBWFCRQUONTSPIKHGD
    :param num_swaps: how many times to swap a wire between two pairs.
    :return:
    """

    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:len(reflector_wiring)]
    # Convert the string notation to pairs notation, e.g. BADC => (A,B), (C,D)
    unique_pairs = convert_reflector_to_pairs_notation(reflector_wiring)
    # For each swap pick two pairs out of a bag of all pairs (e.g. for 2 swaps
    # pick 4 pairs). This should produce n!/r!(n-r)! combinations where n is the
    # total number of pairs and r = 2 * num_swaps, e.g. for 2 swaps = 715
    combinations = list(itertools.combinations(unique_pairs, num_swaps*2))
    # Iterate over every combination of pairs and swap the wires in
    # every possible ways:
    result = []
    for c in combinations:
        #print("Combination ", list(c))
        # All possible ways to pick 2 pairs out of a combination of 4 pairs.
        # There are 6 ways to do this but only 3 unique since in 4 pairs like:
        # (A,C), (B,E), (D,F), (G,H)
        # (A,C), (D,F) leaves (B, E), (G,H)
        # and
        # (B,E), (G,H) then also leaves (A,C), (D,F) and these two are the same:
        swap_combo = list(itertools.combinations(c, 2))
        for s in swap_combo[:int(len(swap_combo)/2)]:
            # s are the two pairs selected from the combination of 4 and
            # r are the remaining two other pairs, e.g. if
            # (A,C), (B,E), (D,F), (G,H) and s = {(A,C), (D,F)} then
            # r = {(B, E), (G,H)}
            r = list(set(c) - set(s))
            # swap two pairs in two ways (skip the old way):
            all_swaps_s = swap_tuples(s[0], s[1])
            # swap two pairs in two ways (skip the old way):
            all_swaps_r = swap_tuples(r[0], r[1])
            # yes, I know what this looks like .... :
            result.append(list(itertools.chain(all_swaps_s[0] + all_swaps_r[0], (unique_pairs - set(c)))))
            result.append(list(itertools.chain(all_swaps_s[0] + all_swaps_r[1], (unique_pairs - set(c)))))
            result.append(list(itertools.chain(all_swaps_s[1] + all_swaps_r[0], (unique_pairs - set(c)))))
            result.append(list(itertools.chain(all_swaps_s[1] + all_swaps_r[1], (unique_pairs - set(c)))))

    wirings = [convert_reflector_to_string_notation(pair_combo) for pair_combo in result]
    return list(set(wirings))

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

    crib_positions = possible_crib_positions(encrypted_text, crib)
    enigma_configs = all_possible_settings(enigma_config)
    print("Found {0} possible positions of the crib and {1} possible Enigma configurations".format(len(crib_positions), len(enigma_configs)))

    potential_configs = []
    for cnf in enigma_configs:
        enigma_instance = Enigma(cnf)
        l = permutate_reflector_by_wire_swap("".join(enigma_instance.rotors[-1].left_pins), 2)
        print("Checking enigma config={0} with {1} reflector wirings".format(enigma_instance.print_state(), len(l)))
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
                    potential_configs.append((str(cnf), reflector_option, e.encode_string(encrypted_text)))
    return potential_configs

#
#
#   ------ Multiprocessing Implementation - using all CPU cores
#
#

def check_enigma_config(enigma_config_list, crib, encrypted_text):
    potential_configs = []
    for enigma_config in enigma_config_list:
        cnf = enigma_config[0]
        pos = enigma_config[1]
        reflector_hack = None
        if len(enigma_config) == 3:
            reflector_hack = enigma_config[2]
        enigma_instance = Enigma(cnf)
        # in case the crib is not at the beginning of the text rotate Enigma
        # forward to find the correct rotor positions
        if reflector_hack:
            enigma_instance.rotors[-1].left_pins = reflector_hack
        enigma_instance.rotate_n_steps(pos)
        potential_config = True
        for inx in range(len(crib)):
            if enigma_instance.encode_character(crib[inx]) != encrypted_text[pos + inx]:
                # if any character does not match this Enigma setting can be discarded
                # and further decryption can be stopped
                potential_config = False
                break
        if potential_config:
            # all characters of the crib could be encoded correctly
            print("Potential config")
            e = Enigma(cnf)
            if reflector_hack:
                e.rotors[-1].left_pins = reflector_hack
                potential_configs.append((str(cnf), reflector_hack, e.encode_string(encrypted_text)))
            else:
                potential_configs.append((str(cnf), e.encode_string(encrypted_text)))
    return potential_configs


def decrypt_cipher_multiproc(encrypted_text, crib, config_string, batch_size):
    """Attempt to break Enigma cypher with a known crib and partially known config
    using multiple processor cores

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
    :return:
    """

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

    # Loop through all potential Enigma settings and try to decrypt the crib:
    potential_configs = []
    pool = mp.Pool(mp.cpu_count())
    batch_count = 0
    batch = []
    batches_count = 0
    results = []
    for pos in crib_positions:
        for cnf in enigma_configs:
            batch.append((cnf,pos))
            batch_count += 1
            if batch_count >= batch_size:
                batches_count += 1
                results.append(pool.apply_async(check_enigma_config, args=(batch, crib, encrypted_text)))
                batch_count = 0
                batch = []
    for r in results:
        potential_configs = list(itertools.chain(potential_configs, r.get()))

    print("Processes: ", pool._processes)
    print("Batch size: ", batch_size)
    print("Batches: ", batches_count)
    pool.close()
    return [cnf for cnf in potential_configs if cnf]

def decrypt_cipher_reflector_scrambled_multiproc(encrypted_text, crib, enigma_config, chunk_size):
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

    crib_positions = possible_crib_positions(encrypted_text, crib)
    enigma_configs = all_possible_settings(enigma_config)
    print("Found {0} possible positions of the crib and {1} possible Enigma configurations".format(len(crib_positions), len(enigma_configs)))

    pool = mp.Pool(mp.cpu_count())
    chunk = []
    chunks_count = 0
    configs_count = 0
    results = []
    potential_configs = []
    for cnf in enigma_configs:
        enigma_instance = Enigma(cnf)
        l = permutate_reflector_by_wire_swap("".join(enigma_instance.rotors[-1].left_pins), 2)
        print("Checking enigma config={0} with {1} reflector wirings".format(enigma_instance.print_state(), len(l)))
        for pos in crib_positions:
            for reflector_option in l:
                chunk.append((cnf, pos, reflector_option))
                configs_count += 1
                if configs_count >= chunk_size:
                    chunks_count += 1
                    results.append(pool.apply_async(check_enigma_config, args=(chunk, crib, encrypted_text)))
                    configs_count = 0
                    chunk = []
    for r in results:
        potential_configs = list(itertools.chain(potential_configs, r.get()))

    print("Processes: ", pool._processes)
    print("Chunk size: ", chunk_size)
    print("Chunks: ", chunks_count)
    pool.close()
    return [cnf for cnf in potential_configs if cnf]

def test_perf_multiproc():
    results = []
    # run in 8 processes and split problem into chunks. Each chunk is
    # a group of Enigma configurations to try out. Several chunk sizes
    # are tested to determine what the ideal size of a chunk is

    for chunk_size in range(1, 101, 50):
        start = time.time()
        print(decrypt_cipher_multiproc("CMFSUPKNCBMUYEQVVDYKLRQZTPUFHSWWAKTUGXMPAMYAFITXIJKMH",
                           "UNIVERSITY",
                           'B Beta-I-III 23-2-10 ?-?-? VH-PT-ZG-BJ-EY-FS', chunk_size))
        end = time.time()
        results.append(end-start)
        print("Time to process with chunk size {0}={1}".format( chunk_size, end - start))

    print(results)

    # Run in a single process:
    start = time.time()
    print(decrypt_cipher("CMFSUPKNCBMUYEQVVDYKLRQZTPUFHSWWAKTUGXMPAMYAFITXIJKMH",
                           "UNIVERSITY",
                           'B Beta-I-III 23-2-10 ?-?-? VH-PT-ZG-BJ-EY-FS'))
    end = time.time()
    print(end - start)

def test_perf_multiproc2():
    results = []
    # run in 8 processes and split problem into chunks. Each chunk is
    # a group of Enigma configurations to try out. Several chunk sizes
    # are tested to determine what the ideal size of a chunk is

    for chunk_size in range(1, 6, 3):
        start = time.time()
        print(decrypt_cipher_multiproc("ABSKJAKKMRITTNYURBJFWQGRSGNNYJSDRYLAPQWIAGKJYEPCTAGDCTHLCDRZRFZHKNRSDLNPFPEBVESHPY",
                                        "THOUSANDS",
                                        '? ["II","IV","Beta","Gamma"]-["II","IV","Beta","Gamma"]-["II","IV","Beta","Gamma"] [2,4,6,8,20,22,24,26]-[2,4,6,8,20,22,24,26]-[2,4,6,8,20,22,24,26] E-M-Y FH-TS-BE-UQ-KD-AL', chunk_size))
        end = time.time()
        results.append(end-start)
        print("Time to process with chunk size {0}={1}".format( chunk_size, end - start))

    print(results)

    # Run in a single process:
    print("Running in a single process:")
    start = time.time()
    print(decrypt_cipher("ABSKJAKKMRITTNYURBJFWQGRSGNNYJSDRYLAPQWIAGKJYEPCTAGDCTHLCDRZRFZHKNRSDLNPFPEBVESHPY",
                                        "THOUSANDS",
                                        '? ["II","IV","Beta","Gamma"]-["II","IV","Beta","Gamma"]-["II","IV","Beta","Gamma"] [2,4,6,8,20,22,24,26]-[2,4,6,8,20,22,24,26]-[2,4,6,8,20,22,24,26] E-M-Y FH-TS-BE-UQ-KD-AL'))
    end = time.time()
    print(end - start)

def test_perf_multiproc5():
    results = []
    # run in 8 processes and split problem into chunks. Each chunk is
    # a group of Enigma configurations to try out. Several chunk sizes
    # are tested to determine what the ideal size of a chunk is
    for chunk_size in range(1, 30, 3):
        #chunk_size = 25
        start = time.time()
        print(decrypt_cipher_reflector_scrambled_multiproc("HWREISXLGTTBYVXRCWWJAKZDTVZWKBDJPVQYNEQIOTIFX",
                                                             "INSTAGRAM",
                                                             "? V-II-IV 6-18-7 A-J-L UG-IE-PO-NX-WT", chunk_size))
        end = time.time()
        results.append(end-start)
        print("Time to process with chunk size {0}={1}".format( chunk_size, end - start))

    print(results)

    # Run in a single process:
    print("Running in a single process:")
    start = time.time()
    print(decrypt_cipher_reflector_scrambled("HWREISXLGTTBYVXRCWWJAKZDTVZWKBDJPVQYNEQIOTIFX",
                                             "INSTAGRAM",
                                             "? V-II-IV 6-18-7 A-J-L UG-IE-PO-NX-WT"))
    end = time.time()
    print(end - start)

#test_perf_multiproc()