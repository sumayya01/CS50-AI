import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a set of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.
    """
    n = len(corpus)
    probs = {}

    # If the page has outgoing links
    if corpus[page]:
        for p in corpus:
            probs[p] = (1 - damping_factor) / n
            if p in corpus[page]:
                probs[p] += damping_factor / len(corpus[page])
    else:
        # If no outgoing links, distribute equally among all pages
        for p in corpus:
            probs[p] = 1 / n

    return probs


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.
    """
    counts = {page: 0 for page in corpus}

    # First sample chosen at random
    page = random.choice(list(corpus.keys()))
    counts[page] += 1

    # Generate the rest of the samples
    for _ in range(1, n):
        probs = transition_model(corpus, page, damping_factor)
        pages, weights = zip(*probs.items())
        page = random.choices(pages, weights=weights, k=1)[0]
        counts[page] += 1

    # Normalize counts to probabilities
    pagerank = {page: counts[page] / n for page in corpus}
    return pagerank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.
    """
    n = len(corpus)
    pagerank = {page: 1 / n for page in corpus}

    # Treat pages with no links as linking to all pages
    links = {page: (corpus[page] if corpus[page] else set(corpus.keys()))
             for page in corpus}

    converged = False
    while not converged:
        new_rank = {}
        for page in corpus:
            total = 0
            for other in corpus:
                if page in links[other]:
                    total += pagerank[other] / len(links[other])
            new_rank[page] = (1 - damping_factor) / n + damping_factor * total

        # Check if all ranks have converged
        converged = all(abs(new_rank[p] - pagerank[p]) < 0.001 for p in pagerank)
        pagerank = new_rank

    return pagerank


if __name__ == "__main__":
    main()
