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

# Mapping from Indonesian phonemes (IPA) to available tokens
# This is an approximate mapping since your token list seems to be for Chinese/English
INDONESIAN_TO_TOKEN_MAP = {
    # Vowels - mapping to similar English phonemes
    'a': '[AA1]',     # Indonesian 'a' -> English 'a' sound
    'i': '[IY1]',     # Indonesian 'i' -> English 'ee' sound  
    'u': '[UW1]',     # Indonesian 'u' -> English 'oo' sound
    'e': '[EH1]',     # Indonesian 'e' -> English 'eh' sound
    'ə': '[AH0]',     # Indonesian schwa -> English schwa
    'o': '[OW1]',     # Indonesian 'o' -> English 'oh' sound
    
    # Consonants - mapping to similar sounds
    'b': '[B]',
    'p': '[P]',
    'd': '[D]',
    't': '[T]',
    'g': '[G]',
    'ɡ': '[G]',
    'k': '[K]',
    'f': '[F]',
    'v': '[V]',
    's': '[S]',
    'z': '[Z]',
    'ʃ': '[SH]',      # Indonesian 'sy' sound
    'ʒ': '[ZH]',      # Voiced 'sh' sound
    'tʃ': '[CH]',     # Indonesian 'c' sound
    'dʒ': '[JH]',     # Indonesian 'j' sound
    'h': '[HH]',
    'm': '[M]',
    'n': '[N]',
    'ŋ': '[NG]',      # Indonesian 'ng' sound
    'l': '[L]',
    'r': '[R]',
    'w': '[W]',
    'j': '[Y]',       # Indonesian 'y' sound
    
    # Additional Indonesian sounds
    'ɲ': '[N]',       # Indonesian 'ny' -> closest match
    'x': '[K]',       # Indonesian 'kh' -> k sound
    'ʔ': 'engsp1',          # Glottal stop -> silent
    
    # Fallback for unknown phonemes
    '?': '?',
    '.': '.',
    '!': '!',
    ',': '',          # Remove commas
    ';': '',          # Remove semicolons  
    ':': '',          # Remove colons
    '-': '',          # Remove hyphens
}

def map_indonesian_phoneme(phoneme):
    """Map an Indonesian phoneme to available token"""
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
        return '[CH]'
    elif phoneme in ['dʒ', 'j']:
        return '[JH]'
    elif phoneme in ['ʃ', 'sy']:
        return '[SH]'
    elif phoneme in ['ŋ', 'ng']:
        return '[NG]'
    elif phoneme in ['ɲ', 'ny']:
        return '[N]'
    
    # For single character phonemes, try direct lookup
    if len(phoneme) == 1:
        return INDONESIAN_TO_TOKEN_MAP.get(phoneme, f'uncased{ord(phoneme) % 85 + 15}')
    
    # Default fallback for unknown phonemes
    return f'uncased{hash(phoneme) % 85 + 15}'

def map_indonesian_phonemes_with_sequential_rules(phoneme_list):
    """
    Map Indonesian phonemes with special rules for sequential i/a combinations
    Also handles '?' characters by removing them when they appear between i/a or a/i
    
    Args:
        phoneme_list (list): List of phonemes for a single word
        
    Returns:
        list: List of mapped tokens
    """
    if not phoneme_list:
        return []
    
    tokens = []
    i = 0
    
    while i < len(phoneme_list):
        current_phoneme = phoneme_list[i]
        
        # # Check for sequential i/a or a/i patterns (including with '?' in between)
        # if i < len(phoneme_list) - 1:
        #     next_phoneme = phoneme_list[i + 1]
            
        #     # Case 1: 'i' followed by 'a' (direct)
        #     if current_phoneme == 'i' and next_phoneme == 'a':
        #         tokens.append('i1')
        #         tokens.append('a1')
        #         i += 2  # Skip both phonemes
        #         continue
            
        #     # Case 2: 'a' followed by 'i' (direct)
        #     elif current_phoneme == 'a' and next_phoneme == 'i':
        #         tokens.append('a1')
        #         tokens.append('i1')
        #         i += 2  # Skip both phonemes
        #         continue
            
        #     # Case 3: 'i' followed by '?' followed by 'a'
        #     elif (current_phoneme == 'i' and next_phoneme == 'ʔ' and 
        #           i + 2 < len(phoneme_list) and phoneme_list[i + 2] == 'a'):
        #         tokens.append('i1')
        #         tokens.append('a1')
        #         i += 3  # Skip i, ?, and a
        #         continue
            
        #     # Case 4: 'a' followed by '?' followed by 'i'
        #     elif (current_phoneme == 'a' and next_phoneme == 'ʔ' and 
        #           i + 2 < len(phoneme_list) and phoneme_list[i + 2] == 'i'):
        #         tokens.append('a1')
        #         tokens.append('i1')
        #         i += 3  # Skip a, ?, and i
        #         continue
        
        # # Skip standalone '?' characters (they get removed)
        # if current_phoneme == '?':
        #     i += 1
        #     continue
        
        # Default mapping for non-sequential cases
        mapped_token = map_indonesian_phoneme(current_phoneme)
        if mapped_token:
            tokens.append(mapped_token)
        
        i += 1
    
    return tokens

def g2p_id(text):
    """
    Indonesian G2P function with token mapping and sequential i/a rules
    
    Args:
        text (str): Indonesian text to convert
        
    Returns:
        str: Space-separated tokens with <sos/eos> tags
        
    Example:
        >>> g2p_id("Selamat pagi")
        '<sos/eos> [S] [AH0] [L] a1 [M] a1 [T] [P] a1 [G] i1 <sos/eos>'
    """
    
    if not text.strip():
        return "<sos/eos> <sos/eos>"
    
    # Initialize Indonesian G2P
    g2p = IndonesianG2p()
    
    # Get phonemes - g2p returns list of lists: [['word1_phonemes'], ['word2_phonemes']]
    phoneme_lists = g2p(text)

    print(f"phoneme {phoneme_lists}")
    
    # Map phonemes to available tokens with sequential rules
    all_tokens = []
    for word_phonemes in phoneme_lists:
        word_tokens = map_indonesian_phonemes_with_sequential_rules(word_phonemes)
        all_tokens.extend(word_tokens)
    
    # Format with start/end tags
    if all_tokens:
        return f"<sos/eos> {' '.join(all_tokens)} <sos/eos>"
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
    Debug version that shows the mapping process with sequential rules
    
    Args:
        text (str): Indonesian text to convert
        
    Returns:
        dict: Debug information showing original phonemes and mapped tokens
    """
    
    g2p = IndonesianG2p()
    phoneme_lists = g2p(text)
    
    debug_info = {
        'original_phonemes': phoneme_lists,
        'word_mappings': [],
        'final_tokens': []
    }
    
    for word_idx, word_phonemes in enumerate(phoneme_lists):
        word_tokens = map_indonesian_phonemes_with_sequential_rules(word_phonemes)
        
        debug_info['word_mappings'].append({
            'word_index': word_idx,
            'original_phonemes': word_phonemes,
            'mapped_tokens': word_tokens
        })
        
        debug_info['final_tokens'].extend(word_tokens)
    
    debug_info['formatted_result'] = f"<sos/eos> {' '.join(debug_info['final_tokens'])} <sos/eos>" if debug_info['final_tokens'] else "<sos/eos> <sos/eos>"
    
    return debug_info

def g2p_id_formatted(text, word_separator=" ", phoneme_wrapper=""):
    """
    Customizable Indonesian G2P function with token mapping and sequential rules
    
    Args:
        text (str): Indonesian text to convert
        word_separator (str): Separator between words (default: " ")
        phoneme_wrapper (str): Wrapper around each phoneme (default: "")
        
    Returns:
        str: Formatted tokens
    """
    
    if not text.strip():
        return ""
    
    g2p = IndonesianG2p()
    phoneme_lists = g2p(text)
    
    # Format each word
    formatted_words = []
    for word_phonemes in phoneme_lists:
        word_tokens = map_indonesian_phonemes_with_sequential_rules(word_phonemes)
        
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