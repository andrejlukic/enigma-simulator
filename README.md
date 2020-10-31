# enigma-simulator

### What is Enigma machine?
The Enigma machine is an encryption device developed and used in the early- to mid-20th century to protect commercial, diplomatic and military communication. It was employed extensively by Nazi Germany during World War II, in all branches of the German military.

Enigma has an electromechanical rotor mechanism that scrambles the 26 letters of the alphabet. In typical use, one person enters text on the Enigma's keyboard and another person writes down which of 26 lights above the keyboard lights up at each key press. If plain text is entered, the lit-up letters are the encoded ciphertext. Entering ciphertext transforms it back into readable plaintext. The rotor mechanism changes the electrical connections between the keys and the lights with each keypress. The security of the system depends on a set of machine settings that were generally changed daily during the war, based on secret key lists distributed in advance, and on other settings that were changed for each message. The receiving station has to know and use the exact settings employed by the transmitting station to successfully decrypt a message. [Read more about Enigma on Wikipedia][1]

### Implementation
First part is a Python simulation of Enigma with 3 or 4 rotors and a Plugboard support. Not every physical limitation of Enigma machine has been respected and so there is no limits in using any rotor / reflector in any place. There is also no limits in the number of plugboard connections (which was 10).

Second part is the breaking of Enigma using the method invented by Alan Turing and his team at Bletchley Park. Given the encoded text, a word known to be in the encoded text (crib) and a partially known Enigma configuration the script will try out the all possible Enigma settings and present potential solutions to the user.

#### Supported rotors
* Beta:     LEYJVCNIXWPBQMDRTAKZGFUHOS
* Gamma:    FSOKANUERHMBTIYCWLQPZXVGJD
* I:        EKMFLGDQVZNTOWYHXUSPAIBRCJQ
* II:       AJDKSIRUXBLHWTMCQGZNPYFVOEE
* III:      BDFHJLCPRTXVZNYEIWGAKMUSQOV
* IV:       ESOVPZJAYQUIRHXLNFTGKDCMWBJ
* V:        VZBRGITYUPSDNHLXAWMJQOFECKZ

#### Supported reflectors
* A:       EJMZALYXVBWFCRQUONTSPIKHGD
* B:       YRUHQSLDPXNGOKMIEBFZCWVJAT
* C:       FVPJIAOYEDRZXWGCTKUQSBNMHL
* B_thin:  ENKQAUYWJICOPBLMDXZVFTHRGS
* C_thin:  RDOBJNTKVEHMLFCWZAXGYIPSUQ

#### Running the code
Following are a few examples of how to run the code to encrypt / decrypt text using the enigma-simulator as well as some code breaking examples.

#### Enigma configuration
Enigma configuration can be written for both 3 or 4 rotor Enigma in a single string. An input string like: 
* B_thin Beta-I-II-III 4-24-17-7 V-E-Q-F AT-LU-NR-IG
will be interpreted as:
* Rotors from right to left: III, II, I, Beta
* Reflecter: B_thin
* Rotor positions right to left: F, Q, E, V (V being the position of the left-most rotor)
* Ring setting right to left: 7, 17, 24, 4 (4 being the ring setting of the left-most rotor)
* Plugboard settings (optional): AT, LU, NR, IG

#### Encrypting text
```python
enigma_config = EnigmaConfig.from_config_string("C III-II-I-V 4-24-17-7 V-E-Q-F AQ-WS-ED-RF")
enigma_machine = Enigma(enigma_config)
plain_text = "HALLOWELT"
encoded_text = enigma_machine.encode_string(plain_text)
print(encoded_text)
# prints PRTWRVUZW
```

#### Decrypting text
```python
from enigma import Enigma, EnigmaConfig

enigma_config = EnigmaConfig.from_config_string("C III-II-I-V 4-24-17-7 V-E-Q-F AQ-WS-ED-RF")
enigma_machine = Enigma(enigma_config)
plain_text = "PRTWRVUZW"
encoded_text = enigma_machine.encode_string(plain_text)
print(encoded_text)
# prints HALLOWELT
```

#### Breaking the Enigma code
An example of breaking Enigma code when the configuration is partially known. The script will attempt to find an Enigma configuration that is able to decrypt the crib. Multiple solutions are possible and in human input is required to chose the correct one. An example of such a partially known Enigma configuration:
* B Beta-I-III 23-2-10 ?-?-? VH-PT-ZG-BJ-EY-FS
meaning that everything is known apart from the initial rotor positions. 

```python
import code_breaking

encrypted_text = "ZQHRLTGWAZSPMTRESAIOAIBKVQLGFP"
crib = "UNIVERSITY"
enigma_config = "B Beta-I-III 23-2-10 ?-?-? VH-PT-ZG-BJ-EY-FS"

solutions = code_breaking.decrypt_cipher(encrypted_text, crib, enigma_config)
# solution is a list with a single tuple: [('B Beta-I-III 23-2-10 I-M-G VH-PT-ZG-BJ-EY-FS', 'ENIGMAMACHINESARESOLDATAUCTION')]
```
A more complicated example of partially known Enigma settings:
* C III-?-["II","I"]-V [4,5,6]-24-?-7 ABGZ-?-Q-F AQ-?S-ED-["ZU","ZF","ZK"]
Interpreted as:
* Reflector is C.
* Rotors:
  * 1 is V
  * rotor 2 is either I or II
  * rotor 3 is unknown and can be any supported rotor
  * rotor 4 is III
* Ring settings:
  * first rotor = 7 
  * second rotor unknown (all 26 possible)
  * third rotor = 24
  * fourth rotor is on of [4, 5 or 6]
* Rotor positions:
  * first rotor = F
  * second rotor = Q
  * third is unknown and can be any position
  * fourth rotor position is one of [A, B, G or Z]
* Plugs:
  * AQ
  * ED
  * ?S one lead connects to S, but the other end is not known
  * ["ZU","ZF","ZK"] last lead is one of [ZU,ZF or ZK]
  
 
```python
import code_breaking

encrypted_text = "ABSKJAKKMRITTNYURBJFWQGRSGNNYJSDRYLAPQWIAGKJYEPCTAGDCTHLCDRZRFZHKNRSDLNPFPEBVESHPY"
crib = "THOUSANDS"
enigma_config = "? ["II","IV","Beta","Gamma"]-["II","IV","Beta","Gamma"]-["II","IV","Beta","Gamma"] [2,4,6,8,20,22,24,26]-[2,4,6,8,20,22,24,26]-[2,4,6,8,20,22,24,26] E-M-Y FH-TS-BE-UQ-KD-AL"

solutions = code_breaking.decrypt_cipher(encrypted_text, crib, enigma_config)
# solution is a list with a single tuple: [('C II-Gamma-IV 24-8-20 E-M-Y FH-TS-BE-UQ-KD-AL', 
#                                            'SQUIRRELSPLANTTHOUSANDSOFNEWTREESEACHYEARBYMERELYFORGETTINGWHERETHEYPUTTHEIRACORNS')]
```

[1]: https://en.wikipedia.org/wiki/Enigma_machine
