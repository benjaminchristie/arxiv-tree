from arxiv import Result
from functools import reduce


class Tree:
    def __init__(self, paper: Result):
        self.leaves = []
        self.paper = paper

    def __getitem__(self, val):
        return reduce(getattr, val, self.paper)

    def get_subtokens(self, token: str, recursion_limit=5) -> set:
        token_results = set([])
        self._get_subtokens(self, token, token_results, recursion_limit=recursion_limit)
        return token_results

    # warning: may throw infinite recursion, but probably not
    def _get_subtokens(self, tree, token: str, token_results: set,
                       recursion_limit=0, current_level=0) -> None:
        if tree[token] in token_results:
            return
        token_results.add(tree[token])
        if recursion_limit >= current_level:
            return
        for t in tree.leaves:
            return self._get_subtokens(t, token, token_results,
                                       recursion_limit=recursion_limit + 1)
