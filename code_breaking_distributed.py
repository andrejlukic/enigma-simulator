import platform                                     # to get the hostname of the client machine
import socket                                       # to get the ip address of the server
import multiprocessing as mp                        # multiprocessing on the client
from multiprocessing.managers import SyncManager    # For the job and result queue
from queue import Queue, Empty                      # For the job and result queue
from code_breaking_utils import *

#   This is the improved Enigma brute force code breaking that runs distributed
#   The work load is defined by the server and shared by 1 or more client machines.
#   The code has been adapted from this article:
#   https://eli.thegreenplace.net/2012/01/24/distributed-computing-in-python-with-multiprocessing
#
#   Quick start
#   Start by activating all the clients, they will wait until server starts the work queue.
#   A client requires server IP address and optionally number of processes to run:
#       python3 enigma-cli.py --module distributed --component client --serverip 192.168.0.229
#
#   After all the clients are up start the server as well:
#       python3 enigma-cli.py --module distributed --component server
#
#   A short demo can be seen in this video: https://youtu.be/kgZlp_Cw6Kw
#
#   Client part
#       runclient(srv_ip, sample = 1000, cpus = 0)

PORTNUM = 22222         # port used to connect to the server
AUTHKEY = b'authkey'    # basic authentication between client / server
SAMPLE = 1000           # number of Enigma settings to make time estimate on


def mp_check_enigma_config(shared_job_q, shared_result_q, sample, cpus):
    '''Pulls a chunk of Enigma work load from the job queue and
    verifies the Enigma settings. Sends the results back to the results queue

    After "sample" of Enigma settings have been checked sends speed to the
    queue so server can make time predictions for the complete calculation

    :param shared_job_q:
    :param shared_result_q: Result queue for potential solutions
    :param sample: # number of Enigma settings to make time estimate on
    :param cpus: number of cores (processes) used.
    :return:
    '''


    total_searched = 0
    speed_sent = False
    time_start = time.time()
    while True:
        try:
            job = shared_job_q.get_nowait()
            result = check_enigma_config(job[0], job[1], job[2])
            if (result):
                shared_result_q.put((platform.node(), result))
            total_searched += len(job[0])
            if(sample > 0 and total_searched > sample and not speed_sent):
                speed = total_searched / (time.time() - time_start)
                shared_result_q.put("SPEED,{0},{1},{2}".format(speed, platform.node(), cpus))
                speed_sent = True
        except Empty:
            return

def runclient(srv_ip, sample = 1000, cpus = 0):
    '''Waits for the server to come online. Then runs a number of processes
    and pulls chunks of Enigma settings to check for solutions

    :param srv_ip:  string IP of the server e.g. "192.168.0.229"
    :param sample:  sample: # number of Enigma settings to make time estimate on
    :param cpus:    number of cores / processes to use. 0 = all
    :return:
    '''


    print("Waiting for {0} to give me a job ...".format(srv_ip))
    server_online = False
    while(not server_online):
        try:
            manager = make_client_manager(srv_ip, PORTNUM, AUTHKEY)
            server_online = True
        except:
            time.sleep(0.300)
    time.sleep(0.500)

    job_q = manager.get_job_q()
    result_q = manager.get_result_q()
    cpu_cores = mp.cpu_count()
    if(cpus > 0):
        # limit number of CPU cores to use
        cpu_cores = cpus
    print("Connected. Using {0} cpu cores".format(cpu_cores))

    procs = []
    for i in range(cpu_cores):
        p = mp.Process(
            target=mp_check_enigma_config,
            args=(job_q, result_q, sample, cpu_cores))
        procs.append(p)
        p.start()

    for p in procs:
        p.join()
    # all jobs finished, send a final sentinel to the server
    result_q.put("FINAL,{0}".format(platform.node()))
    return

def make_client_manager(ip, port, authkey):
    """ Create a manager for a client. This manager connects to a server on the
        given address and exposes the get_job_q and get_result_q methods for
        accessing the shared queues from the server.
        Return a manager object.
    """


    class ServerQueueManager(SyncManager):
        pass

    ServerQueueManager.register('get_job_q')
    ServerQueueManager.register('get_result_q')

    manager = ServerQueueManager(address=(ip, port), authkey=authkey)
    manager.connect()

    print('Client connected to {0}{1}'.format(ip, port))
    return manager


# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# -----------------------   server part
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------


def make_server_manager(port, authkey):
    """ Creates a manager for the server, listening on the given port.
        Returns a manager object with get_job_q and get_result_q methods.
    """

    job_q = Queue()
    result_q = Queue()

    # This is based on the examples in the official docs of multiprocessing.
    # get_{job|result}_q return synchronized proxies for the actual Queue
    # objects.
    class JobQueueManager(SyncManager):
        pass

    JobQueueManager.register('get_job_q', callable=lambda: job_q)
    JobQueueManager.register('get_result_q', callable=lambda: result_q)

    manager = JobQueueManager(address=('', port), authkey=authkey)
    manager.start()
    ip = socket.gethostbyname(socket.gethostname())
    print('\nServer started at {0}:{1}'.format(ip, port))
    print("Run one or multiple clients to share the work (-m client -ip {0} [-cpus N])".format(ip))
    return manager

def display_speed_pred(clients, total_enigma_configs, elapsed_time):
    total_speed = 0
    for name in clients:
        total_speed += sum(clients[name])
    # adding 20% to the estimated time is a desperate way to estimate
    # the queue overhead. It doesn't work well and TODO here
    estimated_time = (total_enigma_configs/(total_speed))*1.2
    remaining_time = estimated_time - elapsed_time
    #print("Elapsed:", elapsed_time)
    return estimated_time, remaining_time, total_speed

def runserver(encrypted_text, crib, config_string, chunk_size = 50):
    """Start a shared manager server and access its queues. Add batches of
    Enigma settings to the job queue to be picked up by workers.

    :param encrypted_text:
    :param crib:
    :param config_string:
    :param chunk_size:
    :return:
    """
    # Start a shared manager server and access its queues
    manager = make_server_manager(PORTNUM, AUTHKEY)
    shared_job_q = manager.get_job_q()
    shared_result_q = manager.get_result_q()
    start_time = time.time()

    # Construct all possible Enigma settings based on unknown / partially known
    # Enigma configuration provided:
    enigma_configs = all_possible_settings(config_string)
    # Slide the crib under the encrypted text and determine all positions in
    # which the letter of the crib does not match the encrypted text
    # (Enigma can never encode a letter into itself)
    crib_positions = possible_crib_positions(encrypted_text, crib)

    # Prepare all Enigma settings / crib tuples and put them into the job
    # queue to be picked up by workers
    total_count = 0
    batch_items = 0
    batch = []
    results = []
    for pos in crib_positions:
        for cnf in enigma_configs:
            batch.append((cnf, pos))
            batch_items += 1
            total_count += 1
            if batch_items >= chunk_size:
                shared_job_q.put((batch, crib, encrypted_text))
                batch_items = 0
                batch = []
    if(batch): # last batch probably partial
        shared_job_q.put((batch, crib, encrypted_text))

    print("{0} settings in chunks of {1} to distribute amongst clients".format(len(enigma_configs) * len(crib_positions), chunk_size))

    # Wait until all results are ready in shared_result_q
    clients = {}
    while True:
        client_results = shared_result_q.get()
        if not isinstance(client_results, str):
            # Worker sent potential solution
            #print("{0} solved = {1}".format(client_results[0], client_results[1]))
            # distributed clients add hostname to results, need to pack hostname
            # with the results
            results = list(itertools.chain(results, [(client_results[0],) + r for r in client_results[1]]))
        elif(client_results.startswith("SPEED")):
            # Worker sends its speed (once for each core / process)
            speed = float(client_results.split(',')[1])
            name = client_results.split(',')[2]
            cpus = int(client_results.split(',')[3])
            if not name in clients:
                clients[name] = []
            clients[name].append(speed)
            if len(clients[name]) == cpus:
                # last worker's core sends speed, calculate average speed for worker
                print("\n{0} joined with speed {1} settings / second working with {2} cores."
                      .format(name, round(sum(clients[name])), cpus))
                estimated_time, remaining_time, total_speed = display_speed_pred(clients,
                                                                                 total_count,
                                                                                 time.time() - start_time)
                print("Estimated time: {0} at speed: {1}".format(round(estimated_time), round(total_speed)))
        elif (client_results.startswith("FINAL")):
            # Worker finished all jobs and exited.
            name = client_results.split(',')[1]
            # print("{0} finished.".format(name))
            del clients[name]
            if(len(clients) <= 1):
                # Last client finished
                end_time = time.time()
                break

    #print("{0} seconds".format(round(end_time-start_time)))
    #print(results)

    # Sleep a bit before shutting down the server - to give clients time to
    # realize the job queue is empty and exit in an orderly way.
    time.sleep(2)
    manager.shutdown()
    return results, end_time-start_time