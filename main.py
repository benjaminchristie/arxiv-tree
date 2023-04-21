from tree import Tree
import matplotlib.pyplot as plt
from argparse import ArgumentParser, Namespace
import os
import utils
from utils import get_id
import pickle
import graph
from concurrent.futures import ThreadPoolExecutor


def _fill_tree(tree: Tree,
               max_level=2, current_level=0):
    if current_level >= max_level:
        return
    for leaf in tree.leaves:
        append_references(leaf, max_level, current_level)
        _fill_tree(leaf,
                   max_level=max_level,
                   current_level=current_level + 1)
    return


# may be removed
def fill_tree(tree: Tree, max_level=2):
    _fill_tree(tree, max_level=max_level, current_level=0)


def download_pdfs(tree: Tree):
    path = "./arxiv-download-folder/pdfs/"
    with ThreadPoolExecutor() as pool:
        for leaf in tree.leaves:
            print("Downloading: ", leaf.paper.title)
            pool.submit(leaf.paper.download_pdf, dirpath=path, filename=leaf.paper.title)
    for leaf in tree.leaves:
        download_pdfs(leaf)


def append_references(tree: Tree, max_level, current_level):
    if current_level >= max_level:
        return
    refs = utils.get_references(tree.paper)
    all_res = []
    with ThreadPoolExecutor() as pool:
        for ref in refs:
            title = ref["title"]
            print(f"{'  ' * current_level}Appending {current_level}: ", title)
            res = next(utils.query_title(title).results(), None)
            if res is None:
                break
            all_res.append(res)
            success = True  # probably os exists
            if not os.path.exists(f"./arxiv-download-folder/sources/{get_id(res.entry_id)}.tar.gz"):
                success = pool.submit(utils.download_paper, res)
            if not success:
                refs.remove(ref)
                if res in all_res:
                    all_res.remove(res)
                continue
            new_tree = Tree(res)
            tree.leaves.append(new_tree)
    # wait to extract bibs until download finished
    for res in all_res:
        utils.extract_bib(res)
    for leaf in tree.leaves:
        append_references(leaf, max_level,
                        current_level + 1)
    return


def main(args: Namespace):
    title = args.title
    _id = args.id
    limit = args.limit
    if title != "":
        res = utils.query_title(title, 1)
    elif _id != "":
        res = utils.query_id_list([_id], 1)
    if not os.path.exists("trees/"):
        os.makedirs("trees/")
    if not os.path.exists(f"trees/tree_{title}_{_id}_{limit}.pkl"):
        paper = next(res.results())   # found user paper
        paper_tree = Tree(paper)
        append_references(paper_tree, limit, 0)
        fill_tree(paper_tree, max_level=limit)
        pickle.dump(paper_tree, open(f"trees/tree_{title}_{_id}_{limit}.pkl", "wb"))
    else:
        paper_tree = pickle.load(open(f"trees/tree_{title}_{_id}_{limit}.pkl", "rb"))
    line_width = 48
    graph.get_tree_plot(paper_tree, line_width)
    plt.savefig("result.png")
    download_pdfs(paper_tree)
    return


if __name__ == "__main__":
    if not os.path.exists('arxiv-download-folder/sources/'):
        os.makedirs('arxiv-download-folder/sources/')
    if not os.path.exists('arxiv-download-folder/pdfs/'):
        os.makedirs('arxiv-download-folder/pdfs/')
    parser = ArgumentParser()
    parser.add_argument('--title', help="title of paper to analyze", type=str, default="")
    parser.add_argument('--id', help="id of paper to analyze", type=str, default="")
    parser.add_argument('--limit', help="limit of height of search tree", type=int, default=2)
    main(parser.parse_args())
