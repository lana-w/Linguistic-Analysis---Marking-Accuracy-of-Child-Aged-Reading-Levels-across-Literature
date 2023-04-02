"""
This file contains the implementations for the three different complexity measures:

Dale_Chall: Complexity measured by ratio of unfamiliar words to overall words

Flesch-Kincaid: Complexity measured by average number of syllables per word and average number of words per sentence

Mean Dependency Distance (MDD): Visualizing the dependency relations of each word in a sentence as a syntax tree,
MDD measures the distance between every parent-child pair.

Also included:
Standardizers for each scoring system. Each returns a value measured on a different scale,
so this returns all the scores as a value between 0 and 1.
"""
from data_processing import TextBlock, Sentence
import csv
from typing import Any, Optional
import create_tree as ct


# DALE_CHALL IMPLEMENTATION (complexity, unfamiliar words list initializer, and score standardizer)
def dale_chall_complexity(text: TextBlock) -> float:
    """
    Returns the reading grade of a reader who can comprehend your text.

    Raw Score = 0.1579 * (PDW) + 0.0496 * ASL

    Raw Score = Reading Grade of a reader who can comprehend your text at 3rd grade or below.

    PDW = Percentage of Difficult Words

    ASL = Average Sentence Length in words

    If (PDW) is greater than 5%, then:
    Adjusted Score = Raw Score + 3.6365, otherwise Adjusted Score = Raw Score

    Adjusted Score = Reading Grade of a reader who can comprehend your text at 4th grade or above.
    """
    reading_scores_per_sent = []
    PDW_per_sentence = []
    num_diff_words = 0

    word_list = dale_chall_word_list("Dale-Chall Familiar Words")
    for sentence in text.excerpt:
        # calculate percentage of difficult words
        words = sentence.sentence_to_list()
        num_unfamiliar = 0
        for word in words:
            if word not in word_list:
                num_unfamiliar += 1

        # sentence num_unfamiliar percentage:
        PDW_per_sentence += num_unfamiliar / len(words)
        num_diff_words += num_unfamiliar

    # calculate average sentence length
    num_words = sum(len(sentence.sentence_to_list()) for sentence in text.excerpt)
    ASL = num_words / len(text.excerpt)
    PDW = num_diff_words / num_words

    # Calculate Score
    score = 0.1579 * (PDW) + 0.0496 * ASL

    if PDW > 0.05:
        score += 3.6365

    return score


def dale_chall_word_list(csv_file: str) -> set[str]:
    """
    Given a text file containing all the Dale Chall familiar words, return a set of those words.
    """
    with open(csv_file) as csv_fle:
        reader = csv.reader(csv_fle)
        headers = next(reader)

        word_set = set()
        for row in reader:
            # add to word_set
            word_set.add(str(row))

    return word_set



def standardized_dale_chall(dc_score: float) -> float:
    """Standardizes DC score using the following metric:

    DC Score Scale:
    4.9 and Below	Grade 4 and Below
    5.0 to 5.9	    Grades 5 - 6
    6.0 to 6.9	    Grades 7 - 8
    7.0 to 7.9	    Grades 9 - 10
    8.0 to 8.9	    Grades 11 - 12
    9.0 to 9.9	    Grades 13 - 15 (College)
    10 and Above	Grades 16 and Above (College Graduate)

    Adjusted to 1.0 Scale:
    TODO: figure out scale


    """
    return dc_score / 10


# FLESCH READING EASE SCORE IMPLEMENTATION (complexity, syllable counter, standardizer)
def flesch_complexity_score(text: TextBlock) -> float:
    """
    Return the Flesch Reading Ease Readability Formula
    RE = 206.835 – (1.015 x ASL) – (84.6 x ASW)

    RE = Readability Ease

    ASL = Average Sentence Length (i.e., the number of words divided by the number of sentences)

    ASW = Average number of syllables per word (i.e., the number of syllables divided by the number of words)
    """
    # compute average num of syllables per word.
    average_num_syllables = 0
    num_words = 0
    for sentence in text.excerpt:
        sentence_cleaned = sentence.sentence_to_list()
        average_num_syllables += sum(num_syllables(word) for word in sentence_cleaned)
        num_words += len(sentence_cleaned)

    ASW = average_num_syllables / num_words

    # calculate average sentence length
    num_words = sum(len(sentence.sentence_to_list()) for sentence in text.excerpt)
    ASL = num_words / len(text.excerpt)

    reading_ease = 206.835 - 1.015 * ASL - 84.6 * ASW

    return reading_ease


def num_syllables(word: str) -> int:
    """Using English rules for syllabififcation:

    From the Flesch Reading Ease Formula:
    each vowel in a word is considered one syllable subject to:
    (a) -es, -ed and -e (except -le) endings are ignored;
    (b) words of three letters or shorter count as single syllables; and
    (c) consecutive vowels count as one syllable
    """
    vowels = {"a", "e", "i", "o", "u"}
    length = len(word)
    if length <= 3:
        return 1

    i = 0
    syll_num = 0
    while i < length:
        # if word starts in a vowel, go until next consonant
        ending_conditions = (i == length - 2 and word[i] + word[i + 1] not in {"ed", "es"}) \
                            or (i == length - 1 and word[i] != "e") or (i < length - 2) or \
                            (i == length - 1 and word[i] == "e" and word[i-1] == "l")

        if (word[i] in vowels) and (word[i-1] not in vowels) and ending_conditions:
            syll_num += 1

        i += 1

    return syll_num

def standardized_flesch_ease(fe_score: float) -> float:
    """Standardizes FE score using the following metric:

    FE Scaling System
    90 - 100: Grade 5
    80 - 90:  Grade 6
    70 - 80:  Grade 7
    60 - 70:  Grade 8-9
    50 - 60:  Grade 10 - 12
    30 - 50:  Grades 13 - 15 (College)
    0 - 30:   Grades 16 and Above (College Graduate)

    Standardized Scoring:


    """
    return fe_score

# Dependency Distance Scoring (Text-block implementation, sentence scoring, dependency (tree parsing), flatten helper)

# Note that this uses the NLTK & Spacy Implementations in create_tree
# to tokenize words and create the tree for each sentence


def mean_dependency_distance(text_block: TextBlock) -> float:
    """ Calculates the mean dependency distance (MDD) for a text block
    by finding the average MDD of each of its sentences.

    Notes on how MDD is determined in function mean_dependency_distance_sentence()
    """
    MDD_lists = []
    for sentence in text_block.excerpt:
        MDD_lists.append(mean_dependency_distance_sentence(sentence))

    return sum(MDD_lists) / text_block.sentence_count


def mean_dependency_distance_sentence(sentence: Sentence) -> float:
    """Calculates the mean_dependency_distance given a sentence

    The Mean Dependency Distance (MDD) is:
    MDD(the sentence) = 1/(n-1) * summation of |D*Di| from i = 1 to n-1

    where DDi is the DD (dependency distance) of the ith syntactic link in the sentence.
    Note that the root of the sentence does not have a governor, and so will have a DD of 0.

    The dependency distance of adjacent words is 1, and dependency distance is defined
    as the (absolute) distance between the governor word and its dependent.

    Example:
        "The girl ate an apple" has dependencies:
        The: 1 (dependent of girl, dist 1)
        girl: 1 (dependent of ate, dist 1)
        ate: 0 (verb, has no governer, not dependent of anything)
        an: 1 (dependent of apple, dist 1)
        apple: 2 (dependent of ate, distance 2)
    """
    # Generally: this function calculates the distance between each word and its dependent in the sentence,
    # by traversing through the tree.
    # to calculate MDD, we begin with creating a dependency tree.
    tree = ct.nltk_spacy_tree(sentence.phrase, False)
    # tree.pretty_print()

    # Then, for each word in the tree, which we refer to as the ith word based on sentence position
    # we need to get, for every subtree, the distance between root and children if there is only one child.

    dependents = []
    flatten(get_dependents(tree), dependents)
    # we can now take every pair to get their distances, by finding their position in the sentence.
    # Since dependency tree is formed left to right, going from i =0  to i = len(sentence) - 1
    # will maintain the order in case of duplicates
    distances = []
    for i in range(0, sentence.calculate_word_count(), 2):
        distances.append(abs(sentence.phrase.index(dependents[i], i - 1)
                             - sentence.phrase.index(dependents[i + 1], i - 1)))

    # lastly, summ all DDs and divide by num of words in sentence
    return sum(distances) * 1 / (sentence.calculate_word_count() - 1)


def get_dependents(tree: ct.nltk.tree) -> list[list[ct.nltk.tree]] | None:
    """Get dependents in pairs

    Note that the NLTK built-in methods for ct.nltk.tree in this function add the following conditions:
    tree.subtrees() returns ALL the constituent trees, this includes the subtrees of its subtrees (and so on).
    It does not return ANY leaves, even those which are direct children of the tree's root.
    It also returns itself as one of the listed subtrees.

    tree.leaves() returns ALL the leaves across the full tree, ie all the descendants which are leaves

    tree.label() is analogous to the in-class tree._root, and returns the root value of the tree
    """
    # Then, for each word in the tree, which we refer to as the ith word based on sentence position,
    tree_root = tree.label()
    dependents = []

    # we need to get, for every subtree, the distance between root and children if there is a direct child leaf.
    # If the tree has leaves, cycle through the leaves in its subtrees, and collect all the leaves that are not also
    # leaves of its subtrees (these are the ones which are direct children of the root

    if len(tree.leaves()) >= 1:
        for leaf in tree.leaves():
            subtrees_sans_original = [subtree for subtree in tree.subtrees() if subtree.label() != tree.label()]
            direct_leaf_condition = not any(leaf in subtree.leaves() for subtree in subtrees_sans_original)
            if direct_leaf_condition:
                dependents.append([tree_root, leaf])

    # Iterate through all subtrees (note that leaves are not included here), and if the subtree is not itself,
    # store the subtree's root and this tree's root in list of dependents
    # Recurse into the subtree to collect all the parent-child pairs inside
    for subtree in tree.subtrees():
        if subtree.label() != tree_root:
            # create a pair with root and every child, confirm that the subtree is a direct child of tree
            subtree_direct_child_of_tree_root = []
            if subtree_direct_child_of_tree_root:
                dependents.append([subtree.label(), tree_root])
            dependents.append(get_dependents(subtree))

    return dependents


def flatten(nested_list: str | list, unnested: list) -> None:
    """Mutate the given unnested list variable to store the items of the given nested list, unnested.
    """
    if isinstance(nested_list, str):
        unnested.append(nested_list)
    else:
        unnested.append(flatten(sublist, []) for sublist in nested_list)


def standardized_syntax_score(syn_score: float) -> float:
    """Standardizes syntax dependency score using the following metric:

    MDD Scores follow the following scale:

    < 1: Very Simple Sentences (<4th Grade LeveL) -> For context, these are sentences like "She danced."
    1 - 2: Simple Sentence (4-6 Grade Level)       -> For context, this would be "The girl ate an apple."
    2 - 2.5: More Complex (Multiple Verbs)          -> "She fights like the wind when she is fighting angrily"
    2.543 - 3: Average Score (8-9th Grade Level)
    3 - 4:  Increased Complexity (10 -12 Grade Level)
    4+:  Multiple Nested Clauses (Graduate Level; these are very rare and convoluted sentences)



    """
    return syn_score
