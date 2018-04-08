import glob
import gzip
import json
import logging
import re
import dictionary
import datetime
import pickle
import progressbar
from collections import deque

logging.basicConfig(filename='walk-away.log', format='%(asctime)s %(message)s', level=logging.DEBUG)

corpusDirectory = "corpus/foo/xml/en/1989/98067/"
# corpusDirectory = "corpus/foo/xml/en/"
# corpusDirectory = "corpus/OpenSubtitles2018/xml/en/"
walk_away = []
BUFFER_SIZE = 30
AWAY_PAUSE = 10000
WALKAWAY_DEFAULT_FILE = 'walkaway'


def parse_time(time_string):
    token = [None, None, None]
    time_groups = re.search('<time id=\"(.+)\" value=\"((\d+):(\d+):(\d+),(\d+))\" />', time_string)
    if time_groups is None:
        return None
    time_id = time_groups.group(1).lower()
    time_hr = time_groups.group(2)
    hours = int(time_groups.group(3))
    minutes = int(time_groups.group(4))
    seconds = int(time_groups.group(5))
    millis = int(time_groups.group(6))

    time_in_millis = millis + seconds * 1000 + minutes * 60 * 1000 + hours * 60 * 60 * 1000

    token[0] = time_hr

    if time_id.endswith('s'):
        token[1] = time_in_millis
    elif time_id.endswith('e'):
        token[2] = time_in_millis

    return token


def parse_word(word_string):
    word_groups = re.search('>(.+)<', word_string)
    if word_groups is None:
        return ''

    return [word_groups.group(1).lower(), None, None]


def get_movie_id(filename):
    movie_id_groups = re.search("\d+/(\d+)/\d+\.xml.gz", filename)
    if movie_id_groups is None:
        return None

    return movie_id_groups.group(1)


def parse_line(line):
    line_string = line.decode('utf-8').lower()

    if '<time ' in line_string:
        return parse_time(line_string)
    elif '<w ' in line_string:
        return parse_word(line_string)

    return None


def replace_time(token):
    # print(token, token[0][1], token[1][2])
    if token[0][2] and token[1][1]:
        return '|- ' + str((token[1][1] - token[0][2]) // 1000)

    if token[0][1]:
        return '-|'

    return token[0][0]


def print_line(buffer):
    bar = list(buffer)
    foo = zip(bar, bar[1:])

    # print(list(foo))
    xxx = map(replace_time, foo)
    return ' '.join(xxx)


def is_pause_after(buffer):
    foo = list(buffer)
    BUFFER_CENTER = BUFFER_SIZE // 2
    bar = foo[BUFFER_CENTER: BUFFER_CENTER + 3]
    kaz = zip(bar, bar[1:])

    for token in kaz:
        if token[0][2] and token[1][1]:
            return (token[1][1] - token[0][2]) > AWAY_PAUSE

    return False


def buffer_start(buffer):
    for token in buffer:
        if token[1]:
            return token[0]

    return 'None'


def log_walkaways(file_foo):
    logging.info(file_foo['movie']['name'] + '\n')
    for timestamp, context in file_foo['occurence'].items():
        logging.info('  ' + timestamp + ': ' + context + '\n')
    logging.info('\n')


def indentify_walk_aways(movie_map):
    walk_aways = []

    logging.info('AWAY_PAUSE: %d' % AWAY_PAUSE)

    filename_list = list(glob.iglob(corpusDirectory + '**/*.xml.gz', recursive=True))
    c = 0

    bar = progressbar.ProgressBar(max_value=len(filename_list))
    for filename in filename_list:
        walkaways = {}
        with gzip.open(filename, 'r') as subtitle_file:
            movie_id = get_movie_id(filename)

            buffer = deque([['', None, None]] * BUFFER_SIZE, maxlen=BUFFER_SIZE)

            for line in subtitle_file:

                token = parse_line(line)

                if token is None or token[0] is None:
                    continue

                buffer.append(token)

                # If thank you is in the middle of the buffer
                is_thank_you = buffer[BUFFER_SIZE // 2][0] is not None and 'thank' in buffer[BUFFER_SIZE // 2][0]
                if is_thank_you:
                    is_pause_after_thank_you = is_pause_after(buffer)
                    if is_pause_after_thank_you:
                        context = print_line(buffer)
                        buffer_start_value = buffer_start(buffer)
                        if 'occurence' not in walkaways:
                            walkaways = {
                                'movie': movie_map[movie_id],
                                'occurence': {}
                            }

                        walkaways['occurence'][buffer_start_value] = context

        if 'occurence' in walkaways:
            walk_aways.append(walkaways)
            log_walkaways(walkaways)

        bar.update(c)
        c = c + 1
    return walk_aways


if __name__ == '__main__':
    movie_dictionary = {}
    try:
        logging.info('Loading dictionary...')
        movie_dictionary = dictionary.load_dictionary()
    except FileNotFoundError:
        logging.info('Building dictionary...')
        movie_dictionary = dictionary.build_dictionary()

    logging.info('Reading...')
    walk_aways = indentify_walk_aways(movie_dictionary)

    with open('data/%s-%s.pkl' % (WALKAWAY_DEFAULT_FILE, str(datetime.datetime.now())), 'wb+') as output:
        pickle.dump(walk_aways, output, pickle.HIGHEST_PROTOCOL)

    with open('data/%s-%s.json' % (WALKAWAY_DEFAULT_FILE, str(datetime.datetime.now())), 'w+') as fp:
        json.dump(walk_aways, fp)
