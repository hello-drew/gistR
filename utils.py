import re
import sys

CLEANR = re.compile('<.*?>')
OUT = 0
IN = 1

def clean_html(raw_html):
  cleantext = re.sub(CLEANR, '', raw_html)
  return cleantext.strip()

def uppercase(matchobj):
    return matchobj.group(0).upper()

def capitalize_each_sentence(s):
    return re.sub('^([a-z])|[\.|\?|\!]\s*([a-z])|\s+([a-z])(?=\.)', uppercase, s)

def capitalize_first_letter(s):
    if len(s) > 1:
        return s[0].upper() + s[1:]

def return_size_of_object(obj) -> str:
    return f"Size: {format_bytes(sys.getsizeof(obj))}"

def format_bytes(size: int):
    power = 2**10
    n = 0
    power_labels = {0 : '', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size /= power
        n += 1
    return f"{round(size, 1)} {power_labels[n]}"

alphabets= "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|Prof|Capt|Cpt|Lt|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov|edu|me)"
digits = "([0-9])"

def split_into_sentences(text):
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    text = re.sub(digits + "[.]" + digits,"\\1<prd>\\2",text)
    if "..." in text: text = text.replace("...","<prd><prd><prd>")
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences

def ordered_list_no_duplicates(sequence):
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]

def remove_duplicate_sentences(text) -> str:
    sentences = split_into_sentences(text)
    sentences = ordered_list_no_duplicates(sentences)
    return " ".join(sentences)

def chunk_list(lst: list, n: int):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def chunk_sentences_into_list(text, chunk_size):
    sentences = split_into_sentences(text)
    chunks = chunk_list(sentences, chunk_size)
    text_chunks = [" ".join(chunk).strip() for chunk in chunks]
    return text_chunks


def count_words_in_string(string):
    state = OUT
    wc = 0
 
    # Scan all characters one by one
    for i in range(len(string)):
 
        # If next character is a separator,
        # set the state as OUT
        if (string[i] == ' ' or string[i] == '\n' or
            string[i] == '\t'):
            state = OUT
 
        # If next character is not a word
        # separator and state is OUT, then
        # set the state as IN and increment
        # word count
        elif state == OUT:
            state = IN
            wc += 1
 
    # Return the number of words
    return wc