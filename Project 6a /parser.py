import nltk
import sys

# Terminal rules
TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

# Nonterminal rules
NONTERMINALS = """
S -> NP VP | S Conj S

NP -> N | Det N | Det AdjP N | AdjP N | NP PP | NP Conj NP
AdjP -> Adj | Adj AdjP

VP -> V | V NP | V PP | V NP PP | Adv VP | VP Adv | VP Conj VP
PP -> P NP
"""

# Build grammar and parser
grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():
    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()
    else:
        s = input("Sentence: ")

    # Preprocess
    s = preprocess(s)

    # Parse
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return

    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree and NP chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Tokenize sentence, convert to lowercase,
    and remove non-alphabetic tokens.
    """
    tokens = nltk.word_tokenize(sentence.lower())
    words = [w for w in tokens if any(c.isalpha() for c in w)]
    return words


def np_chunk(tree):
    """
    Return a list of noun phrase chunks.
    A NP chunk is an NP subtree without nested NP inside it.
    """
    chunks = []
    for subtree in tree.subtrees():
        if subtree.label() == "NP":
            if not any(child.label() == "NP" for child in subtree.subtrees(lambda t: t != subtree)):
                chunks.append(subtree)
    return chunks


if __name__ == "__main__":
    main()
