from code_breaking_utils import *
import time                     # for measuring time required to break the code
import multiprocessing as mp    # code breaking in a pool of processwes
import itertools                # special case: scrambling reflector
#
#
#   This is the improved Enigma brute force code breaking that runs in a
#   pool of processes
#
#   Use the CLI to try the multiprocessing:
#       python3 enigma-cli.py --module interactive
#   Select 2 for code breaking, then 1 for predefined demo job, then 2 for the
#   multprocessing code breaker
#
#   Function decrypt_cipher_multiproc finds Enigma configuration based on encrypted
#   text, crib and a partially known configuration and using all processor cores:
#
#       decrypt_cipher_multiproc(encrypted_text, crib, config_string, chunk_size = 50)
#
#
#   Function decrypt_cipher_reflector_scrambled_multiproc (special case related to my uni
#   project to find Enigma configuration based on encrypted text, crib and a partially
#   known configuration and knowing that two wires of the Reflector had been swapped.
#
#       decrypt_cipher_reflector_scrambled_multiproc(encrypted_text, crib, enigma_config, chunk_size = 50)
#

def decrypt_cipher_multiproc(encrypted_text, crib, config_string, chunk_size = 50):
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

    print("\nDistributed amongst {0} processes to find solutions.".format(mp.cpu_count()))
    print("Searching through {0} Enigma settings split in chunks of {1}".format(len(enigma_configs) * len(crib_positions), chunk_size))

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
            if batch_count >= chunk_size:
                batches_count += 1
                results.append(pool.apply_async(check_enigma_config, args=(batch, crib, encrypted_text)))
                batch_count = 0
                batch = []

    # Wait for all the processes to finish and collect results:
    for r in results:
        result = r.get()
        if(result): # (list of configs, time)
            potential_configs = list(itertools.chain(potential_configs, result))
    pool.close()
    return [cnf for cnf in potential_configs if cnf], time.time() - time_start

def decrypt_cipher_reflector_scrambled_multiproc(encrypted_text, crib, enigma_config, chunk_size = 50):
    """Attempt to break Enigma cypher with a known crib and a reflector that
    had been hacked (2 wires in the reflector were swapped) on multiple CPU cores

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

    print("\nDistributed amongst {0} processes in chunks of {1} to find solutions.".format(mp.cpu_count(), chunk_size))
    print("\nReflector has two wires swapped.")
    print("{0} settings (4290 reflector wirings) to search".format(len(enigma_configs) * 4290 * len(crib_positions)))

    pool = mp.Pool(mp.cpu_count())
    chunk = []
    chunks_count = 0
    configs_count = 0
    results = []
    potential_configs = []
    for cnf in enigma_configs:
        enigma_instance = Enigma(cnf)
        l = permutate_reflector_by_wire_swap("".join(enigma_instance.rotors[-1].left_pins), 2)
        #print("Checking enigma config={0} with {1} reflector wirings".format(enigma_instance.print_state(), len(l)))
        for pos in crib_positions:
            for reflector_option in l:
                chunk.append((cnf, pos, reflector_option))
                configs_count += 1
                if configs_count >= chunk_size:
                    chunks_count += 1
                    results.append(pool.apply_async(check_enigma_config, args=(chunk, crib, encrypted_text)))
                    configs_count = 0
                    chunk = []

    # Wait for all the processes to finish and collect results:
    for r in results:
        result = r.get()
        if (result):  # (list of configs, time)
            potential_configs = list(itertools.chain(potential_configs, result))

    pool.close()
    return [cnf for cnf in potential_configs if cnf], time.time() - time_start

# ---------------------------
# ---------------------------
# --------------------------- END OF CODE BREAKING CODE
# ---------------------------
# ---------------------------

def test_perf_multiproc():
    results = []
    # run in 8 processes and split problem into chunks. Each chunk is
    # a group of Enigma configurations to try out. Several chunk sizes
    # are tested to determine what the ideal size of a chunk is

    for chunk_size in range(50, 100, 50):
        start = time.time()
        print_results(decrypt_cipher_multiproc("CMFSUPKNCBMUYEQVVDYKLRQZTPUFHSWWAKTUGXMPAMYAFITXIJKMH",
                           "UNIVERSITY",
                           'B Beta-I-III 23-2-10 ?-?-? VH-PT-ZG-BJ-EY-FS', chunk_size))
        end = time.time()
        results.append(end-start)
        print("Time to process with chunk size {0}={1}".format( chunk_size, end - start))

def test_perf_multiproc2():
    results = []
    # run in 8 processes and split problem into chunks. Each chunk is
    # a group of Enigma configurations to try out. Several chunk sizes
    # are tested to determine what the ideal size of a chunk is
    print("Test")
    #for chunk_size in range(1, 6, 3):
    start = time.time()
    chunk_size = 50
    print_results(decrypt_cipher_multiproc("ABSKJAKKMRITTNYURBJFWQGRSGNNYJSDRYLAPQWIAGKJYEPCTAGDCTHLCDRZRFZHKNRSDLNPFPEBVESHPY",
                                    "THOUSANDS",
                                    '? ["II","IV","Beta","Gamma"]-["II","IV","Beta","Gamma"]-["II","IV","Beta","Gamma"] [2,4,6,8,20,22,24,26]-[2,4,6,8,20,22,24,26]-[2,4,6,8,20,22,24,26] E-M-Y FH-TS-BE-UQ-KD-AL', chunk_size))
    end = time.time()
    results.append(end-start)
    print("Time to process with chunk size {0}={1}".format( chunk_size, end - start))
    print(results)

def test_perf_multiproc5():
    results = []
    # run in 8 processes and split problem into chunks. Each chunk is
    # a group of Enigma configurations to try out. Several chunk sizes
    # are tested to determine what the ideal size of a chunk is
    #for chunk_size in range(1, 30, 3):
    chunk_size = 50
    start = time.time()
    print_results(decrypt_cipher_reflector_scrambled_multiproc("HWREISXLGTTBYVXRCWWJAKZDTVZWKBDJPVQYNEQIOTIFX",
                                                         "INSTAGRAM",
                                                         "? V-II-IV 6-18-7 A-J-L UG-IE-PO-NX-WT", chunk_size))
    end = time.time()
    results.append(end-start)
    print("Time to process with chunk size {0}={1}".format( chunk_size, end - start))