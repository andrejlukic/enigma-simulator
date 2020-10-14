import pytest


class PlugLead:
    def __init__(self, mapping):
        self.mapping = tuple(mapping)
        if self.plug1() == self.plug2():
            raise ValueError("Plug cannot connect to itself.")

    def encode(self, character):
        # e.g. AZ connects A with Z and works both directions
        if self.plug1() == character:
            return self.plug2()
        elif self.plug2() == character:
            return self.plug1()
        else:
            return character

    def plug1(self):
        return self.mapping[0]

    def plug2(self):
        return self.mapping[1]


class Plugboard:
    def __init__(self):
        self.leads = dict()  # keys will serve for verifying that a plug only connects once

    def add(self, lead):
        # a plug can be connected exactly once
        if lead.plug1() not in self.leads and lead.plug2() not in self.leads:
            self.leads[lead.plug1()] = lead
            self.leads[lead.plug2()] = lead
        else:
            raise ValueError("Once of the plugs {0}-{1} is already connected".format(lead.plug1(), lead.plug2()))

    def encode(self, character):
        # check if this plug is connected
        if character in self.leads:
            # return the mapped character
            print("Swap {0} with {1}".format(character, self.leads[character].encode(character)))
            return self.leads[character].encode(character)
        else:
            print("Plug {0} is not connected".format(character))
            # plug is not connected
            return character


class Rotor:
    supported_rotors = {
        'Alphabet': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
                     'U', 'V', 'W', 'X', 'Y', 'Z'],
        'Beta': ['L', 'E', 'Y', 'J', 'V', 'C', 'N', 'I', 'X', 'W', 'P', 'B', 'Q', 'M', 'D', 'R', 'T', 'A', 'K', 'Z',
                 'G',
                 'F', 'U', 'H', 'O', 'S'],
        'Gamma': ['F', 'S', 'O', 'K', 'A', 'N', 'U', 'E', 'R', 'H', 'M', 'B', 'T', 'I', 'Y', 'C', 'W', 'L', 'Q', 'P',
                  'Z',
                  'X', 'V', 'G', 'J', 'D'],
        'I': ['E', 'K', 'M', 'F', 'L', 'G', 'D', 'Q', 'V', 'Z', 'N', 'T', 'O', 'W', 'Y', 'H', 'X', 'U', 'S', 'P', 'A',
              'I',
              'B', 'R', 'C', 'J', 'Q'],
        'II': ['A', 'J', 'D', 'K', 'S', 'I', 'R', 'U', 'X', 'B', 'L', 'H', 'W', 'T', 'M', 'C', 'Q', 'G', 'Z', 'N', 'P',
               'Y', 'F', 'V', 'O', 'E', 'E'],
        'III': ['B', 'D', 'F', 'H', 'J', 'L', 'C', 'P', 'R', 'T', 'X', 'V', 'Z', 'N', 'Y', 'E', 'I', 'W', 'G', 'A', 'K',
                'M', 'U', 'S', 'Q', 'O', 'V'],
        'IV': ['E', 'S', 'O', 'V', 'P', 'Z', 'J', 'A', 'Y', 'Q', 'U', 'I', 'R', 'H', 'X', 'L', 'N', 'F', 'T', 'G', 'K',
               'D', 'C', 'M', 'W', 'B', 'J'],
        'V': ['V', 'Z', 'B', 'R', 'G', 'I', 'T', 'Y', 'U', 'P', 'S', 'D', 'N', 'H', 'L', 'X', 'A', 'W', 'M', 'J', 'Q',
              'O',
              'F', 'E', 'C', 'K', 'Z'],
        'A': ['E', 'J', 'M', 'Z', 'A', 'L', 'Y', 'X', 'V', 'B', 'W', 'F', 'C', 'R', 'Q', 'U', 'O', 'N', 'T', 'S', 'P',
              'I',
              'K', 'H', 'G', 'D'],
        'B': ['Y', 'R', 'U', 'H', 'Q', 'S', 'L', 'D', 'P', 'X', 'N', 'G', 'O', 'K', 'M', 'I', 'E', 'B', 'F', 'Z', 'C',
              'W',
              'V', 'J', 'A', 'T'],
        'C': ['F', 'V', 'P', 'J', 'I', 'A', 'O', 'Y', 'E', 'D', 'R', 'Z', 'X', 'W', 'G', 'C', 'T', 'K', 'U', 'Q', 'S',
              'B',
              'N', 'M', 'H', 'L']
    }

    def __init__(self, rotor_label, left_rotor=None, right_rotor=None, init_position=0, ring_setting=0):
        if rotor_label in Rotor.supported_rotors:
            self.position = init_position - ring_setting
            self.ring_setting = ring_setting
            self.label = rotor_label
            self.left_rotor = left_rotor
            self.right_rotor = right_rotor
            self.right_pins = Rotor.supported_rotors['Alphabet']
            self.left_pins = Rotor.supported_rotors[rotor_label][:26]
            # notch is 27th character in the list:
            if len(Rotor.supported_rotors[rotor_label]) > 26:
                self.notch = Rotor.supported_rotors[rotor_label][26]
                if self.ring_setting > 0:
                    inx = self.right_pins.index(self.notch) - ring_setting
                    self.notch = self.right_pins[inx]
            else:
                self.notch = None
        else:
            raise ValueError("Rotor {} not supported".format(rotor_label))

    def encode_right_to_left(self, character):
        # character = pin of the previous rotor / input pin
        # 1 - determine what pin this translates to on current rotor
        # 2 - translate to the output pin

        #offset = self.position - self.ring_setting
        offset = self.position
        if self.right_rotor is not None:
            offset -= self.right_rotor.get_position()
        input_pin = (self.right_pins.index(character) + offset) % 26
        print("{2}:\t\t{1} <= {0} ({3},{4})".format(self.right_pins[input_pin],
                                                    self.left_pins[input_pin],
                                                    self.label,
                                                    character,
                                                    offset))
        return self.left_pins[input_pin]

    def encode_left_to_right(self, character):
        # character = pin of the previous rotor / input pin
        # 1 - determine what pin this translates to on current rotor
        # 2 - translate to the output pin
        #offset = self.position - self.ring_setting
        offset = self.position
        if self.left_rotor is not None:
            offset -= self.left_rotor.get_position()
        input_pin = (self.right_pins.index(character) + offset) % 26
        pin_index = self.left_pins.index(self.right_pins[input_pin])
        print("{2}:\t\t{0} => {1} ({3})".format(self.left_pins[pin_index],
                                                self.right_pins[pin_index],
                                                self.label, character))
        return self.right_pins[pin_index]

    def rotate(self):
        rotate_left = self.right_pins[self.position] == self.notch
        self.position += 1
        self.position %= 26
        print("Rotated\t{0} to {1}. Rotate rotor to the left: {2}".format(self.label, self.position, rotate_left))
        return rotate_left

    def is_rotor_reflector(self):
        return self.left_rotor is None

    def set_left_rotor(self, left_rotor):
        self.left_rotor = left_rotor

    def set_right_rotor(self, right_rotor):
        self.right_rotor = right_rotor

    def get_position(self):
        return self.position % 26

    def get_ring_setting(self):
        return self.ring_setting

    def is_notch_position(self):
        return self.right_pins[self.position] == self.notch


class Enigma:
    def __init__(self, rotor_config, plug_config=""):
        # apply plugboard configuration
        self.plugboard = Plugboard()
        for lead_config in plug_config.split():
            self.plugboard.add(PlugLead(lead_config))

        # this is the static input ring that connects to the first rotor
        self.input_ring = Rotor.supported_rotors['Alphabet']
        # apply rotor configuration, right to left
        self.rotors = list()
        for rotor_label in rotor_config:
            self.rotors.append(Rotor(rotor_label,
                                     init_position=rotor_config[rotor_label][0],
                                     ring_setting=rotor_config[rotor_label][1]))
        for rotor_inx in range(len(self.rotors)):
            first = rotor_inx == 0
            last = rotor_inx == len(self.rotors) - 1
            if not last:
                self.rotors[rotor_inx].set_left_rotor(self.rotors[rotor_inx + 1])
            if not first:
                self.rotors[rotor_inx].set_right_rotor(self.rotors[rotor_inx - 1])

    def encode_string(self, plain_text):
        print("Encoding ", plain_text)
        encoded_string = ""
        for c in plain_text:
            encoded_string += str(self.encode_character(c))
        print("Encoded {0} as {1}".format(plain_text, encoded_string))
        return encoded_string

    def decode_string(self, encrypted_text):
        plain_string = self.encode_string(encrypted_text)
        print("Decoded {0} as {1}".format(encrypted_text, plain_string))
        return plain_string

    def encode_character(self, character):
        # swap character if lead connected
        character = self.plugboard.encode(character)
        # rotate the rotors from right to left
        # the second rotor (index=1) does the double step
        rotate_left_rotor = self.rotors[0].rotate()
        if rotate_left_rotor or self.rotors[1].is_notch_position():
            rotate_left_rotor = self.rotors[1].rotate()
            if rotate_left_rotor:
                self.rotors[2].rotate()
        # scramble character from right to left and back
        for rotor in self.rotors:
            character = rotor.encode_right_to_left(character)
        for rotor in reversed(self.rotors[0:-1]):
            character = rotor.encode_left_to_right(character)
        # calculate offset between right-most rotor and the alphabet ring
        inx = self.input_ring.index(character)
        print(self.rotors[0].get_position(), self.rotors[0].get_ring_setting())
        first_rotor_offset = (self.rotors[0].get_position()) % 26
        character = self.input_ring[(inx - first_rotor_offset) % 26]
        print("Encoded as", character)
        character = self.plugboard.encode(character)
        print("----")
        return character


if __name__ == "__main__":
    plugboard = Plugboard()

    plugboard.add(PlugLead("SZ"))
    plugboard.add(PlugLead("GT"))
    plugboard.add(PlugLead("DV"))
    plugboard.add(PlugLead("KU"))

    with pytest.raises(ValueError):
        plugboard.add(PlugLead("KD"))
    with pytest.raises(ValueError):
        plugboard.add(PlugLead("KK"))
    assert (plugboard.encode("K") == "U")
    assert (plugboard.encode("A") == "A")

    assert (Enigma({'III': (-1, 0),
                    'II': (0, 0),
                    'I': (0, 0),
                    'B': (0, 0)})
            .encode_character('A') == 'U')

    assert (Enigma({'III': (0, 0),
                    'II': (0, 0),
                    'I': (0, 0),
                    'B': (0, 0)})
            .encode_character('A') == 'B')

    assert (Enigma({'III': (21, 0),
                    'II': (4, 0),
                    'I': (16, 0),
                    'B': (0, 0)})
            .encode_character('A') == 'L')

    assert (Enigma({'III': (-1, 0),
                    'II': (0, 0),
                    'I': (0, 0),
                    'B': (0, 0)},
                   plug_config="HL MO AJ CX BZ SR NI YW DG PK")
            .encode_string('HELLOWORLD') == 'RFKTMBXVVW')

    assert (Enigma({'III': (-1, 0),
                    'II': (0, 0),
                    'I': (0, 0),
                    'B': (0, 0)},
                   plug_config="HL MO AJ CX BZ SR NI YW DG PK")
            .decode_string('RFKTMBXVVW') == 'HELLOWORLD')

    assert (Enigma({'Beta': (0, 23),
                    'V': (0, 8),
                    'IV': (0, 13),
                    'B': (0, 0)})
            .encode_character('H') == 'Y')

    assert (Enigma({'IV': (25, 18),
                    'III': (21, 14),
                    'II': (4, 10),
                    'I': (16, 6),
                    'C': (0, 0)})
            .encode_character('Z') == 'V')

    assert (Enigma({'I': (15, 4),
                    'Beta': (6, 2),
                    'V': (-1, 23),
                    'IV': (4, 17),
                    'A': (0, 0)},
                   plug_config="PC XZ FM QA ST NB HY OR EV IU")
            .decode_string('BUPXWJCDPFASXBDHLBBIBSRNWCSZXQOLBNXYAXVHOGCUUIBCVMPUZYUUKHI') == 'CONGRATULATIONSONPRODUCINGYOURWORKINGENIGMAMACHINESIMULATOR')
