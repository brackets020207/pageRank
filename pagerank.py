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
    a list of all other pages in the corpus that are linked to by the page.
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

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """    
    model = {}
    if len(corpus[page]) != 0:
        for key in corpus:
            model[key] = (1-damping_factor)/len(corpus)
        for link in corpus[page]:
            model[link] += (damping_factor)/len(corpus[page])
    else:
        for key in corpus:
            model[key] = 1/(len(corpus))

    return model


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    nextpage = None
    pageRanks = {}
    page = random.choice(list(corpus.keys()))
    for i in range(n):
        model = transition_model(corpus, page, damping_factor)
        choice = random.random()
        total = 0
        for key in model:
            total+= model[key]
            if total > choice:
                nextpage = key
                break
        pageRanks[page] = pageRanks.get(page,0) + 1
        page = nextpage
    
    for page in pageRanks:
        pageRanks[page] = pageRanks[page] / n
    return pageRanks


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    
    # Get number of links to each page
    pageRank = {}
    links_to = {}
    for page in corpus:
        links_to[page] = set()

    for page in corpus:
        if corpus[page] == set():
            corpus[page].update(set(corpus.keys()))

    for page in corpus:
        # set default page rank
        pageRank[page] = 1/len(corpus)
        for link in corpus[page]:
            if link in links_to:
                links_to[link].add(page)
            else:
                links_to[link] = {page}

    maxdifference = 1
    while maxdifference > 0.0001:
        lastrank = pageRank.copy()
        maxdifference = 0  
        for page in pageRank:
            pageRank[page] = (1-damping_factor)/len(corpus)
            for link in links_to[page]:
                pageRank[page] += damping_factor * (pageRank[link] / len(corpus[link]))
            
            if abs(pageRank[page] - lastrank[page]) > maxdifference:
                maxdifference = abs(pageRank[page] - lastrank[page])

    return pageRank


if __name__ == "__main__":
    main()
