class PlugLead:
    """PlugLead represents a connection between two plugs on the plugboard (Steckerbrett)."""

    def __init__(self, mapping):
        self.mapping = tuple(mapping)
        if self.plug1() == self.plug2():
            raise ValueError("Plug cannot connect to itself.")

    def encode(self, character):
        """ Substitute an input character

        If A is connected to E then the substitution can go both ways,
        e.g. the letter E will be substituted with A and the letter A
        will be substituted with E

        :param character: A character to be substituted
        :return: the substitute for the input character
        """
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

    def __str__(self):
        return "{0}{1}".format(self.mapping[0],self.mapping[1])


class Plugboard:
    """Plugboard represents the Enigma plugboard (Steckerbrett).

        A plugboard substitutes characters before and after rotor scrambling.
        Substitution happens only when the plugs are connected, If plug A is
        not connected then it will remain A. If A is connected to E then the
        substitution can go both ways, e.g. the letter E will be substituted with
        A and the letter A will be substituted with E
        """
    def __init__(self):
        self.leads = dict()  # keys will serve for verifying that a plug only connects once

    def add(self, lead):
        """Add a new connection between two plugs"""

        if lead.plug1() not in self.leads and lead.plug2() not in self.leads:
            # Substitution can go both ways, dict is used for fast lookup
            self.leads[lead.plug1()] = lead
            self.leads[lead.plug2()] = lead
        else:
            raise ValueError("Once of the plugs {0}-{1} is already connected".format(lead.plug1(), lead.plug2()))

    def encode(self, character):
        """ Substitute an input character if plug is connected

        Substitution happens only when the plugs are connected, If plug A is
        not connected then it will remain A. If A is connected to E then the
        substitution can go both ways, e.g. the letter E will be substituted with
        A and the letter A will be substituted with E

        :param character: A character to be substituted
        :return: the substitute for the input character
        """
        if character in self.leads:
            # plug is connected, substitute it
            return self.leads[character].encode(character)
        else:
            # plug is not connected, return the original character
            return character

    def __str__(self):
        return str(set("{0}".format(" ".join(str(self.leads[l]) for l in self.leads)).split()))


class Rotor:
    supported_rotors = {
        'Alphabet': "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        'Beta': "LEYJVCNIXWPBQMDRTAKZGFUHOS",
        'Gamma': "FSOKANUERHMBTIYCWLQPZXVGJD",
        'I': "EKMFLGDQVZNTOWYHXUSPAIBRCJQ",
        'II': "AJDKSIRUXBLHWTMCQGZNPYFVOEE",
        'III': "BDFHJLCPRTXVZNYEIWGAKMUSQOV",
        'IV': "ESOVPZJAYQUIRHXLNFTGKDCMWBJ",
        'V': "VZBRGITYUPSDNHLXAWMJQOFECKZ",
        'A': "EJMZALYXVBWFCRQUONTSPIKHGD",
        'B': "YRUHQSLDPXNGOKMIEBFZCWVJAT",
        'C': "FVPJIAOYEDRZXWGCTKUQSBNMHL",
        'B_thin': "ENKQAUYWJICOPBLMDXZVFTHRGS",
        'C_thin': "RDOBJNTKVEHMLFCWZAXGYIPSUQ"
    }

    def __init__(self, label, r_left=None, r_right=None, pos=0, ring=0):
        """Inititalize an Enigma rotor or reflector

        :param label:   Rotor name (must be one of supported rotors, e.g. IV)
        :param r_left:  Rotor on the left side
        :param r_right: Rotor on the right side
        :param pos:     Initial position of the rotor (e.g. Z)
        :param ring:    Ring setting of the rotor (e.g. 02)
        """
        if label in Rotor.supported_rotors:
            # beware that ring setting does not change the notch
            self.position = pos - ring
            self.ring_setting = ring
            self.label = label
            self.left_rotor = r_left
            self.right_rotor = r_right
            # Pins that face the rotor on the left:
            self.right_pins = Rotor.supported_rotors['Alphabet']
            # Pins that face the rotor on the right:
            self.left_pins = Rotor.supported_rotors[label][:26]
            # if notch is defined, it is 27th character in the list:
            if len(Rotor.supported_rotors[label]) > 26:
                self.notch = Rotor.supported_rotors[label][26]
                if self.ring_setting > 0:
                    # since ring setting was subtracted from position it
                    # also has to be subtracted from the notch setting
                    # (since ring setting does NOT affect the notch)
                    inx = self.right_pins.index(self.notch) - ring
                    self.notch = self.right_pins[inx]
            else:
                self.notch = None
        else:
            raise ValueError("Rotor {} not supported".format(label))

    def encode_right_to_left(self, character):
        """Pass a character to the right through the rotor

        :param character:   Input character to be encoded. It is the character as
        it leaves the rotor to the right so an offset is possible
        :return:            Encoded character (pin) on the left
        """

        # rotor position is already adjusted for the ring setting
        offset = self.position
        # if the rotor on the right has moved, then pins should be aligned
        if self.right_rotor is not None:
            offset -= self.right_rotor.get_position()
        input_pin = (self.right_pins.index(character) + offset) % 26
        return self.left_pins[input_pin]

    def encode_left_to_right(self, character):
        """Pass a character to the left through the rotor

        :param character:   Input character to be encoded. It is the character as
        it leaves the rotor to the left so an offset is possible
        :return:            Encoded character (pin) on the left
        """

        # rotor position is already adjusted for the ring setting
        offset = self.position
        # if the rotor on the right has moved, then pins should be aligned
        if self.left_rotor is not None:
            offset -= self.left_rotor.get_position()
        input_pin = (self.right_pins.index(character) + offset) % 26
        pin_index = self.left_pins.index(self.right_pins[input_pin])
        return self.right_pins[pin_index]

    def rotate(self):
        """Rotate the Enigma rotor one step

        :return: A boolean whether rotor to the left should also rotate
        """

        # if rotor is in notch position before rotation, then rotor to the left
        # should also be rotated in the current cycle:
        rotate_left = self.right_pins[self.position] == self.notch
        self.position += 1
        self.position %= 26
        return rotate_left

    def is_rotor_reflector(self):
        return self.left_rotor is None

    def set_left_rotor(self, left_rotor):
        """Set rotor to the left of this rotor"""

        self.left_rotor = left_rotor

    def set_right_rotor(self, right_rotor):
        """Set rotor to the right of this rotor"""

        self.right_rotor = right_rotor

    def get_position(self):
        return self.position % 26

    def get_ring_setting(self):
        return self.ring_setting

    def is_notch_position(self):
        return self.right_pins[self.position] == self.notch

    def __str__(self):
        return self.label

class EnigmaConfig:
    """Represents reflector, rotor and plugboard settings of Enigma machine"""

    def __init__(self, reflector, rotors,  rotor_positions, ring_settings, plugs):
        self.reflector = reflector
        self.rotors = rotors
        self.rotors_pos = rotor_positions
        self.ring_settings = ring_settings
        self.plugs = plugs

    @classmethod
    def from_config_string(cls, config_string):
        """Instantiate Enigma config from a short config string

        An input string like "B_thin Beta-I-II-III 13-13-13-13 A-A-A-A AT-LU-NR-IG"
        is interpreted as:
            - Rotors from right to left: III, II, I, Beta
            - Reflecter: B_thin
            - Rotor positions right to left: A, A, A, A
            - Ring setting right to left: 13, 13, 13, 13
            - Plugboard settings (optional): AT, LU, NR, IG
        All parameters apart from the plugboard settings are optional.

        :param config_string: An input config string
        :return: An instance of Enigma config
        """

        config_parts = config_string.split()
        # get the name of the reflector
        config_reflector = config_parts[0]
        # get the list of the plugboard connection pairs if any defined
        if len(config_parts) > 4:
            config_plugboard = config_parts[4].replace('-', ' ').split()
        else:
            config_plugboard = []
        # get the rotor names, positions and ring settings in reverse order
        # so that the first rotor in the list is the right-most rotor in Enigma
        config_rotors = []
        config_positions = []
        config_ring_settings = []
        for rotor_label, ring_setting, rotor_position in zip(config_parts[1].split('-')[::-1],
                                                             config_parts[2].split('-')[::-1],
                                                             config_parts[3].split('-')[::-1]):
            config_rotors.append(rotor_label)
            config_positions.append(rotor_position)
            config_ring_settings.append(int(ring_setting))
        return cls(config_reflector, config_rotors, config_positions, config_ring_settings,  config_plugboard)

    def is_valid_configuration(self):
        """Enigma settings validation"""

        lead_chars = set()
        if self.plugs:
            # Verify that no plug on the plugboard is connected more than once:
            for lead in self.plugs:
                for c in list(lead):
                    if c in lead_chars:
                        return False
                    else:
                        lead_chars.add(c)
        return True

    def __str__(self):
        """Print out Enigma settings

        Enigma settings will be printed out in the following format:
        B_thin Beta-I-II-III 13-13-13-13 A-A-A-A AT-LU-NR-IG
        """

        return "{0} {1} {2} {3} {4}".format(self.reflector,
                             "-".join(r for r in self.rotors[::-1]),
                             "-".join(str(r) for (r) in self.ring_settings[::-1]),
                             "-".join(r for r in self.rotors_pos[::-1]),
                             "-".join(r for r in self.plugs))


class Enigma:
    """Represents a 3 or 4 rotor Enigma encryption device"""

    def __init__(self, cnf):
        """Instantiate 3 or 4 rotor steckered or unsteckered Enigma from config

        :param cnf: An instance of EnigmaConfig class that
        specifies reflector, rotor and plugboard settings
        """

        self.config = cnf
        # apply plugboard configuration
        self.plugboard = Plugboard()
        for lead_config in cnf.plugs:
            self.plugboard.add(PlugLead(lead_config))

        # static input ring that connects to the right-most rotor
        self.input_ring = Rotor.supported_rotors['Alphabet']

        # apply rotor configuration, right to left (3 or 4 rotors)
        # rotor is defined with its name, initial position and ring setting
        # it has to be one of the supported rotors I, II, III, IV, V, Beta, Gammma
        self.rotors = list()
        for r_lbl, r_pos, r_ring in zip(cnf.rotors, cnf.rotors_pos, cnf.ring_settings):
            self.rotors.append(Rotor(r_lbl,
                                     pos=self.input_ring.index(r_pos),
                                     # ring settings should be 0-25 instead of 1-26
                                     ring=r_ring - 1))
        # at the end add the reflector (just a rotor that doesn't rotate)
        self.rotors.append(Rotor(cnf.reflector))
        # for each of the rotors set its neighbours to the left and to the right
        for rotor_inx in range(len(self.rotors)):
            first = rotor_inx == 0
            last = rotor_inx == len(self.rotors) - 1
            if not last:
                self.rotors[rotor_inx].set_left_rotor(self.rotors[rotor_inx + 1])
            if not first:
                self.rotors[rotor_inx].set_right_rotor(self.rotors[rotor_inx - 1])

    def encode_string(self, plain_text):
        """Encode or decode a string using the current Enigma settings.

        Rotor position will not be reset when calling this function so if this
        function is called multiple times the rotor positions will continue
        they left off after the last encoding/decoding

        :param plain_text: input plain or encrypted string
        :return: decoded or encoded string
        """

        encoded_string = ""
        for c in plain_text:
            encoded_string += str(self.encode_character(c))
        return encoded_string

    def rotate_n_steps(self, n):
        """Position rotors forward n-steps

        In case that encoding/decoding happens at an offset then this can be used
        to adjust the rotor positions. It follows the same rules of rotor rotation
        as encoding a character.

        :param n: the number of steps to position rotors forward
        :return:
        """

        # rotate all the rotors from right to left
        # the second rotor (index=1) does the double step
        # only first three rotors can rotate (4th cannot)
        for i in range(n):
            rotate_left_rotor = self.rotors[0].rotate()
            if rotate_left_rotor or self.rotors[1].is_notch_position():
                rotate_left_rotor = self.rotors[1].rotate()
                if rotate_left_rotor:
                    self.rotors[2].rotate()

    def reset_rotors(self):
        """Set rotor positions back to initial position"""
        for r,p in zip(self.rotors[:-1],self.config.rotors_pos):
            r.position = self.input_ring.index(p)

    def encode_character(self, character):
        """Encode or decode a character using the current Enigma settings.

        Rotor position will not be reset when calling this function so if this
        function is called multiple times the rotor positions will continue
        they left off after the last encoding/decoding

        :param character: input character
        :return: decoded or encoded character
        """

        # swap character if lead connected in the plugboard
        character = self.plugboard.encode(character)

        # rotate all the rotors from right to left
        # the second rotor (index=1) does the double step
        # only first three rotors can rotate (4th cannot)
        self.rotate_n_steps(1)

        # pass the character from right to left and through the reflector
        for rotor in self.rotors:
            character = rotor.encode_right_to_left(character)

        # pass the character back from left to right (skip reflector)
        for rotor in reversed(self.rotors[0:-1]):
            character = rotor.encode_left_to_right(character)

        # calculate offset between right-most rotor and the static alphabet ring
        inx = self.input_ring.index(character)
        first_rotor_offset = (self.rotors[0].get_position()) % 26
        character = self.input_ring[(inx - first_rotor_offset) % 26]

        # swap character the second time if lead connected in the plugboard
        character = self.plugboard.encode(character)
        return character

    def __str__(self):
        return str(self.config)

    def print_state(self):
        return "{0} {1} {2} {3} {4}".format(self.rotors[-1],
                                            "-".join(str(r) for r in self.rotors[-2::-1]),
                                            "-".join(str(r.ring_setting+1) for (r) in self.rotors[-2::-1]),
                                            "-".join(str(self.input_ring[r.position + r.ring_setting]) for r in self.rotors[-2::-1]),
                                            self.plugboard)
