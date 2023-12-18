import re
import os
import numpy as np

def read_values(values_file_path):
    letters = []
    values = []
    with open(values_file_path) as file:
        for line in file:
            letter, value = line.strip().split()
            letters.append(letter)
            values.append(int(value))

    postn_values = dict(zip(letters, values))
    sorted_postn_values = dict(sorted(postn_values.items(), key=lambda x: x[1]))

    return sorted_postn_values

def word_least_letter_checker(theword, sorted_postn_values):
    least_letter = None
    least_letter_score = float('inf')
    index_count = 0

    for letter in theword[1:]:
        index_count += 1

        if letter in sorted_postn_values:
            current_score = sorted_postn_values[letter] + min(index_count, 3)

            if least_letter is None or current_score < least_letter_score:
                least_letter = letter
                least_letter_score = current_score

            if least_letter == theword[-1]:
                for letter in theword[1:-1]:
                    if letter in sorted_postn_values and sorted_postn_values[letter] < 5:
                        current_score = sorted_postn_values[letter] + min(index_count, 3)
                        if current_score < least_letter_score:
                            least_letter = letter
                            least_letter_score = current_score

            elif sorted_postn_values.get(least_letter, 0) > 5 and theword[-1] != 'E':
                least_letter = theword[-1]
                least_letter_score = 5
            elif sorted_postn_values.get(least_letter, 0) > 20 and theword[-1] == 'E':
                least_letter = theword[-1]
                least_letter_score = 20
            else:
                least_letter_score = sorted_postn_values.get(letter, 0) + min(index_count, 3)

    return least_letter, least_letter_score, index_count

def least_score_checker_updated(name, sorted_postn_values):
    index_count = 0
    least_letter_tracker = {}
    least_score_tracker = {}
    names_split = name.split()

    for theword in names_split:
        least_letter, least_letter_score, index_count = word_least_letter_checker(theword, sorted_postn_values)
        least_score_tracker[theword] = least_letter_score
        least_letter_tracker[theword] = least_letter

    return least_letter_tracker, least_score_tracker

def name_abbreviator(name, sorted_postn_values):
    abb = ''
    score = -1
    abbreviations_dic = {}
    words = re.findall(r'\b\w+\b', name)

    if len(words) == 1:
        word = words[0]
        if len(word) < 3:
            abb = ''
            score = np.nan
        elif len(word) == 3:
            abb = word
            score_of_mid_letter = sorted_postn_values[word[1]]
            score = score_of_mid_letter + 20 if abb[-1] == 'E' else score_of_mid_letter + 5
        elif len(word) > 3:
            abb = word[0]
            least_letter, least_letter_score, least_index_count = word_least_letter_checker(word, sorted_postn_values)

            if least_letter == word[-1]:
                second_least_letter, second_least_letter_score, second_least_index_count = \
                    word_least_letter_checker(word[:-1], sorted_postn_values)
                abb += second_least_letter
                abb += least_letter
                score = least_letter_score + second_least_letter_score
            else:
                second_least_letter, second_least_letter_score, second_least_index_count = \
                    word_least_letter_checker(word.replace(least_letter, ''), sorted_postn_values)

                if second_least_index_count < least_index_count:
                    abb += second_least_letter
                    abb += least_letter
                else:
                    abb += least_letter
                    abb += second_least_letter

                score += least_letter_score + second_least_letter_score
    elif len(words) >= 3:
        abb = ''.join(word[0] for word in words)[:3]
        score = 0
    elif len(words) == 2 and len(''.join(words)) == 3:
        abb = ''.join(words)
        score = 20 if abb[-1] == 'E' else 5
    elif len(words) == 2:
        abb = words[0][0]
        least_letter_tracker, least_score_tracker = least_score_checker_updated(name, sorted_postn_values)
        least_letter_word = min(least_score_tracker, key=least_score_tracker.get)

        if least_letter_word == words[1]:
            abb += words[1][0]
            abb += least_letter_tracker[least_letter_word]
            score = least_score_tracker[least_letter_word]
        elif least_letter_word == words[0]:
            abb += least_letter_tracker[least_letter_word]
            abb += words[1][0]
            score = least_score_tracker[least_letter_word]

    return abb, score

def abbreviator(path, sorted_postn_values):
    with open(str(path)) as file:
        names = file.readlines()

    staged_names = [name.upper().replace("'", "").replace("\n", "") for name in names]
    cleaned_names = [re.sub(r'[^a-zA-Z \n]', ' ', name) for name in staged_names]
    cleaned_names = [re.sub(r'\s+', ' ', name).strip() for name in cleaned_names]

    abbreviations_dic = {}
    abbreviatons_only = []

    for name in cleaned_names:
        abb, score = name_abbreviator(name, sorted_postn_values)
        abbreviations_dic[name] = {abb: score}
        abbreviatons_only.append(abb)

    name_and_abb_dic = dict(zip(staged_names, abbreviatons_only))

    names_and_abbs = []
    for name_only, abbreviation_only in name_and_abb_dic.items():
        names_and_abbs.append(name_only)
        names_and_abbs.append(abbreviation_only)

    # Create output directory if it doesn't exist
    output_directory = 'output/'
    os.makedirs(output_directory, exist_ok=True)

    # Create output file name
    input_filename = path.split('\\')[-1].split('.')[0].lower()
    surname = 'Umesh'
    output_name = f"{surname}_{input_filename}_abbrevs.txt"

    # Write each item of the list as a new line to the output file
    output_path = os.path.join(output_directory, output_name)
    with open(output_path, 'w') as file:
        file.write('\n'.join(names_and_abbs))

    print(f"Output written to: {output_path}")

if __name__ == '__main__':
    path_name = input('Please enter data filename: ')
    values_file_path = r'C:\Users\sheet\OneDrive\Desktop\Python assignment\values.txt'
    sorted_postn_values = read_values(values_file_path)
    abbreviator(path_name, sorted_postn_values)