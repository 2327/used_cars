'''This module contain Name_Cleaner class which methods provide you ability to clean any string which you want from junk
words, char groups, multispaces and so on. Args that you should define with class object initialisation:
    bad_row - it is a row that contain regular expression for searching and deleting junk words and chars groups in your
string;
    replace_dict - dictionary which keys contain expected strings and values contain replacement strings for it;
    first_words_list - list that contain words what you want to put to beginning of the string if it contain this words;
    last_words_list - list that contain words what you want to put to end of the string if it contain this words.

    Module contain also samples of args for Name_Cleaner that you can use to clean used cars models names that you got from
auto.ru scrapping.'''


import re
from collections import deque


bad_row = r'Рестайлинг( 1)?( 2)?\b|(?<!Mark )(?<!Lancer )(?<!Model )\b(I?X?V?I{,3}){1}\b(?!-Trail)(?!-klasse)|\([^\)\(]*\)|-klasse| [A-Z]{1}\d{2,3} '

replace_dict = {'1 серия II (F20/F21) Рестайлинг 2': '1 серия 118i'}

first_words_list = ['AMG']

last_words_list = ['Coupe']

class Name_Cleaner():

    __slots__ = ['bad_row', 'replace_dict', 'first_list', 'last_list']

    def __init__(self, bad_row, replace_dict, first_list = [], last_list = []):
        self.bad_row = re.compile(bad_row)
        self.replace_dict = replace_dict
        self.first_list = first_list
        self.last_list = last_list

    def order_checker(self, string):
        first = deque()
        last = deque()
        middle = deque()
        dump = [first, middle, last]
        words = string.split(' ')
        while words:
            word = words.pop()
            if word in self.first_list:
                first.appendleft(word)
            elif word in self.last_list:
                last.appendleft(word)
            else:
                middle.appendleft(word)
        for item in dump:
            words += item
        result = ' '.join(words)
        return result

    def deep_duplicates_deleter(self, string):
        words = string.split(' ')
        for word in words:
            if len(word) > 1:
                flag = re.findall(f'\\b{word}\\w+', string)
                if flag:
                    words.remove(word)
        result = ' '.join(words)
        return result

    def duplicates_deleter(self, string):
        words_list = string.split(' ')
        words = deque()
        while words_list:
            word = words_list.pop()
            words.appendleft(word)
            while word in words_list:
                words_list.remove(word)
        result = ' '.join(words)
        return result

    def name_replacer(self, string):
        if self.replace_dict:
            string = re.sub(r'\n', '', string)
            if string in replace_dict.keys():
                result = replace_dict[string]
                return result
        
    def name_cleaner(self, string):
        return self.bad_row.sub('', string)

    def multispaces_deleter(self, string):
        result = re.sub(r' +', ' ', string)
        return result

    def tiles_deleter(self, string):
        result = re.sub(r'[\W_]+$|^[\W_]+', '', string)
        return result

    def treat_name(self, string):
        result = self.name_replacer(string)
        if not result:
            result = string
            operations = [self.duplicates_deleter, self.name_cleaner, self.deep_duplicates_deleter, self.multispaces_deleter, self.tiles_deleter, self.order_checker]
            for operation in operations:
                result = operation(result)
        return result

if __name__=='__main__':
    treater = Name_Cleaner(bad_row, replace_dict, first_words_list, last_words_list)
    with open('./MODELS.txt', encoding='utf-8') as f:
        for line in f.readlines():
            output = treater.treat_name(line)
            print(line, '<-------->', output, '\n')

    lines = ['V-klasse компактный II 220 d компактный', 'S-klasse AMG  III (W222, C217) 63 AMG',
             'Mercedes-Benz\' \'V-klasse компактный II 220 d компактный',
             'Mercedes-Benz\' \'GL-klasse AMG  63 AMG',
             'Mercedes-Benz\' \'GLE Coupe AMG  C292 63',
             'FX  II (S51) Рестайлинг FX37',
             'Protege  III (BJ) Protege5']
    for line in lines:
        output = treater.treat_name(line)
        print(line, '<-------->', output, '\n')
    
