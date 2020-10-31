# Enigma simulator and code breaking

  * [1. What is Enigma machine](#1-what-is-enigma-machine)
  * [2. Quick start](#2-quick-start)
  * [3. Implementation](#3-implementation)
    + [3.1 Supported rotors](#31-supported-rotors)
    + [3.1 Supported reflectors](#31-supported-reflectors)
  * [4. Parallelizing code breaking](#4-parallelizing-code-breaking)
    + [4.1. Estimating time required to break a certain code](#41-estimating-time-required-to-break-a-certain-code)
    + [4.2. Breaking the code with multiple worker processes](#42-breaking-the-code-with-multiple-worker-processes)
    + [4.3. Distributing the workload between multiple computers](#43-distributing-the-workload-between-multiple-computers)
    + [4.4 Predicting time required to complete the job in the distributed scenario](#44-predicting-time-required-to-complete-the-job-in-the-distributed-scenario)
  * [5. Running the code](#5-running-the-code)
    + [5.1 Enigma configuration](#51-enigma-configuration)
    + [5.2 Enigma CLI](#52-enigma-cli)
    + [5.3 Set up an Enigma and encrypt some text](#53-set-up-an-enigma-and-encrypt-some-text)
      - [Using CLI](#using-cli)
      - [Using code](#using-code)
    + [5.4 Breaking Enigma code](#54-breaking-enigma-code)
      - [Single process code breaking](#single-process-code-breaking)
        * [Using CLI](#using-cli-1)
        * [Using code](#using-code-1)
      - [Multiprocessing code breaking](#multiprocessing-code-breaking)
        * [Using CLI](#using-cli-2)
        * [Using code](#using-code-2)
      - [Distributed code breaking](#distributed-code-breaking)
        * [Activate clients directly from the command line](#activate-clients-directly-from-the-command-line)
        * [Activate clients using CLI](#activate-clients-using-cli)
        * [Activate clients using code](#activate-clients-using-code)
        * [Activate server directly from the command line](#activate-server-directly-from-the-command-line)
        * [Activate server using CLI](#activate-server-using-cli)
        * [Activate server using code](#activate-server-using-code)


## 1. What is Enigma machine
The Enigma machine is an encryption device developed and used in the early- to mid-20th century to protect commercial, diplomatic and military communication. It was employed extensively by Nazi Germany during World War II, in all branches of the German military.

Enigma has an electromechanical rotor mechanism that scrambles the 26 letters of the alphabet. In typical use, one person enters text on the Enigma's keyboard and another person writes down which of 26 lights above the keyboard lights up at each key press. If plain text is entered, the lit-up letters are the encoded ciphertext. Entering ciphertext transforms it back into readable plaintext. The rotor mechanism changes the electrical connections between the keys and the lights with each keypress. The security of the system depends on a set of machine settings that were generally changed daily during the war, based on secret key lists distributed in advance, and on other settings that were changed for each message. The receiving station has to know and use the exact settings employed by the transmitting station to successfully decrypt a message. [Read more about Enigma on Wikipedia][1]

## 2. Quick start
Run a command line CLI and play around with the Enigma simulator:
```bash
python3 enigma-cli.py --module interactive
```
More instructions in the section 5, Running the code.

## 3. Implementation
First part is a Python simulation of Enigma with 3 or 4 rotors and a Plugboard support. Not every physical limitation of Enigma machine has been respected and so there is no limits in using any rotor / reflector in any place. There is also no limits in the number of plugboard connections (which was 10).

### 3.1 Supported rotors
* Beta:     LEYJVCNIXWPBQMDRTAKZGFUHOS
* Gamma:    FSOKANUERHMBTIYCWLQPZXVGJD
* I:        EKMFLGDQVZNTOWYHXUSPAIBRCJQ
* II:       AJDKSIRUXBLHWTMCQGZNPYFVOEE
* III:      BDFHJLCPRTXVZNYEIWGAKMUSQOV
* IV:       ESOVPZJAYQUIRHXLNFTGKDCMWBJ
* V:        VZBRGITYUPSDNHLXAWMJQOFECKZ

### 3.1 Supported reflectors
* A:       EJMZALYXVBWFCRQUONTSPIKHGD
* B:       YRUHQSLDPXNGOKMIEBFZCWVJAT
* C:       FVPJIAOYEDRZXWGCTKUQSBNMHL
* B_thin:  ENKQAUYWJICOPBLMDXZVFTHRGS
* C_thin:  RDOBJNTKVEHMLFCWZAXGYIPSUQ

Second part is the breaking of Enigma using the method invented by Alan Turing and his team at Bletchley Park. Given the encoded text, a word known to be in the encoded text (crib) and a partially known Enigma configuration the script will try out the all possible Enigma settings and present potential solutions to the user. The code breaking part has been implemented in three ways, as a single process, multiprocessing and distributed between machines.

## 4. Parallelizing code breaking

This document is structured as follows:
* Section 4.1: Estimating time required to break an Enigma code
* Section 4.2: Parallelizing the code breaking of Enigma using multiprocessing
* Section 4.3: Distributing computing to break the Enigma code 
* Section 4.4: Extending the time estimation to the scenario of distributed computing
* Section 4.5: User guide for the Enigma Command Line Interface with common use cases

### 4.1. Estimating time required to break a certain code
Time estimation in a single process code has been implemented by measuring time required to verify a subset of Enigma settings. Assuming that the process will continue with more or less the same speed and knowing the total number of possible Enigma settings the time estimate t = total_settings / sample_speed.

At the beginning the time estimates had an error of up to 40%. After additional measuring it seemed that the time required to check an Enigma setting has an upward trend:

<img src="https://github.com/andrejlukic/enigma-simulator/blob/master/presentation/files/001_time_estimates_before_shuffle.png">

This is due to the nature of checking an Enigma configuration. It takes more processing when crib is not at position 0 and rotors have to be first rotated to the correct position. Enigma settings with crib at position 0 were mostly at the beginning of the list. This was solved by randomizing the order of Enigma settings before attempting to measure time, which removed the upward trend:

<img src="https://github.com/andrejlukic/enigma-simulator/blob/master/presentation/files/002_time_estimates_after_shuffle.png">

Various sample sizes were tried, below are averages of sets of 3 measurements per sample size. The sample sizes of less than 50 gave too inaccurate results. Since there is no real penalty in chosing a larger sample size of 1000 has been used throughout the rest of the code.

| Sample size |	Predicted (sec) |	Measured (sec) |	% Err |	Stddev predicted |	Stddev measured |
|---|---|---|---|---|---|
| 10 | 128,1 | 121,6 | 15,4% | 27,5 | 0,2 |
| 25 | 115,3 | 121,3 | 5,0% | 2,9 | 0,2 |
| 50 | 120,6 | 121,3 | 4,4% | 6,8 | 0,1 |
| 100 | 124,9 | 120,5 | 3,6% | 3,7 | 0,5 |
| 150 | 118,3 | 121,0 | 2,3% | 2,9 | 1,4 |
| 200 | 117,9 | 119,8 | 2,6% | 3,8 | 0,3 |
| 500 | 123,9 | 122,0 | 1,8% | 2,5 | 0,8 |
| 1000 | 120,3 | 121,4 | 2,0% | 2,6 | 0,5 |

Overall estimating time required to check all possible Enigma settings makes sense if ran in a single process. In the section about multiprocessing and distribute computing it will also be shown how this method is not good enough for that scenario.

### 4.2. Breaking the code with multiple worker processes
Since breaking Enigma code is a  CPU intensive process and most of modern CPUs feature more than one core it makes sense to split up the workload into several processes. Only default Python libraries were used to do so. For this the decrypt_cipher function has been rewritten so that the workload (list of Enigma settings to verify) has been split in chunks and then those chunks were distributed amongst the processes in a process pool. The number of processes was determined by the number of CPU cores. So an 8 core CPU would be using 8 processes. 

The first question that arose was the size of the chunks. If chunks were too small, then overhead for switching between processes was to big. And if the chunk was too big, than the probability of longer execution time increased, since it could happen that all of the processes had finished and  waiting for the last processes to work on its last chunk. The following measurements show that for chunk sizes of less than 20 the overhead is too big compared to the gain from parallelizaton. However these measurements also show the nice performance gain from parallelizing the processing of the workload:

<img src="https://github.com/andrejlukic/enigma-simulator/blob/master/presentation/files/004_time_vs_chunksize_2.png" style="width: 800px;">

<img src="https://github.com/andrejlukic/enigma-simulator/blob/master/presentation/files/005_time_vs_chunksize_3.png" style="width: 800px;">

### 4.3. Distributing the workload between multiple computers
An obvious next step after parallelizing the workload by using multiple processes on a single computer was to use multiple computers connected in a network. The approach is based on the [article published by Eli Bendersky](https://eli.thegreenplace.net/2012/01/24/distributed-computing-in-python-with-multiprocessing) and uses a job queue and a result queue and only default Python libraries. This method has been adapted to work with the Enigma code breaker. In the architecture presented below a server defines the workload and splits it into chunks. The chunk sizes has been kept the same as in section 2. The workload is fed into a work queue and another result queue is initialized by the server. Any number of clients can connect to the work queue and take workload out until the queue is empty. At the same time the result queue is filled with results. Architecture diagram is drawn below:

<img src="https://github.com/andrejlukic/enigma-simulator/blob/master/presentation/files/007_arch_enigma_distributed.png" style="width: 500px;">

In the example used to test this implementation the following 7 machines were used to share the workload:
* Laptop with an Intel i5 CPU (MacBook Pro)
* 3x Raspberry PI 4B client
* 1x Raspberry PI 3A+ client
* 2x Raspberry PI Zero client

The first important point to measure was the performance loss due to managing of two queues and client / server communication. For sanity check the performance of the multiprocessing implementation described in section 2 was compared to the performance of the distributed implementation where both, server and client are running on the same machine. Every measurement was repeated 4 times and mean was calculated. The graph shows time in seconds to break the code of Enigma with the crib THOUSANDS and encrypted text ABSKJAKKMRITTNYURBJFWQGRSGNNYJSDRYLAPQWIAGKJYEPCTAGDCTHLCDRZRFZHKNRSDLNPFPEBVESHPY:

<img src="https://github.com/andrejlukic/enigma-simulator/blob/master/presentation/files/008_perf_single_multi_distri_single_server.png" style="width: 500px;">

|Setup|Time to break code (seconds)|
|---|---|
| Laptop (single process) | 131,8s |
| Laptop (multiprocessing) | 42,5s |
| Laptop (server + client multiprocessing) | 47,1s |

This shows that having to taking care of two queues and network connection even on the same machine reduces performance for 10.8% and it still offers a big advantage (280%) over running the task in a single process. The next step was determining how much adding a much weaker computer like a Raspberry PI to share the load could improve the execution times. First the performance of a single Raspberry PI 4B and the work laptop are compared. The measurements were repeated 4 times on the same code breaking example. (here, Raspberry PI has an additional disadvantage of having to communicate over the LAN):

<img src="https://github.com/andrejlukic/enigma-simulator/blob/master/presentation/files/009_perf_RPi4B_vs_MacBook_i5.png" style="width: 300px;">

|Setup|Time to break the code|
|---|---|
| Laptop (server + client) | 47,1s |
| Laptop (server) + 1x Rpi 4B as client | 178,1s |

The difference is big (378%) so even though there are multiple Raspberry PIs in the network the expected gain won't be drastic. Comparing time required to break the code on a single laptop and the time required to break the code where an additional Raspberry PI 4B is sharing the work load gives an approximately 20.5% improvement when repeating the same test:

<img src="https://github.com/andrejlukic/enigma-simulator/blob/master/presentation/files/011_perf_macbook_vs_one_added_RPI4B.png" style="width: 400px;">

| Setup | Time to break code (seconds) |
|---|---|
| L (S+C) | 47,1s |
| L (S+C) + 1x Rpi 4B |	39,1s |

Another interesting point was sensibility of adding the very slow version of Raspberry PIs called PI Zero. Those computers were not made for performance, but rather as an educational tool and/or specific tasks. The same test, when repeated with and without 2 Raspberry PI Zero computers, showed that Raspberry PI Zero is too slow to add any performance gain. The overhead of having both computers in the distributed network is even slightly bigger than the gain:

<img src="https://github.com/andrejlukic/enigma-simulator/blob/master/presentation/files/012_adding_two_zeros_or_not.png" style="width: 400px;">

| Setup | Time to break code (seconds) |
|---|---|
| Laptop server and client running 2 cores + 2x Rpi 4B + 1x Rpi3B + 1x Rpi A+ + 2x Rpi Zero W | 36,7s |
| Laptop server and client running 2 cores + 2x Rpi 4B + 1x Rpi3B + 1x Rpi A+ |35,8s |

Another topic that needs mentioning is how much resources a client should use in the scenario where both client and server are running on the same machine. Since the laptop was comparably fast it makes sense to keep it as a client, however when using up all the CPU cores as a client the results of measurements were unstable and high variance was noted. After trying multiple options in the end the best performance was achieved by having the laptop run as a client with 6 out of 8 cores and keeping the remaining 2 cores free to do its job as a server. On the client side only the faster Raspberry PIs were deployed (4B, 3B and 3A+) and the low performing PI Zeros were excluded. The result achieved was a 49% shorter time required to break the code on a single laptop multiprocessing:

<img src="https://github.com/andrejlukic/enigma-simulator/blob/master/presentation/files/013_perf_final.png" style="width: 400px;">

| Setup | Time to break code (seconds) |
|---|---|
| Laptop running a single process | 131,8s
| Laptop multiprocessing (8) | 42,5s
| Laptop server and client multiprocessing (8) | 47,1s
| Laptop server and client running 6/8 cores + 2x Rpi 4B + 1x Rpi3B + 1x Rpi A+ | 28,5s |



<img src="https://github.com/andrejlukic/enigma-simulator/blob/master/presentation/files/010_perf_comparison_architecture_all.png" style="width: 800px;">

| Setup | Time to break code (seconds) |
|---|---|
| Laptop running a single process | 131,8s |
| Laptop multiprocessing (8) | 42,5s |
| Laptop server and laptop client (8 cores) | 47,1s |
| Laptop server. Clients: laptop  (8 cores), RPI 4B as a client | 39,1s |
| Laptop server. Clients: RPI 4B | 178,1s |
| Laptop server. Clients: 2x RPI 4B | 109,8s |
| Laptop server. Clients: 2x RPI 4B, 1x RPI 3B | 91,5s |
| Laptop server. Clients: 2x RPI 4B, 1x RPI 3B, 1x RPI 3B, 1x RPI A+, 2x RPI Zero W | 56,9s |
| Laptop server. Clients: Laptop (2 cores), 2x RPI 4B, 1x RPI 3B, 1x RPI 3B, 1x RPI A+, 2x RPI Zero W | 36,7s |
| Laptop server. Clients: Laptop (2 cores), 2x RPI 4B, 1x RPI 3B, 1x RPI 3B, 1x RPI A+ | 35,8s |
| Laptop server. Clients: Laptop (6 cores), 2x RPI 4B, 1x RPI 3B, 1x RPI 3B, 1x RPI A+ | 28,5s |

For the end a short demo video of distributed Enigma code breaking in action: https://youtu.be/kgZlp_Cw6Kw


### 4.4 Predicting time required to complete the job in the distributed scenario

One last part that took disproportionately lots of time and can be considered failed was an attempt to predict the time required to finish the job in a distributed scenario. As described in section 1 in the single process scenario the simple approach of measuring time to complete a subset of tasks worked because there is no process / network / queue overhead. An assumption was that inside a LAN the overhead might be small enough that if each client process sends its own time prediction calculated on a sample and the server collects predictions from all the clients, then a total prediction of time required to complete the job could be of some value. The process tested was as follows:

1. Clients connect to the job queue and start pulling chunks of work
2. Every process on every client measures the time required to complete a subset of tasks (sample)
3. Every process on every client sends its estimated speed to the server
4. Server collects speed estimates from every process from every client and knowing the total size of the job attempts to estimate the total time required to finish the job. If a new client joins then the time is adjusted. 

Here is a screenshot of this process in action:

<img src="https://github.com/andrejlukic/enigma-simulator/blob/master/presentation/files/014_clients_send_speed_estimates.png" style="width: 600px;">

The results were consistently underestimated times in the range of 20%. It is obvious that without having a good way to account for the network / process / queue overhead this method won't work. Since it makes little sense the measurements will not be included here.

## 5. Running the code

The simplest way to set up an Enigma, play with it and run code deciphering scripts is using the command line interface in enigma-cli.py. The CLI leads user through the menus, already has a set of predefined demo Enigma settings prepared as well as demo settings for the code breaking part. 

### 5.1 Enigma configuration
Enigma configuration can be written for both 3 or 4 rotor Enigma in a single string. An input string like: 
* B_thin Beta-I-II-III 4-24-17-7 V-E-Q-F AT-LU-NR-IG
will be interpreted as:
* Rotors from right to left: III, II, I, Beta
* Reflecter: B_thin
* Rotor positions right to left: F, Q, E, V (V being the position of the left-most rotor)
* Ring setting right to left: 7, 17, 24, 4 (4 being the ring setting of the left-most rotor)
* Plugboard settings (optional): AT, LU, NR, IG

### 5.2 Enigma CLI
An example of using a CLI to set up an Enigma a´machine and encrypt some text:

```bash
python3 enigma-cli.py --module interactive

Entering interactive mode. Navigate by entering the number of a choice.

1	Enigma simulator
2	Enigma code breaker / distributed server
3	Enigma distributed client
4	Exit

1


1	Use default setting - A IV-V-Beta-I 18-24-3-5 E-Z-G-P PC-XZ-FM-QA-ST-NB-HY-OR-EV-IU
2	Enter custom setting
3	Return


2

Enter Enigma settings in format RF R4-R3-R2-R1 RS4-RS3-RS2-RS1 POS4-POS3-POS2-POS1 XY-QZ
Example: A IV-V-Beta-I 18-24-3-5 E-Z-G-P PC-XZ-FM-QA-ST-NB-HY-OR-EV-IU
A IV-V-Beta-I 18-24-3-5 E-Z-G-P PC-XZ-FM-QA-ST-NB-HY-OR-EV-IU

String to encrypt / decrypt:
DAYSAREGETTINGSHORTER
WGJIDWIWOKASLMDOINWBS
```

Note: All examples using CLI will from here onwards will omit the menus.

### 5.3 Set up an Enigma and encrypt some text

#### Using CLI
Start CLI, enter 1 for Enigma Simulator, then 2 for custom settings. Enter Enigma settings and encode some text:
```bash
python3 enigma-cli.py --module interactive
```

```bash
String to encrypt / decrypt:
DAYSAREGETTINGSHORTER
WGJIDWIWOKASLMDOINWBS
```

#### Using code
```python
from enigma import *

plaint_text = "DAYSAREGETTINGSHORTER"
settings = 'C II-Gamma-IV 24-8-20 E-M-Y FH-TS-BE-UQ-KD-AL'

encoded = Enigma(EnigmaConfig
                 .from_config_string(settings))
                 .encode_string(plaint_text)
print(encoded)
```

### 5.4 Breaking Enigma code
All examples of code breaking will be based on the example of Enigma settings:

? ["II","IV","Beta","Gamma"]-["II","IV","Beta","Gamma"]-["II","IV","Beta","Gamma"] [2,4,6,8,20,22,24,26]-[2,4,6,8,20,22,24,26]-[2,4,6,8,20,22,24,26] E-M-Y FH-TS-BE-UQ-KD-AL

Interpret this string as:
* Reflector unknown
* Leftmost rotor one of "II","IV","Beta","Gamma" and the same logic for other rotors
* Leftmost rotor ring settings one of 2,4,6,8,20,22,24,26 and the same logic for other rotor ring settings
* Rotor starting positions E,M,Y
* Plugboard configuration: FH-TS-BE-UQ-KD-AL

#### Single process code breaking

##### Using CLI
Start CLI, enter 2 for code breaking, then 1 for predefined demo job, then 1 for the single process code breaker:
```bash
python3 enigma-cli.py --module interactive

```

```bash
Running a single process to find solutions.
1916928 settings to search
Estimated 119.35 and 131.91 seconds left. 1916428 remaining.
132 seconds

Solutions:

SQUIRRELSPLANTTHOUSANDSOFNEWTREESEACHYEARBYMERELYFORGETTINGWHERETHEYPUTTHEIRACORNS
C II-Gamma-IV 24-8-20 E-M-Y FH-TS-BE-UQ-KD-AL

```

##### Using code
```python
import code_breaking

cipher = "ABSKJAKKMRITTNYURBJFWQGRSGNNYJSDRYLAPQWIAGKJYEPCTAGDCTHLCDRZRFZHKNRSDLNPFPEBVESHPY"
crib = "THOUSANDS"
settings = '? ["II","IV","Beta","Gamma"]-["II","IV","Beta","Gamma"]-["II","IV","Beta","Gamma"] [2,4,6,8,20,22,24,26]-[2,4,6,8,20,22,24,26]-[2,4,6,8,20,22,24,26] E-M-Y FH-TS-BE-UQ-KD-AL'

solutions = code_breaking.decrypt_cipher(cipher, crib, settings)
```

#### Multiprocessing code breaking

##### Using CLI
Start CLI, enter 2 for code breaking, then 1 for predefined demo job, then 2 for the multprocessing code breaker:
```bash
python3 enigma-cli.py --module interactive

```

```bash
Distributed amongst 8 processes to find solutions.
Searching through 1916928 Enigma settings split in chunks of 50
45 seconds

Solutions:

SQUIRRELSPLANTTHOUSANDSOFNEWTREESEACHYEARBYMERELYFORGETTINGWHERETHEYPUTTHEIRACORNS
C II-Gamma-IV 24-8-20 E-M-Y FH-TS-BE-UQ-KD-AL

```

##### Using code
```python
import code_breaking_multiproc

cipher = "ABSKJAKKMRITTNYURBJFWQGRSGNNYJSDRYLAPQWIAGKJYEPCTAGDCTHLCDRZRFZHKNRSDLNPFPEBVESHPY"
crib = "THOUSANDS"
settings = '? ["II","IV","Beta","Gamma"]-["II","IV","Beta","Gamma"]-["II","IV","Beta","Gamma"] [2,4,6,8,20,22,24,26]-[2,4,6,8,20,22,24,26]-[2,4,6,8,20,22,24,26] E-M-Y FH-TS-BE-UQ-KD-AL'

solutions = code_breaking_multiproc.decrypt_cipher_multiproc(cipher, crib, settings)
```

#### Distributed code breaking
Start by activating all the clients, they will wait until server start the work queue and they can start working. After all the clients are up start the server as well. Server and clients can be either started using the interactive CLI or using command line arguments. A short demo can be seen in this video: https://youtu.be/kgZlp_Cw6Kw

##### Activate clients directly from the command line
A client requires server IP address and optionally number of processes to run:
```bash
python3 enigma-cli.py --module distributed --component client --serverip 192.168.0.229

```

```bash
Waiting for 192.168.0.229 to give me a job ...
```

##### Activate clients using CLI
Start CLI, enter 3 for code breaking client, then enter IP address of the server and optionally choose number of processes to deploy for working on a job. After starting client will wait for the server to give it job:
```bash
python3 enigma-cli.py --module interactive

```

```bash
Waiting for 192.168.0.229 to give me a job ...
```

#####  Activate clients using code
```python
import code_breaking_multiproc

server_ip = "192.168.0.229"
proc_num = 4
code_breaking_distributed.runclient(server_ip, cpus=proc_num)
```

##### Activate server directly from the command line
A server is the one setting up the job for the clients so basic information about the job has to be entered (crib, ciphertext, partially known Enigma settings).

```bash
python3 enigma-cli.py --module distributed --component server

```

```bash
Server started at 192.168.0.229:22222
Run one or multiple clients to share the work (-m client -ip 192.168.0.229 [-cpus N])
1916928 settings in chunks of 50 to distribute amongst clients
```

##### Activate server using CLI
Start CLI, enter 2 for code breakinger, then enter 1 for the demo job (or specify your own), then enter 3 to start up the server:

```bash
python3 enigma-cli.py --module interactive

```

```bash
Server started at 192.168.0.229:22222
Run one or multiple clients to share the work (-m client -ip 192.168.0.229 [-cpus N])
1916928 settings in chunks of 50 to distribute amongst clients
```

#####  Activate server using code
```python
import code_breaking_multiproc

cipher = "ABSKJAKKMRITTNYURBJFWQGRSGNNYJSDRYLAPQWIAGKJYEPCTAGDCTHLCDRZRFZHKNRSDLNPFPEBVESHPY"
crib = "THOUSANDS"
settings = '? ["II","IV","Beta","Gamma"]-["II","IV","Beta","Gamma"]-["II","IV","Beta","Gamma"] [2,4,6,8,20,22,24,26]-[2,4,6,8,20,22,24,26]-[2,4,6,8,20,22,24,26] E-M-Y FH-TS-BE-UQ-KD-AL'

solutions = code_breaking_distributed.runserver(cipher, crib, settings)
```


[1]: https://en.wikipedia.org/wiki/Enigma_machine
