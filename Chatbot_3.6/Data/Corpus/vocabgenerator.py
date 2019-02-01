import os
import colorama

AUG_FOLDER = "Augment"

VOCAB_FILE = "vocab.txt"
CORNELL_DATA_FILE = "cornell_cleaned_new.txt"
REDDIT_DATA_FILE = "reddit_cleaned_part.txt"
EXCLUDED_FILE = "excluded.txt"

colorama.init()

def generate_vocab_file(corpus_dir):
    """
    Generate the vocab.txt file for the training and prediction/inference. 
    Manually remove the empty bottom line in the generated file.
    """
    vocab_list = []

    # Special tokens, with IDs: 0, 1, 2
    for t in ['_unk_', '_bos_', '_eos_']:
        vocab_list.append(t)

    # The word following this punctuation should be capitalized in the prediction output.
    for t in ['.', '!', '?']:
        vocab_list.append(t)

    # The word following this punctuation should not precede with a space in the prediction output.
    for t in ['(', '[', '{', '``', '$']:
        vocab_list.append(t)

    for fd in range(0, -1, -1):
        if fd == 0:
            file_dir = os.path.join(corpus_dir, AUG_FOLDER)

        for data_file in sorted(os.listdir(file_dir)):
            full_path_name = os.path.join(file_dir, data_file)
            if os.path.isfile(full_path_name) and data_file.lower().endswith('.txt'):
                if fd == 0 and (data_file == CORNELL_DATA_FILE or data_file == REDDIT_DATA_FILE):
                    continue  # Will be processed below
                with open(full_path_name, 'r') as f:
                    for line in f:
                        l = line.strip()
                        if not l:
                            continue
                        if l.startswith("Q:") or l.startswith("A:"):
                            tokens = l[2:].strip().split(' ')
                            for token in tokens:
                                if len(token) and token != ' ':
                                    t = token.lower()
                                    if t not in vocab_list:
                                        vocab_list.append(t)
    
    print(colorama.Fore.GREEN + "Vocab size after all base data files scanned: " + format(len(vocab_list)) + colorama.Fore.RESET)

    temp_dict = {}  # A temp dict
    cornell_file = os.path.join(corpus_dir, AUG_FOLDER, CORNELL_DATA_FILE)
    if os.path.exists(cornell_file):
        with open(cornell_file, 'r') as f1:
            for line in f1:
                ln = line.strip()
                if not ln:
                    continue
                if ln.startswith("Q:") or ln.startswith("A:"):
                    tokens = ln[2:].strip().split(' ')
                    for token in tokens:
                        if len(token) and token != ' ':
                            t = token.lower()
                            if t not in vocab_list:
                                if ln.startswith("A:"):  # Keep all for responses
                                    vocab_list.append(t)
                                else:
                                    if t not in temp_dict:
                                        temp_dict[t] = 1
                                    else:
                                        temp_dict[t] += 1
                                        if temp_dict[t] >= 2:
                                            vocab_list.append(t)

    print(colorama.Fore.GREEN + "Vocab size after cornell data file scanned: " +format(len(vocab_list)) + colorama.Fore.RESET)

    reddit_file = os.path.join(corpus_dir, AUG_FOLDER, REDDIT_DATA_FILE)
    if os.path.exists(reddit_file):
        with open(reddit_file, 'r') as f2:
            line_cnt = 0
            for line in f2:
                line_cnt += 1
                if line_cnt % 200000 == 0:
                    print("{:,} lines of reddit data file scanned.".format(line_cnt))
                ln = line.strip()
                if not ln:
                    continue
                if ln.startswith("Q:") or ln.startswith("A:"):
                    tokens = ln[2:].strip().split(' ')
                    for token in tokens:
                        if len(token) and token != ' ':
                            t = token.lower()
                            if t not in vocab_list:
                                if ln.startswith("A:"):  # Keep all for responses
                                    vocab_list.append(t)
                                else:
                                    if t not in temp_dict:
                                        temp_dict[t] = 1
                                    else:
                                        temp_dict[t] += 1
                                        if temp_dict[t] >= 2:
                                            if t.startswith('.') or t.startswith('-') \
                                                    or t.endswith('..') or t.endswith('-'):
                                                continue

                                            vocab_list.append(t)

    with open(VOCAB_FILE, 'a') as f_voc:
        for v in vocab_list:
            f_voc.write("{}\n".format(v))

    print(colorama.Fore.GREEN + "The final vocab file generated. Vocab size: " + format(len(vocab_list)) + colorama.Fore.RESET)

    with open(EXCLUDED_FILE, 'a') as f_excluded:
        for k, _ in temp_dict.items():
            if k not in vocab_list:
                f_excluded.write("{}\n".format(k))

if __name__ == "__main__":
    from settings import PROJECT_ROOT

    corp_dir = os.path.join(PROJECT_ROOT, '', '')
    generate_vocab_file(corp_dir)
