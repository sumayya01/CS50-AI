from logic import *

# Symbols for A
AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

# Symbols for B
BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

# Symbols for C
CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Base knowledge: Each person is either a knight or a knave, but not both
knowledgeBase = And(
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),

    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),

    Or(CKnight, CKnave),
    Not(And(CKnight, CKnave))
)

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    knowledgeBase,
    Implication(AKnight, And(AKnight, AKnave)),
    Implication(AKnave, Not(And(AKnight, AKnave)))
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    knowledgeBase,
    Implication(AKnight, And(AKnave, BKnave)),
    Implication(AKnave, Not(And(AKnave, BKnave)))
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    knowledgeBase,

    # A says: "We are the same kind."
    Implication(AKnight, Or(And(AKnight, BKnight), And(AKnave, BKnave))),
    Implication(AKnave, Not(Or(And(AKnight, BKnight), And(AKnave, BKnave)))),

    # B says: "We are of different kinds."
    Implication(BKnight, Or(And(AKnight, BKnave), And(AKnave, BKnight))),
    Implication(BKnave, Not(Or(And(AKnight, BKnave), And(AKnave, BKnight))))
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave." (we don't know which)
# B says "A said 'I am a knave.'" and then says "C is a knave."
# C says "A is a knight."
A_said_knave = Implication(AKnight, AKnave)
A_said_also_knave = Implication(AKnave, Not(AKnave))

knowledge3 = And(
    knowledgeBase,

    # B says "A said 'I am a knave'."
    # This is equivalent to B saying that one of the two implications from A must be true.
    # If B is a knight, A must have uttered a self-contradictory statement
    Implication(BKnight, And(A_said_knave, A_said_also_knave)),
    Implication(BKnave, Not(And(A_said_knave, A_said_also_knave))),
    
    # B also says "C is a knave."
    Implication(BKnight, CKnave),
    Implication(BKnave, Not(CKnave)),

    # C says "A is a knight."
    Implication(CKnight, AKnight),
    Implication(CKnave, Not(AKnight))
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")

if __name__ == "__main__":
    main()
    
