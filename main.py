import arxiv
from tree import Tree
import bibtexparser
import tarfile
from argparse import ArgumentParser, Namespace
import os


def query_id_list(id_list: list[str], max_results=1):
    search = arxiv.Search(id_list=id_list,
                          sort_by=arxiv.SortCriterion.Relevance,
                          sort_order=arxiv.SortOrder.Descending,
                          )
    return search


def query_title(title: str, max_results=1):
    search = arxiv.Search(query=title,
                          max_results=max_results,
                          sort_by=arxiv.SortCriterion.Relevance,
                          sort_order=arxiv.SortOrder.Descending,
                          )
    return search


def extract(filename: str,
            file_to_extract="bibtex.bib",
            folder_to_extract="./arxiv-download-folder/bibs/"):
    file = tarfile.open(filename)
    file.extract(file_to_extract, folder_to_extract)


# parses bibtex.bib for references
def get_references(_id: str):
    filename = f"{_id}/bibtext.bib"
    with open(filename) as file:
        bib_database = bibtexparser.load(file)
    return bib_database.entries  # probably want ...entries.titles


def main(args: Namespace,
         download_folder="./arxiv-download-folder/sources/",
         papers_folder="./arxiv-download-folder/pdfs/"):
    # 1a. generate tree originating at paper
    title = args.title
    _id = args.id
    limit = args.searchlimit
    if title != "":
        res = query_title(title, 1)
    elif _id != "":
        res = query_id_list([_id], 1)
    paper_tree = Tree({"title": title, "id": _id})

    # 1b. download first pdf in tar.gz format
    paper = res.results(0)
    paper.download_source(dirpath=download_folder, filename=f"{title}_{_id}.tar.gz")

    # 2. extract to tar.gz format
    return


if __name__ == "__main__":
    if not os.path.exists('arxiv-download-folder/sources/'):
        os.makedirs('arxiv-download-folder/sources/')
    if not os.path.exists('arxiv-download-folder/pdfs/'):
        os.makedirs('arxiv-download-folder/pdfs/')
    parser = ArgumentParser()
    parser.add_argument('--title', help="title of paper to analyze", type=str, default="")
    parser.add_argument('--id', help="id of paper to analyze", type=str, default="")
    parser.add_argument('--searchlimit', help="limit of recursive search", type=int, default=2)
    main(parser.parse_args())
