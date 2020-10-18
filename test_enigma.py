import pytest
from enigma import *

def test_plugboard():
    plugboard = Plugboard()
    plugboard.add(PlugLead("SZ"))
    plugboard.add(PlugLead("GT"))
    plugboard.add(PlugLead("DV"))
    plugboard.add(PlugLead("KU"))
    # each plug can only be connected once:
    with pytest.raises(ValueError):
        plugboard.add(PlugLead("KD"))
    # a plug cannot be connected to itself:
    with pytest.raises(ValueError):
        plugboard.add(PlugLead("KK"))
    # a plug should work in both directions:
    assert (plugboard.encode("K") == "U")
    assert (plugboard.encode("U") == "K")
    # if a plug is not connected it is not encoded:
    assert (plugboard.encode("A") == "A")

def test_enigma():

    assert (Enigma(EnigmaConfig("B", ["III","II","I"], ['Z','A','A'], [1,1,1], []))
            .encode_character('A') == 'U')

    assert (Enigma(EnigmaConfig.from_config_string("B I-II-III 1-1-1 A-A-Z"))
            .encode_character('A') == 'U')

    assert (Enigma(EnigmaConfig.from_config_string("B I-II-III 1-1-1 A-A-A"))
            .encode_character('A') == 'B')

    assert (Enigma(EnigmaConfig.from_config_string("B I-II-III 1-1-1 Q-E-V"))
            .encode_character('A') == 'L')

    assert (Enigma(EnigmaConfig.from_config_string("B I-II-III 1-1-1 A-A-Z HL-MO-AJ-CX-BZ-SR-NI-YW-DG-PK"))
            .encode_string('HELLOWORLD') == 'RFKTMBXVVW')

    assert (Enigma(EnigmaConfig.from_config_string("B IV-V-Beta 14-9-24 A-A-A"))
            .encode_character('H') == 'Y')

    assert (Enigma(EnigmaConfig.from_config_string("C I-II-III-IV 7-11-15-19 Q-E-V-Z"))
            .encode_character('Z') == 'V')

    assert (Enigma(EnigmaConfig.from_config_string("A IV-V-Beta-I 18-24-3-5 E-Z-G-P PC-XZ-FM-QA-ST-NB-HY-OR-EV-IU"))
            .encode_string('BUPXWJCDPFASXBDHLBBIBSRNWCSZXQOLBNXYAXVHOGCUUIBCVMPUZYUUKHI') == 'CONGRATULATIONSONPRODUCINGYOURWORKINGENIGMAMACHINESIMULATOR')

    # 1. longer test
    plain_text = "ACOMPUTERWOULDDESERVETOBECALLEDINTELLIGENTIFITCOULDDECEIVEAHUMANINTOBELIEVINGTHATITWASHUMANSOMETIMESITSTHEVERYPEOPLEWHONOONEIMAGINESANYTHINGOFWHODOTHETHINGSNOONECANIMAGINESOMETIMESITISTHEPEOPLENOONECANIMAGINEANYTHINGOFWHODOTHETHINGSNOONECANIMAGINETHOSEWHOCANIMAGINEANYTHINGCANCREATETHEIMPOSSIBLEALANTURING"
    encrypted = "BSQBJJCYBTXBALYACFQRCGZKQOBGDGRFWQLUWFKGZKOEHXEMLTSNDSVQTLUGXAGXQQEZHFCYCUWFBJPYGQVAUZNLPZXXAJUMHDCBWLDJPXEGDQKYZXWTMJALIQAUUOMELDDCCULBODHJXIMJAWIMIUYRWFBUGTQUSMURWAGCQQTIITSXUOFULJYCGSSHFJCUHXYWZASNAYLXQARMBFFLNFWHZELWYLAKBFZZUEQURCZFVZKVGPFJDXUABZCFMZDDMFLEBLNUSWWEDZDXKPOLSPSNYNHMQKXZQHEFRVLMWZXAFGOAP"
    emachine = Enigma(EnigmaConfig.from_config_string("A III-II-I-Gamma 4-24-17-7 V-E-Q-J AT-LU-NR-IG"))
    assert (encrypted == emachine.encode_string(plain_text))

    # 2. longer test
    encrypted = "YTJEGCNXFCUWRCMSXSQFAMPYZHRNMXFTFCYCYFJYZALLAHGGZKIZDKWYAOVLOQMTDKRNEOHKWDWYLSGIGOMIVDNTVNIDUWTXTBJRKZFDMOXLXNHXHVIFJTYHBCSFLWFPVVAZVKLJOHTNUKGQXPYJUJSLNHDISIPDWEQMNBMDDQBTSTDXCLQFYFXJQWOBALEVRANRPKHHKLBMUOUBKFQXRFUNXLUOWOWMTQKCXTJTGJBBIYCZRYJAMOGFCIOJUWQJKAZNCOMYODLHYDCANPIKUCDCWJJYBZLOKUVNDWTLYYCCEGLQL"
    emachine = Enigma(EnigmaConfig.from_config_string("A III-II-I-IV 4-24-17-7 V-E-Q-J AT-LU-NR-IG"))
    assert (encrypted == emachine.encode_string(plain_text))

    # 3. longer test
    emachine = Enigma(EnigmaConfig.from_config_string("C III-II-I-V 4-24-17-7 V-E-Q-F AQ-WS-ED-RF"))
    plain_text = "IMAGINATIONISMOREIMPORTANTTHANKNOWLEDGEFORKNOWLEDGEISLIMITEDWHEREASIMAGINATIONEMBRACESTHEENTIREWORLDSTIMULATINGPROGRESSGIVINGBIRTHTOEVOLUTION"
    encrypted = "FBJCCQLHETUUEBIMUPZWCJCSKLNUTEIADVNSKEGEZLCKPEUKWTCSTAEBPZIUBGDOGFZGDGAQYBGSPBYDMTRSUCFRMSCVGTJEXMNBQLMNTDBWDYDRPCSPJUKZZEFOLRVQKYDQMWSTLYQVZ"
    assert (encrypted == emachine.encode_string(plain_text))

    # 4. test on a file of 10000 characters:
    emachine = Enigma(EnigmaConfig.from_config_string("B_thin Beta-I-II-III 13-13-13-13 A-A-A-A"))
    with open('test_files/long_plaintext.txt', 'r') as plain_text:
        with open("test_files/enc B_thin Beta-I-II-III 13-13-13-13 A-A-A-A.txt", "r") as encrypted:
            for line_plain, line_encrypted in zip(plain_text, encrypted):
                test_encrypted = emachine.encode_string(line_plain[:-1].upper())
                assert (line_encrypted[:-1] == test_encrypted)


