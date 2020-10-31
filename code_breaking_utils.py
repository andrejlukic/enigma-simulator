import random
import time
import itertools
from enigma import *

#
#   all_possible_settings(config_string)
#       return a list of enigma configurations for a partially known
#       input Enigma settings. Read comments in the method for more details
#
#   check_enigma_config(enigma_config_list, crib, encrypted_text, sample = None)
#       Given an input of a list of Enigma settings and a crib, try out every
#       setting to see if it correctly encrypts the crib. Return a list of
#       such successfull Enigma settings
#
#
#


def check_enigma_config(enigma_config_list, crib, encrypted_text, sample = None):
    '''Find Enigma settings that correctly encrpyt the crib

    Given an input of a list of Enigma settings and a crib, try out every
    setting to see if it correctly encrypts the crib. Return a list of
    such successfull Enigma settings

    :param enigma_config_list: list of 2 or 3 element tuples
                                (Enigma settings, crib position
                                [, reflector scrambled])
    :param crib:                known crib to try to decrypt
    :param encrypted_text:
    :param sample:              if sample of size X is given, than time will be
                                returned requried to check the number of Enigma
                                settings given by the sample
    :return:
    '''

    # in order to predict time required to finish the time required for the
    # first "sample" settings will be measures. Various Enigma settings need
    # different times to process (e.g. if crib position is not at the beginning)
    # so here the list is randomized
    random.shuffle(enigma_config_list)
    # turn off time estimates for tiny searches
    if len(enigma_config_list) < 10000:
        sample = None

    count_tested = 0
    time_start = time.time()
    potential_configs = []
    for enigma_config in enigma_config_list:
        # Prepare Enigma settings:
        cnf = enigma_config[0]
        pos = enigma_config[1]
        reflector_hack = None
        if len(enigma_config) == 3:
            reflector_hack = enigma_config[2]

        # Init Enigma and rotate it to correct position:
        enigma_instance = Enigma(cnf)
        if reflector_hack:
            # if reflector hack is available override wiring:
            enigma_instance.rotors[-1].left_pins = reflector_hack
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
            # potential match: all characters of the crib were encoded correctly
            e = Enigma(cnf)
            # include reflector wiring in result:
            if reflector_hack:
                e.rotors[-1].left_pins = reflector_hack
            result = (str(cnf), e.encode_string(encrypted_text))
            if reflector_hack:
                result += (reflector_hack,)
            potential_configs.append(result)
        count_tested += 1

        if sample and count_tested == sample:
            # return time it took to check a given number of Enigma settings
            # this is used only by the single process implementation
            sample_time = time.time() - time_start
            time_pred = ((len(enigma_config_list) / sample)*sample_time) - sample_time
            # error is expected to be within +- 3%
            print("Estimated {0:.2f} and {1:.2f} seconds left. {2} remaining."
                  .format(time_pred-0.05*time_pred,time_pred+0.05*time_pred, len(enigma_config_list)-count_tested))

    return potential_configs

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

def print_results(results):
    # ('B V-II-IV 6-18-7 A-J-L UG-IE-PO-NX-WT', 'YOUCANFOLLOWMYDOGONINSTAGRAMATTALESOFHOFFMANN')
    # or
    # ('B V-II-IV 6-18-7 A-J-L UG-IE-PO-NX-WT', 'YOUCANFOLLOWMYDOGONINSTAGRAMATTALESOFHOFFMANN', 'PQUHRSLDYXNGOKMABEFZCWVJIT')
    try:
        for solution in results:
            print("\n{0}".format(solution[1]))
            print("{0}".format(solution[0]))
            if(len(solution) > 2):
                print("{0}".format(solution[2]))
    except:
        print(results)


# ------------------------------------------------------------------------
#           Scrambled Reflector Case
#
# All methods below this line are for breaking a specific case
# which is imaginary, where an Enigma reflector had it's
# connections scrambled. So a reflector has been meddled with
# by swapping two wires (4 pairs changed)
# ------------------------------------------------------------------------



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
