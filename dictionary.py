import gzip
import pickle

OPENSUBTITLES_DUMP_FILE = 'corpus/subtitles_all.txt.gz'
DUMP_FILE_HEADER = 'ImdbID'
DICTIONARY_DEFAULT_FILE = 'data/movie_dictionary.pkl'


def load_dictionary(filename=DICTIONARY_DEFAULT_FILE):
    with open(filename, 'rb') as input:
        return pickle.load(input)


def build_dictionary(filename=OPENSUBTITLES_DUMP_FILE, header=DUMP_FILE_HEADER):
    movie_dict = {}

    with gzip.open(filename, 'r') as f:
        for line in f:
            try:
                pairs = line.decode('utf-8').split('\t')
                title_id = pairs[6]
                movie_dict[title_id] = {
                    'id': title_id,
                    'name': pairs[1],
                    'release_date': pairs[2],
                    'season': pairs[11],
                    'episode': pairs[12]
                }

            except IndexError:
                None

    del movie_dict[header]
    return movie_dict


if __name__ == '__main__':
    with open(DICTIONARY_DEFAULT_FILE, 'wb+') as output:
        dictionary = build_dictionary()
        pickle.dump(dictionary, output, pickle.HIGHEST_PROTOCOL)
