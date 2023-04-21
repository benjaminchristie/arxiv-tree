import arxiv
import bibtexparser
import tarfile
import os


def get_id(_id):
    return _id.split('/')[-1]


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


def download_paper(paper: arxiv.Result):
    download_folder = "./arxiv-download-folder/sources/"
    paper.download_source(dirpath=download_folder, filename=f"{get_id(paper.entry_id)}.tar.gz")


def extract_bib(paper: arxiv.Result):
    _from = f"./arxiv-download-folder/sources/{get_id(paper.entry_id)}.tar.gz"
    _to = f"./arxiv-download-folder/bibs/{get_id(paper.entry_id)}/"
    if not os.path.exists(_from):
        download_paper(paper)
    if not os.path.exists(_to):
        os.makedirs(_to)
    file = tarfile.open(_from)
    # find bib file
    output = None
    for member in file.getmembers():
        if os.path.splitext(member.path)[-1] == ".bib":
            output = member.path
            break
    if output is not None:
        file.extract(output, _to)
        os.rename(_to + output, _to + "bibtex.bib")
    else:
        open(_to + "bibtex.bib", "a").close()


def get_references(paper: arxiv.Result):
    bibpath = f"./arxiv-download-folder/bibs/{get_id(paper.entry_id)}/bibtex.bib"
    if not os.path.exists(bibpath):
        extract_bib(paper)
    with open(bibpath) as file:
        try:
            bib_database = bibtexparser.load(file)
        except bibtexparser.bibdatabase.UndefinedString:  # KeyError
            return []
    return bib_database.entries
