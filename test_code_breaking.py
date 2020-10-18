import pytest
import code_breaking

def test_missing_information():
    encrypted_text = "ABSKJAKKMRITTNYURBJFWQGRSGNNYJSDRYLAPQWIAGKJYEPCTAGDCTHLCDRZRFZHKNRSDLNPFPEBVESHPY"
    cribs = "THOUSANDS,HUNDREDS"

    # enigma configuration is partially known:
    enigma_config = 'C III-?-["II","I"]-V [4,5,6]-24-?-7 ABGZ-?-Q-F AQ-?S-ED-["ZU","ZF","ZK"]'
    config_possibilities = code_breaking.all_enigma_settings_candidates(enigma_config)
    expected_possibilities={}
    expected_possibilities["reflectors"] = ["C"]
    expected_possibilities["rotors"] = [["V"], ["II","I"], ["I", "II", "III", "IV", "V", "Beta", "Gamma"], ["III"]]
    expected_possibilities["rotor_positions"] = ["F", "Q", "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "ABGZ"]
    expected_possibilities["ring_settings"] = [[7], [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26], [24], [4, 5, 6]]
    expected_possibilities["plugboard"] = [["AQ"], ["AS","BS","CS","DS","ES","FS","GS","HS","IS","JS","KS","LS","MS","NS","OS","PS","QS","RS","TS","US","VS","WS","XS","YS","ZS"], ["ED"], ["ZU","ZF","ZK"]]
    assert (config_possibilities == expected_possibilities)

    # nothing is known of the Enigma configuration:
    enigma_config = '? ?-?-? ?-?-? ?-?-?'
    config_possibilities = code_breaking.all_enigma_settings_candidates(enigma_config)
    expected_possibilities = {}
    #expected_possibilities["reflectors"] = ["A", "B", "C", "B_thin", "C_thin"]
    expected_possibilities["reflectors"] = ["A", "B", "C"]
    expected_possibilities["rotors"] = [["I", "II", "III", "IV", "V", "Beta", "Gamma"],
                                        ["I", "II", "III", "IV", "V", "Beta", "Gamma"],
                                        ["I", "II", "III", "IV", "V", "Beta", "Gamma"]]
    expected_possibilities["rotor_positions"] = ["ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                                                 "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                                                 "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]
    expected_possibilities["ring_settings"] = [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
                                                20, 21, 22, 23, 24, 25, 26],
                                               [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
                                                20, 21, 22, 23, 24, 25, 26],
                                               [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
                                                20, 21, 22, 23, 24, 25, 26]]
    expected_possibilities["plugboard"] = []
    assert (config_possibilities == expected_possibilities)

def test_code_breaking():

    assert(code_breaking.possible_crib_positions("DMEXBMKYCVPNQBEDHXVPZGKMTFFBJRPJTLHLCHOTKOYXGGHZ", "SECRETS")
           == [0, 2, 3, 4, 5, 7, 8, 9, 11, 12, 14, 15, 16, 17, 18, 20, 21, 22, 23, 24, 25, 28, 29, 30, 31, 32, 33, 35, 36, 37, 38, 39, 40, 41])

    assert (code_breaking.possible_crib_positions("DMEXBMKYCVPNQBEDHXVPZGKMTFFBJRPJTLHLCHOTKOYXGGHZ", "SECRETS")
            == [0, 2, 3, 4, 5, 7, 8, 9, 11, 12, 14, 15, 16, 17, 18, 20, 21, 22, 23, 24, 25, 28, 29, 30, 31, 32, 33, 35,
                36, 37, 38, 39, 40, 41])

    assert (code_breaking.permutate_reflector_by_wire_swap("DCBAHEGF", 2).sort()
            == ['BADCEHGFIJ', 'BADCFGHEIJ', 'DGBAHECFIJ', 'FDHEBAGCIJ', 'ECBHGAFDIJ', 'EHAFCDGBIJ', 'GCBAHEDFIJ',
                'DFHABGECIJ', 'HGBFADCEIJ', 'FCBEGAHDIJ', 'DGFABCHEIJ', 'FHDECAGBIJ', 'GHFACEDBIJ', 'FCBEHADGIJ',
                'BADCGEHFIJ', 'DFHACBEGIJ', 'HDFEBCGAIJ', 'GFHACBDEIJ', 'DCBGEHAFIJ', 'ECBFHDAGIJ', 'CDABHEFGIJ',
                'FGBHDACEIJ', 'HFDECBGAIJ', 'EFAHCBGDIJ', 'ECBHFGADIJ', 'BADCHEGFIJ', 'DHFABCEGIJ', 'HCBEGDFAIJ',
                'DFGACBHEIJ', 'CDABGEHFIJ', 'HGBFDECAIJ', 'BADCHEFGIJ', 'EAHFBDGCIJ', 'FGBHAECDIJ', 'CDABHEGFIJ',
                'CDABFGHEIJ', 'GFHABEDCIJ', 'DCBGHEAFIJ', 'EAFHBCGDIJ', 'HCBEFGDAIJ', 'GCBAEHDFIJ', 'DHFACGEBIJ',
                'ECBFGDHAIJ', 'CDABEHGFIJ', 'GHFABCDEIJ', 'DGBAEHCFIJ'].sort())

    assert(code_breaking.decrypt_cipher("DMEXBMKYCVPNQBEDHXVPZGKMTFFBJRPJTLHLCHOTKOYXGGHZ",
                   "SECRETS",
                   '? Beta-Gamma-V 4-2-14 M-J-M KI-XN-FL')
           == [('C Beta-Gamma-V 4-2-14 M-J-M KI-XN-FL',
                'NICEWORKYOUVEMANAGEDTODECODETHEFIRSTSECRETSTRING')])
    
    assert(code_breaking.decrypt_cipher("CMFSUPKNCBMUYEQVVDYKLRQZTPUFHSWWAKTUGXMPAMYAFITXIJKMH",
                   "UNIVERSITY",
                   'B Beta-I-III 23-2-10 ?-?-? VH-PT-ZG-BJ-EY-FS')
            == [('B Beta-I-III 23-2-10 I-M-G VH-PT-ZG-BJ-EY-FS',
                 'IHOPEYOUAREENJOYINGTHEUNIVERSITYOFBATHEXPERIENCESOFAR')])

    assert(code_breaking.decrypt_cipher("BUPXWJCDPFASXBDHLBBIBSRNWCSZXQOLBNXYAXVHOGCUUIBCVMPUZYUUKHI",
                   "CONGRATULATIONS",
                   'A IV-V-Beta-I 18-24-3-5 E-Z-G-P PC-XZ-FM-QA-ST-NB-HY-OR-EV-IU')
           == [('A IV-V-Beta-I 18-24-3-5 E-Z-G-P PC-XZ-FM-QA-ST-NB-HY-OR-EV-IU', 'CONGRATULATIONSONPRODUCINGYOURWORKINGENIGMAMACHINESIMULATOR')])

    assert(code_breaking.decrypt_cipher("ABSKJAKKMRITTNYURBJFWQGRSGNNYJSDRYLAPQWIAGKJYEPCTAGDCTHLCDRZRFZHKNRSDLNPFPEBVESHPY",
                                        "THOUSANDS",
                                        '? ["II","IV","Beta","Gamma"]-["II","IV","Beta","Gamma"]-["II","IV","Beta","Gamma"] [2,4,6,8,20,22,24,26]-[2,4,6,8,20,22,24,26]-[2,4,6,8,20,22,24,26] E-M-Y FH-TS-BE-UQ-KD-AL')
           == [('C II-Gamma-IV 24-8-20 E-M-Y FH-TS-BE-UQ-KD-AL', 'SQUIRRELSPLANTTHOUSANDSOFNEWTREESEACHYEARBYMERELYFORGETTINGWHERETHEYPUTTHEIRACORNS')])

    assert (('A V-III-IV 24-12-10 S-W-U WP-RJ-TA-VF-KI-HN-CG-BS', 'NOTUTORSWEREHARMEDNORIMPLICATEDOFCRIMESDURINGTHEMAKINGOFTHESEEXAMPLES')
            in code_breaking.decrypt_cipher("SDNTVTPHRBNWTLMZTQKZGADDQYPFNHBPNHCQGBGMZPZLUAVGDQVYRBFYYEIXQWVTHXGNW",
                                 "TUTOR",
                                 "A V-III-IV 24-12-10 S-W-U WP-RJ-A?-VF-I?-HN-CG-BS"))

    assert (code_breaking.decrypt_cipher_reflector_scrambled("HWREISXLGTTBYVXRCWWJAKZDTVZWKBDJPVQYNEQIOTIFX",
                                                             "INSTAGRAM",
                                                             "? V-II-IV 6-18-7 A-J-L UG-IE-PO-NX-WT")
            == [('B V-II-IV 6-18-7 A-J-L UG-IE-PO-NX-WT', 'PQUHRSLDYXNGOKMABEFZCWVJIT', 'YOUCANFOLLOWMYDOGONINSTAGRAMATTALESOFHOFFMANN')])