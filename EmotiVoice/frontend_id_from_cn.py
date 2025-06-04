# Copyright 2023, YOUDAO
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
from frontend_cn import g2p_cn, re_digits, tn_chinese
from frontend_en import ROOT_DIR, read_lexicon, G2p, get_eng_phoneme
from g2p_id import G2p as IndonesianG2p


# Thanks to GuGCoCo and PatroxGaurab for identifying the issue: 
# the results differ between frontend.py and frontend_en.py. Here's a quick fix.
#re_english_word = re.compile('([a-z\-\.\'\s,;\:\!\?]+|\d+[\d\.]*)', re.I)
re_english_word = re.compile('([^\u4e00-\u9fa5]+|[ \u3002\uff0c\uff1f\uff01\uff1b\uff1a\u201c\u201d\u2018\u2019\u300a\u300b\u3008\u3009\u3010\u3011\u300e\u300f\u2014\u2026\u3001\uff08\uff09\u4e00-\u9fa5]+)', re.I)
def g2p_cn_en(text, g2p, lexicon):
    # Our policy dictates that if the text contains Chinese, digits are to be converted into Chinese.
    text=tn_chinese(text)
    parts = re_english_word.split(text)
    parts=list(filter(None, parts))
    tts_text = ["<sos/eos>"]
    chartype = ''
    text_contains_chinese = contains_chinese(text)
    for part in parts:
        if part == ' ' or part == '': continue
        if re_digits.match(part) and (text_contains_chinese or chartype == '') or contains_chinese(part):
            if chartype == 'en':
                tts_text.append('eng_cn_sp')
            phoneme = g2p_cn(part).split()[1:-1]
            chartype = 'cn'
        elif re_english_word.match(part):
            if chartype == 'cn':
                if "sp" in tts_text[-1]:
                    ""
                else:
                    tts_text.append('cn_eng_sp')
            phoneme = get_eng_phoneme(part, g2p, lexicon).split()
            if not phoneme :
                # tts_text.pop()
                continue
            else:
                chartype = 'en'
        else:
            continue
        tts_text.extend( phoneme )

    tts_text=" ".join(tts_text).split()
    if "sp" in tts_text[-1]:
        tts_text.pop()
    tts_text.append("<sos/eos>")

    return " ".join(tts_text)

def contains_chinese(text):
    pattern = re.compile(r'[\u4e00-\u9fa5]')
    match = re.search(pattern, text)
    return match is not None

# Mapping from Indonesian phonemes (IPA) to Chinese tokens
# Using the provided Chinese token set
INDONESIAN_TO_TOKEN_MAP = {
    # Vowels - mapping to Chinese tokens with tone variations
    'a': 'a1',        # Indonesian 'a' -> Chinese 'a1'
    'i': 'i1',        # Indonesian 'i' -> Chinese 'i1'
    'u': 'u1',        # Indonesian 'u' -> Chinese 'u1'
    'e': 'e1',        # Indonesian 'e' -> Chinese 'e1'
    'ə': 'e1',        # Indonesian schwa -> Chinese 'e1' (closest match)
    'o': 'o1',        # Indonesian 'o' -> Chinese 'o1'
    
    # Diphthongs and compound vowels
    'ai': 'ai1',      # Indonesian 'ai' -> Chinese 'ai1'
    'au': 'ao1',      # Indonesian 'au' -> Chinese 'ao1' (closest)
    'ei': 'ei1',      # Indonesian 'ei' -> Chinese 'ei1'
    'ou': 'ou1',      # Indonesian 'ou' -> Chinese 'ou1'
    'ia': 'ia1',      # Indonesian 'ia' -> Chinese 'ia1'
    'ie': 'ie1',      # Indonesian 'ie' -> Chinese 'ie1'
    'iu': 'iou1',     # Indonesian 'iu' -> Chinese 'iou1'
    'ua': 'ua1',      # Indonesian 'ua' -> Chinese 'ua1'
    'ue': 'ue2',      # Indonesian 'ue' -> Chinese 'ue2'
    'ui': 'uei1',     # Indonesian 'ui' -> Chinese 'uei1'
    'uo': 'uo1',      # Indonesian 'uo' -> Chinese 'uo1'
    
    # Consonants - mapping to Chinese consonants
    'b': 'b',
    'p': 'p',
    'd': 'd',
    't': '[T]',
    'g': 'g',
    'ɡ': 'g',
    'k': 'k',
    'f': 'f',
    'v': 'v1',        # Indonesian 'v' -> Chinese 'v1'
    's': 's',
    'z': 'z',
    'ʃ': 'sh',        # Indonesian 'sy' sound -> Chinese 'sh'
    'ʒ': 'zh',        # Voiced 'sh' sound -> Chinese 'zh'
    'tʃ': 'ch',       # Indonesian 'c' sound -> Chinese 'ch'
    'dʒ': 'zh',       # Indonesian 'j' sound -> Chinese 'zh' (closest)
    'h': 'h',
    'm': 'm',
    'n': 'n',
    'ŋ': '[NG]',        # Indonesian 'ng' sound -> Chinese 'ng' (using 'ng' as fallback)
    'l': 'l',
    'r': 'r',
    'w': 'u1',        # Indonesian 'w' -> Chinese 'u1' (semi-vowel)
    'j': 'i1',        # Indonesian 'y' sound -> Chinese 'i1' (semi-vowel)
    'x': 'h',         # Indonesian 'kh' -> Chinese 'h' (closest)
    'y': 'y',         # Indonesian 'y' consonant
    'c': 'c',         # Indonesian 'c' (if not tʃ)
    'q': 'q',         # Rare but possible
    
    # Nasal compounds
    'an': 'an1',      # Indonesian 'an' -> Chinese 'an1'
    'en': 'en1',      # Indonesian 'en' -> Chinese 'en1'
    'in': 'in1',      # Indonesian 'in' -> Chinese 'in1'
    'on': 'ong1',     # Indonesian 'on' -> Chinese 'ong1' (closest)
    'un': 'u1',       # Indonesian 'un' -> Chinese 'u1' (fallback)
    'ang': 'ang1',    # Indonesian 'ang' -> Chinese 'ang1'
    'eng': 'eng1',    # Indonesian 'eng' -> Chinese 'eng1'
    'ing': 'ing1',    # Indonesian 'ing' -> Chinese 'ing1'
    'ong': 'ong1',    # Indonesian 'ong' -> Chinese 'ong1'
    'ung': 'ong1',    # Indonesian 'ung' -> Chinese 'ong1' (closest)
    
    # Compound endings
    'er': 'er1',      # Indonesian 'er' -> Chinese 'er1'
    'ar': 'ar1',      # Indonesian 'ar' -> Chinese 'ar1'
    'ir': 'ir1',      # Indonesian 'ir' -> Chinese 'ir1'
    'or': 'or1',      # Indonesian 'or' -> Chinese 'or1'
    'ur': 'ur1',      # Indonesian 'ur' -> Chinese 'ur1'
    
    # Additional Chinese-specific combinations
    'ian': 'ian1',    # Indonesian 'ian' -> Chinese 'ian1'
    'iang': 'iang1',  # Indonesian 'iang' -> Chinese 'iang1'
    'iao': 'iao1',    # Indonesian 'iao' -> Chinese 'iao1'
    'uai': 'uai1',    # Indonesian 'uai' -> Chinese 'uai1'
    'uan': 'uan1',    # Indonesian 'uan' -> Chinese 'uan1'
    'uang': 'uang1',  # Indonesian 'uang' -> Chinese 'uang1'
    'uen': 'uen1',    # Indonesian 'uen' -> Chinese 'uen1'
    'ueng': 'ueng1',  # Indonesian 'ueng' -> Chinese 'ueng1'
    'iong': 'iong1',  # Indonesian 'iong' -> Chinese 'iong1'
    'van': 'van1',    # Indonesian 'van' -> Chinese 'van1'
    've': 've1',      # Indonesian 've' -> Chinese 've1'
    'vn': 'vn1',      # Indonesian 'vn' -> Chinese 'vn1'
    
    # Special Indonesian sounds
    'ɲ': 'n',         # Indonesian 'ny' -> Chinese 'n' (closest)
    'ʔ': 'sp1',       # Glottal stop -> silence token
    
    # Punctuation and special tokens
    '?': '?',
    '.': '.',
    '!': '!',
    ',': 'sp1',       # Comma -> silence token
    ';': 'sp1',       # Semicolon -> silence token
    ':': 'sp1',       # Colon -> silence token
    '-': 'sp1',       # Hyphen -> silence token
    ' ': 'sp1',       # Space -> silence token
}

# Valid Chinese tokens set for validation
VALID_CHINESE_TOKENS = {
    'a1', 'a2', 'a3', 'a4', 'a5', 'ai1', 'ai2', 'ai3', 'ai4', 'ai5',
    'air1', 'air2', 'air4', 'air5', 'an1', 'an2', 'an3', 'an4', 'an5',
    'ang1', 'ang2', 'ang3', 'ang4', 'ang5', 'angr1', 'angr2', 'angr4',
    'anr1', 'anr2', 'anr3', 'anr4', 'ao1', 'ao2', 'ao3', 'ao4', 'ao5',
    'aor1', 'aor2', 'aor3', 'aor4', 'ar1', 'ar2', 'ar3', 'ar4', 'ar5',
    'arr4', 'b', 'c', 'ch', 'cn_eng_sp', 'd', 'e1', 'e2', 'e3', 'e4', 'e5',
    'ei1', 'ei2', 'ei3', 'ei4', 'ei5', 'eir1', 'eir4', 'en1', 'en2', 'en3',
    'en4', 'en5', 'eng1', 'eng2', 'eng3', 'eng4', 'eng5', 'eng_cn_sp',
    'engr1', 'engr3', 'engr4', 'engsp1', 'engsp2', 'engsp4', 'enr1', 'enr2',
    'enr3', 'enr4', 'enr5', 'er1', 'er2', 'er3', 'er4', 'er5', 'f', 'g', 'h',
    'i1', 'i2', 'i3', 'i4', 'i5', 'ia1', 'ia2', 'ia3', 'ia4', 'ia5',
    'ian1', 'ian2', 'ian3', 'ian4', 'ian5', 'iang1', 'iang2', 'iang3',
    'iang4', 'iang5', 'iangr2', 'iangr4', 'ianr1', 'ianr2', 'ianr3',
    'ianr4', 'ianr5', 'iao1', 'iao2', 'iao3', 'iao4', 'iao5', 'iaor2',
    'iaor3', 'iaor4', 'iar2', 'iar3', 'iar4', 'ie1', 'ie2', 'ie3', 'ie4',
    'ie5', 'ier4', 'ii1', 'ii2', 'ii3', 'ii4', 'ii5', 'iii1', 'iii2',
    'iii3', 'iii4', 'iii5', 'iiir2', 'iiir3', 'iiir4', 'iir2', 'iir3',
    'iir4', 'in1', 'in2', 'in3', 'in4', 'in5', 'ing1', 'ing2', 'ing3',
    'ing4', 'ing5', 'ingr1', 'ingr2', 'ingr3', 'ingr4', 'inr1', 'inr4',
    'iong1', 'iong2', 'iong3', 'iong4', 'iong5', 'iou1', 'iou2', 'iou3',
    'iou4', 'iou5', 'iour2', 'iour3', 'iour4', 'ir1', 'ir2', 'ir3', 'ir4',
    'irr1', 'j', 'k', 'l', 'm', 'n', 'o1', 'o2', 'o3', 'o4', 'o5',
    'ong1', 'ong2', 'ong3', 'ong4', 'ong5', 'ongr2', 'ongr3', 'ongr4',
    'or4', 'ou1', 'ou2', 'ou3', 'ou4', 'ou5', 'our1', 'our2', 'our3',
    'our4', 'our5', 'p', 'q', 'r', 's', 'sh', 'sp0', 'sp1', 'sp2', 'sp3',
    'sp4', 't', 'u1', 'u2', 'u3', 'u4', 'u5', 'ua1', 'ua2', 'ua3', 'ua4',
    'ua5', 'uai1', 'uai2', 'uai3', 'uai4', 'uai5', 'uair4', 'uan1', 'uan2',
    'uan3', 'uan4', 'uan5', 'uang1', 'uang2', 'uang3', 'uang4', 'uang5',
    'uanr1', 'uanr2', 'uanr3', 'uanr4', 'uanr5', 'uar1', 'uar2', 'uar3',
    'uar4', 'uei1', 'uei2', 'uei3', 'uei4', 'uei5', 'ueir1', 'ueir2',
    'ueir3', 'ueir4', 'uen1', 'uen2', 'uen3', 'uen4', 'uen5', 'ueng1',
    'ueng3', 'ueng4', 'uenr1', 'uenr2', 'uenr3', 'uenr4', 'uo1', 'uo2',
    'uo3', 'uo4', 'uo5', 'uor1', 'uor2', 'uor3', 'uor4', 'uor5', 'ur1',
    'ur2', 'ur3', 'ur4', 'ur5', 'v1', 'v2', 'v3', 'v4', 'v5', 'van1',
    'van2', 'van3', 'van4', 'van5', 'vanr1', 'vanr2', 'vanr3', 'vanr4',
    've1', 've2', 've3', 've4', 've5', 'ver2', 'vn1', 'vn2', 'vn3', 'vn4',
    'vn5', 'vr2', 'vr3', 'vr4', 'vr5', 'x', 'y', 'z', 'zh', 'engsp0',
    '?', '.', 'spn', 'ue2', '!', 'err1', '[LAUGH]', 'rr', 'ier2', 'or1',
    'ueng2', 'ir5', 'iar1', 'iour1'
}

def map_indonesian_phoneme(phoneme):
    """Map an Indonesian phoneme to available Chinese token"""
    # Clean the phoneme
    phoneme = phoneme.strip()
    if not phoneme:
        return None
        
    # Direct mapping
    if phoneme in INDONESIAN_TO_TOKEN_MAP:
        mapped = INDONESIAN_TO_TOKEN_MAP[phoneme]
        return mapped if mapped else None
    
    # Handle multi-character phonemes or special cases
    if phoneme in ['tʃ', 'ch']:
        return 'ch'
    elif phoneme in ['dʒ', 'j']:
        return 'zh'
    elif phoneme in ['ʃ', 'sy']:
        return 'sh'
    elif phoneme in ['ŋ', 'ng']:
        return '[NG]'
    elif phoneme in ['ɲ', 'ny']:
        return 'n'
    
    # For single character phonemes, try direct lookup
    if len(phoneme) == 1:
        # Check if it's a valid Chinese token
        if phoneme in VALID_CHINESE_TOKENS:
            return phoneme
        # Try with tone 1
        with_tone = f"{phoneme}1"
        if with_tone in VALID_CHINESE_TOKENS:
            return with_tone
        # Fallback to mapping
        return INDONESIAN_TO_TOKEN_MAP.get(phoneme, 'sp1')
    
    # Default fallback for unknown phonemes
    return 'sp1'  # Use silence token for unknown phonemes

def g2p_id(text):
    """
    Indonesian G2P function with Chinese token mapping
    
    Args:
        text (str): Indonesian text to convert
        
    Returns:
        str: Space-separated Chinese tokens with <sos/eos> tags
        
    Example:
        >>> g2p_id("Selamat pagi")
        '<sos/eos> s e1 l a1 m a1 t p a1 g i1 <sos/eos>'
    """
    
    if not text.strip():
        return "<sos/eos> <sos/eos>"
    
    # Initialize Indonesian G2P
    g2p = IndonesianG2p()
    
    # Get phonemes - g2p returns list of lists: [['word1_phonemes'], ['word2_phonemes']]
    phoneme_lists = g2p(text)

    print(f"phoneme {phoneme_lists}")
    
    # Map phonemes to available Chinese tokens
    tokens = []
    for word_phonemes in phoneme_lists:
        for phoneme in word_phonemes:
            mapped_token = map_indonesian_phoneme(phoneme)
            if mapped_token:  # Only add non-empty tokens
                tokens.append(mapped_token)
    
    # Format with start/end tags
    if tokens:
        return f"<sos/eos> {' '.join(tokens)} <sos/eos>"
    else:
        return "<sos/eos> <sos/eos>"

def g2p_id_raw(text):
    """
    Raw Indonesian G2P function - returns the original g2p-id-py output
    
    Args:
        text (str): Indonesian text to convert
        
    Returns:
        list: List of lists containing phonemes for each word
        
    Example:
        >>> g2p_id_raw("Selamat pagi")
        [['s', 'ə', 'l', 'a', 'm', 'a', 't'], ['p', 'a', 'g', 'i']]
    """
    
    g2p = IndonesianG2p()
    return g2p(text)

def g2p_id_with_mapping_debug(text):
    """
    Debug version that shows the mapping process
    
    Args:
        text (str): Indonesian text to convert
        
    Returns:
        dict: Debug information showing original phonemes and mapped tokens
    """
    
    g2p = IndonesianG2p()
    phoneme_lists = g2p(text)
    
    debug_info = {
        'original_phonemes': phoneme_lists,
        'mappings': [],
        'final_tokens': []
    }
    
    for word_phonemes in phoneme_lists:
        for phoneme in word_phonemes:
            mapped_token = map_indonesian_phoneme(phoneme)
            debug_info['mappings'].append({
                'original': phoneme,
                'mapped': mapped_token
            })
            if mapped_token:
                debug_info['final_tokens'].append(mapped_token)
    
    debug_info['formatted_result'] = f"<sos/eos> {' '.join(debug_info['final_tokens'])} <sos/eos>" if debug_info['final_tokens'] else "<sos/eos> <sos/eos>"
    
    return debug_info

def g2p_id_formatted(text, word_separator=" ", phoneme_wrapper=""):
    """
    Customizable Indonesian G2P function with Chinese token mapping
    
    Args:
        text (str): Indonesian text to convert
        word_separator (str): Separator between words (default: " ")
        phoneme_wrapper (str): Wrapper around each phoneme (default: "")
        
    Returns:
        str: Formatted Chinese tokens
    """
    
    if not text.strip():
        return ""
    
    g2p = IndonesianG2p()
    phoneme_lists = g2p(text)
    
    # Format each word
    formatted_words = []
    for word_phonemes in phoneme_lists:
        word_tokens = []
        for phoneme in word_phonemes:
            mapped_token = map_indonesian_phoneme(phoneme)
            if mapped_token:
                word_tokens.append(mapped_token)
        
        if word_tokens:
            if phoneme_wrapper:
                formatted_tokens = [f"{phoneme_wrapper}{token}{phoneme_wrapper}" for token in word_tokens]
            else:
                formatted_tokens = word_tokens
            formatted_words.append(" ".join(formatted_tokens))
    
    return word_separator.join(formatted_words)

if __name__ == "__main__":
    import sys
    from os.path import isfile
    lexicon = read_lexicon(f"{ROOT_DIR}/lexicon/librispeech-lexicon.txt")

    g2p = G2p()
    if len(sys.argv) < 2:
        print("Usage: python %s <text>" % sys.argv[0])
        exit()
    text_file = sys.argv[1]
    if isfile(text_file):
        fp = open(text_file, 'r')
        for line in fp:
            phoneme = g2p_cn_en(line.rstrip(), g2p, lexicon)
            print(phoneme)
        fp.close()
