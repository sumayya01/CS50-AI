import sys
from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generator.
        """
        self.crossword = crossword
        # Start with all words as possible values
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )

        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]

                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)
        print(f"Image saved successfully to: {filename}")

    def solve(self):
        """
        Enforce node and arc consistency, then solve with backtracking.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Remove values that do not satisfy unary constraints
        (length of the word must equal variable length).
        """
        for var in self.domains:
            for word in set(self.domains[var]):
                if len(word) != var.length:
                    self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with `y`.
        """
        revised = False
        overlap = self.crossword.overlaps[x, y]

        if overlap is None:
            return False

        i, j = overlap
        for word_x in set(self.domains[x]):
            # keep word_x only if there is some word_y that matches at overlap
            if all(word_x[i] != word_y[j] for word_y in self.domains[y]):
                self.domains[x].remove(word_x)
                revised = True
        return revised

    def ac3(self, arcs=None):
        """
        AC-3 algorithm to enforce arc consistency.
        """
        if arcs is None:
            arcs = [(x, y) for x in self.crossword.variables
                    for y in self.crossword.neighbors(x)]

        queue = list(arcs)
        while queue:
            x, y = queue.pop(0)
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for z in self.crossword.neighbors(x) - {y}:
                    queue.append((z, x))
        return True

    def assignment_complete(self, assignment):
        """
        Assignment is complete if all variables are assigned.
        """
        return set(assignment.keys()) == self.crossword.variables

    def consistent(self, assignment):
        """
        Assignment is consistent if all constraints are satisfied.
        """
        # distinct values
        if len(set(assignment.values())) < len(assignment.values()):
            return False

        for var, word in assignment.items():
            # length constraint
            if len(word) != var.length:
                return False

            # overlaps
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    i, j = self.crossword.overlaps[var, neighbor]
                    if word[i] != assignment[neighbor][j]:
                        return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Least-constraining values: prefer values that rule out the fewest
        options for neighbors.
        """
        def conflicts(value):
            count = 0
            for neighbor in self.crossword.neighbors(var):
                if neighbor not in assignment:
                    i, j = self.crossword.overlaps[var, neighbor]
                    for w in self.domains[neighbor]:
                        if value[i] != w[j]:
                            count += 1
            return count

        return sorted(self.domains[var], key=conflicts)

    def select_unassigned_variable(self, assignment):
        """
        Select an unassigned variable using MRV heuristic,
        breaking ties with degree heuristic.
        """
        unassigned = [v for v in self.crossword.variables if v not in assignment]
        return min(
            unassigned,
            key=lambda var: (len(self.domains[var]), -len(self.crossword.neighbors(var)))
        )

    def backtrack(self, assignment):
        """
        Backtracking search to find a full assignment.
        """
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = value
            if self.consistent(new_assignment):
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result
        return None


def main():
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
