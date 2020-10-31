import sys # for the demo
import argparse # for the demo
import time
import multiprocessing as mp
import socket # to get server ip address
from enigma import *
import code_breaking
import code_breaking_multiproc
import code_breaking_distributed

def print_results(solutions):
    # ('B V-II-IV 6-18-7 A-J-L UG-IE-PO-NX-WT', 'YOUCANFOLLOWMYDOGONINSTAGRAMATTALESOFHOFFMANN')
    # or
    # ('B V-II-IV 6-18-7 A-J-L UG-IE-PO-NX-WT', 'YOUCANFOLLOWMYDOGONINSTAGRAMATTALESOFHOFFMANN', 'PQUHRSLDYXNGOKMABEFZCWVJIT')
    print("{0} seconds".format(round(solutions[1])))
    print("\nSolutions:")
    try:
        for solution in solutions[0]:
            print("\n{0}".format(solution[1]))
            print("{0}".format(solution[0]))
            if (len(solution) > 2):
                print("{0}".format(solution[2]))
    except:
        print(solutions)
    print("\n")

def cli_configure_enigma():
    ENIGMA_DEFAULT = "A IV-V-Beta-I 18-24-3-5 E-Z-G-P PC-XZ-FM-QA-ST-NB-HY-OR-EV-IU"
    print("\n")
    print("1\tUse default setting - {0}".format(ENIGMA_DEFAULT))
    print("2\tEnter custom setting")
    print("3\tReturn")
    print("\n")
    choice = input().strip()
    if (choice == '1'):
        return Enigma(EnigmaConfig.from_config_string(ENIGMA_DEFAULT))
        print("Setting Enigma to {0}".format(ENIGMA_DEFAULT))
    elif (choice == '2'):
        print(
            "Enter Enigma settings in format RF R4-R3-R2-R1 RS4-RS3-RS2-RS1 POS4-POS3-POS2-POS1 XY-QZ")
        print("Example: A IV-V-Beta-I 18-24-3-5 E-Z-G-P PC-XZ-FM-QA-ST-NB-HY-OR-EV-IU")
        settings = input().strip()
        return Enigma(EnigmaConfig.from_config_string(settings))
    else:
        return None

def cli_select_codebreaker():
    print("\n")
    print("1\tSingle process code breaker")
    print("2\tMulti process code breaker")
    print("3\tDistributed code breaker server (run clients first)")
    print("4\tReturn")
    print("\n")

    choice = input().strip()
    if (choice == '1'):
        if not reflector_swap:
            return code_breaking.decrypt_cipher
        else:
            return code_breaking.decrypt_cipher_reflector_scrambled
    elif (choice == '2'):
        if not reflector_swap:
            return code_breaking_multiproc.decrypt_cipher_multiproc
        else:
            return code_breaking_multiproc.decrypt_cipher_reflector_scrambled_multiproc
    elif (choice == '3'):
        return code_breaking_distributed.runserver
    else:
        return None

def cli_define_distributed_client(last_ip):
    '''Get IP of the distributed server and define
    how many CPU cores to use on the client

    :param last_ip:
    :return:
    '''

    cpu_cores = mp.cpu_count()
    if (last_ip):
        print("Reuse last server ip {0}?".format(last_ip))
        if (input().strip() != 'y'):
            last_ip = None
    if (not last_ip):
        ip = socket.gethostbyname(socket.gethostname())
        print("Server ip address: (hit enter to use {0})".format(ip))
        last_ip = ip
        custom_ip = input().strip()
        if (custom_ip):
            last_ip = custom_ip
            print("IP:{0}".format(last_ip))
    #print("{0} cores available".format(cpu_cores))
    print("Type number of cores to use or hit Enter to keep all {0}:".format(cpu_cores))
    cores = input().strip()
    if (cores):
        cpu_cores = int(cores)
        print("changed to {0}".format(cpu_cores))
    return last_ip, cpu_cores

def cli_define_codebreaking_job():
    '''Define partially known Enigma settings, encoded text and crib to start
    the code breaking job

    :return:
    '''
    DEMO_CYPHER = "ABSKJAKKMRITTNYURBJFWQGRSGNNYJSDRYLAPQWIAGKJYEPCTAGDCTHLCDRZRFZHKNRSDLNPFPEBVESHPY"
    DEMO_CRIB = "THOUSANDS"
    DEMO_SETTINGS = '? ["II","IV","Beta","Gamma"]-["II","IV","Beta","Gamma"]-["II","IV","Beta","Gamma"] [2,4,6,8,20,22,24,26]-[2,4,6,8,20,22,24,26]-[2,4,6,8,20,22,24,26] E-M-Y FH-TS-BE-UQ-KD-AL'

    print("\n")
    print("\nDefine a job for the Enigma code breaker.")
    print("1\tDemo job ({0})".format(DEMO_CRIB))
    print("2\tCustom job")
    print("3\tReturn")
    print("\n")

    choice = input().strip()
    if (choice == '2'):
        print("Partially known Enigma settings:")
        settings = input().strip()
        print("Crib (a word known to be in the text):")
        crib = input().strip()
        print("Encoded text:")
        encoded_text = input().strip()
        print("Hit 'r' for the special case where reflector had 2 wires swapped:")
        reflector_swap = input().strip() == 'r'
    elif (choice == '1'):
        settings = DEMO_SETTINGS
        crib = DEMO_CRIB
        encoded_text = DEMO_CYPHER
        print("Enigma settings:\t", DEMO_SETTINGS)
        print("Encoded text:\t", DEMO_CYPHER)
        print("Crib:\t", DEMO_CRIB)
        reflector_swap = False
    else:
        return None
    return settings, crib, encoded_text, reflector_swap

if __name__ == "__main__":
    last_server_ip = None
    executable = sys.argv[0]

    print("\n#\tThis is a simple command line interface for testing the Enigma simulator.")
    print("#\tInteractive mode allows to try out Enigma as well as break its code.")
    print("#\tSupported code breaking: single process, multiple processes, distributed")
    print("#\tTo run interactive mode simply run {0} with no arguments".format(executable))
    print("#")
    print("#\tDistributed mode runs a server and a any number of clients to work on the code breaking job")
    print("#\tFirst run all the clients and they will wait for the server to become available")
    print("#\tto run a client: {0} --module distributed --component client --serverip 192.168.0.229".format(executable))
    print("#\tto run a server: {0} --module distributed --component server\n\n".format(executable))

    parser = argparse.ArgumentParser(description='Simulate Enigma machine')
    parser.add_argument('--module', choices=['interactive', 'distributed'], help='Run interactive cli or distributed client / server')
    parser.add_argument('--component', choices=['client', 'server'], help="Distributes code breaking client / server")
    parser.add_argument('--serverip', help="IP of distributed server")
    parser.add_argument('--procnum', type=int, help="Number of processes to use")
    parser.add_argument('--loop', type=bool, help="After distributed client / server finishes run again with the same settings")
    parser.set_defaults(module="interactive", serverip="127.0.0.1", procnum=0, component="client", loop=False)
    args = parser.parse_args()

    if args.module == 'interactive':
        print("Entering interactive mode. Navigate by entering the number of a choice.\n")
        while True:
            print("1\tEnigma simulator")
            print("2\tEnigma code breaker / distributed server")
            print("3\tEnigma distributed client")
            print("4\tExit")
            print("\n")

            choice = input().strip()
            if (choice == '1'):
                # play with simulated Enigma machine:
                while True:
                    machine = cli_configure_enigma()
                    if not machine:
                        break
                    # use configured enigma to encrypt some text:
                    while True:
                        print("String to encrypt / decrypt:")
                        text = input().strip()
                        print(machine.encode_string(text.upper()))
                        print("\n")
                        print("Press 'y' for another string or any key to go back")
                        text = input().strip()
                        if (text != 'y'):
                            break
            elif (choice == '3'):
                # run a distributed code breaking client
                last_server_ip, cpus = cli_define_distributed_client(last_server_ip)
                code_breaking_distributed.runclient(last_server_ip, cpus)
            elif (choice == '2'):
                # Define a code breaking job and run code breaking in a single or
                # multiple processes or start a distributed server
                while True:
                    job = cli_define_codebreaking_job()
                    if not job:
                        break

                    settings = job[0]
                    crib = job[1]
                    encoded_text = job[2]
                    reflector_swap = job[3]

                    while True:
                        breaker = cli_select_codebreaker()
                        solutions = breaker(encoded_text, crib, settings)
                        print_results(solutions)
    elif(args.module == 'distributed'):
        # just a more convenient way to start a distributed server / client
        keep_running = True
        if(args.component == "server"):
            job = cli_define_codebreaking_job()
            if job:
                settings = job[0]
                crib = job[1]
                encoded_text = job[2]
                reflector_swap = job[3]

                while (keep_running):
                    solutions = code_breaking_distributed.runserver(encoded_text, crib, settings)
                    print_results(solutions)
                    keep_running = args.loop
                    if(keep_running):
                        time.sleep(2) # wait for clients to get ready
        else:
            # run client
            while(keep_running):
                server_ip = args.serverip
                processes = args.procnum
                code_breaking_distributed.runclient(server_ip, cpus=processes)
                keep_running = args.loop



