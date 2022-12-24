import math
import random
import sys
import string
ordered_alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
POPULATION_SIZE = 1000
CLONES = 1
TOURNAMENT_SIZE = 20
TOURNAMENT_WIN = .75
CROSSOVER_POINTS = 5
MUTATION_RATE = .8
NGRAM_SIZE = 4
NGRAM_SIGNIFIER = str(NGRAM_SIZE) + '-gram'
NEXT_NGRAM_SIGNIFIER = str(NGRAM_SIZE + 1) + '-gram'
input_string = sys.argv[1].upper()
numbers_0_to_25 = range(0, 26)

n_gram_dictionary = {} #n_gram: log2(frequency)

cipher_to_translation_and_score = {} #Should be rebuilt each time a new population is created cipher: (translation and score)


def sort_strategies_by_score(strategy):
    score = cipher_to_translation_and_score[strategy][1]
    return score


def generate_initial_random_population():
    population = []
    for x in range(POPULATION_SIZE):
        temp_alphabet = list(ordered_alphabet)
        random.shuffle(temp_alphabet)
        temp_alphabet = ''.join(temp_alphabet)
        population.append(temp_alphabet)
    return population


def generate_n_gram_dictionary():
    with open('ngrams1.tsv') as f:
        read_into_dictionary = False
        for line in f:
            line = line.strip()
            my_arr = line.split()
            if my_arr[0] == NGRAM_SIGNIFIER:
                read_into_dictionary = True
            if my_arr[0] == NEXT_NGRAM_SIGNIFIER:
                return
            if read_into_dictionary and my_arr[0] != NGRAM_SIGNIFIER:
                ngram = my_arr[0]
                frequency = int(my_arr[1])
                ngram_score = math.log(frequency, 2)
                n_gram_dictionary[ngram] = ngram_score


generate_n_gram_dictionary()


def fitness_function(string_input):
    score = 0
    to_be_scored = string_input.split()
    for word in to_be_scored:
        ngrams = generate_ngrams_from_word(word)
        for ngram in ngrams:
            if ngram in n_gram_dictionary:
                score += n_gram_dictionary[ngram]
    return score


def generate_ngrams_from_word(word):
    word = word.translate(str.maketrans('', '', string.punctuation))
    length = len(word)
    if length < NGRAM_SIZE:
        return []
    ngrams = []
    for x in range(0, length - NGRAM_SIZE + 1):
        ngrams.append(word[x:x + NGRAM_SIZE])
    return ngrams


def translate_given_string(string_input, key):
    temp = list(string_input)
    for x in range(len(temp)):
        char = temp[x]
        if char.isalpha():
            temp[x] = key[ordered_alphabet.index(char)]
    return ''.join(temp)


def generate_child(parent1, parent2):
    child = [''] * 26
    indexes_to_crossover = random.sample(numbers_0_to_25, CROSSOVER_POINTS)
    for index in indexes_to_crossover:
        child[index] = parent1[index]
    for char in parent2:
        if char not in child:
            child[child.index('')] = char
    if random.random() < MUTATION_RATE:
        child = mutate(child)
    return ''.join(child)


def mutate(list_arg):
    indexes_to_swap = random.sample(numbers_0_to_25, 2)
    temp = list_arg[indexes_to_swap[0]]
    list_arg[indexes_to_swap[0]] = list_arg[indexes_to_swap[1]]
    list_arg[indexes_to_swap[1]] = temp
    return list_arg


def create_two_tournaments(population):
    tournament_one = random.sample(population, TOURNAMENT_SIZE)
    temp_population = [i for i in population if i not in tournament_one]
    tournament_two = random.sample(temp_population, TOURNAMENT_SIZE)
    return sorted(tournament_one, key=sort_strategies_by_score, reverse=True), sorted(tournament_two, key=sort_strategies_by_score, reverse=True)


def generate_parents(tournament_one, tournament_two):
    parent1 = tournament_winner(tournament_one)
    parent2 = tournament_winner(tournament_two)
    return parent1, parent2


def tournament_winner(tournament):
    for i in range(TOURNAMENT_SIZE):
        if random.random() < TOURNAMENT_WIN:
            return tournament[i]
    return tournament[0]


def create_next_generation(sorted_population):
    new_population = []
    for i in range(CLONES):
        new_population.append(sorted_population[i])
    while len(new_population) < POPULATION_SIZE:
        tournament_one, tournament_two = create_two_tournaments(sorted_population)
        parent1, parent2 = generate_parents(tournament_one, tournament_two)
        child = generate_child(parent1, parent2)
        if child not in new_population:
            new_population.append(child)
    return new_population


def genetic_algorithm():
    new_population = generate_initial_random_population()
    generate_cipher_dictionary(new_population)
    new_population = sorted(new_population, reverse=True, key=sort_strategies_by_score)
    generation = 0
    print('Generation = ' + str(generation) + '  Cipher = ' + new_population[0] + '  Score =  ' + str(cipher_to_translation_and_score[new_population[0]][1]) + "   Translated String = " + cipher_to_translation_and_score[new_population[0]][0])
    while generation < 500:
        generation = generation + 1
        new_population = create_next_generation(new_population)
        generate_cipher_dictionary(new_population)
        new_population = sorted(new_population, reverse=True, key = sort_strategies_by_score)
        print('Generation = ' + str(generation) + '  Cipher = ' + new_population[0] + '  Score =  ' + str(
            cipher_to_translation_and_score[new_population[0]][1]) + "   Translated String = " +
              cipher_to_translation_and_score[new_population[0]][0])
        # if generation == 5: #Just for pstats
        #     return


def generate_cipher_dictionary(population):
    global cipher_to_translation_and_score
    cipher_to_translation_and_score = {}
    for cipher in population:
        new_input = translate_given_string(input_string, cipher)
        cipher_to_translation_and_score[cipher] = (new_input, fitness_function(new_input))


genetic_algorithm()

