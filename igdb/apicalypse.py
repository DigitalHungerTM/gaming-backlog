from typing import List


class QueryBuilder:
    _operations: List[str]
    def __init__(self):
        self._operations = []

    def fields(self, fields: List[str]):
        """
        :param fields: Fields to include in the result
        """
        self._operations.append(f'fields {','.join(fields)};')
        return self

    def exclude(self, fields: List[str]):
        """
        :param fields: Fields to exclude from the result
        """
        self._operations.append(f'exclude {','.join(fields)};')
        return self

    def where(self, filter: str):
        """
        :param filter: A 'where' query. See https://apicalypse.io/syntax/#where for supported operators.
        """
        self._operations.append(f'where {filter};')
        return self

    def limit(self, limit: int):
        """
        :param limit: Number of items to return.
        """
        self._operations.append(f'limit {limit};')
        return self

    def offset(self, offset: int):
        """
        :param offset: The index to start returning results from.
        """
        self._operations.append(f'offset {offset};')
        return self

    def sort(self, field: str, desc: bool=False):
        """
        :param field: Field to sort by.
        :param desc: Whether to sort in desc order. Default `False`.
        """
        self._operations.append(f'sort {field}{' desc' if desc else 'asc'};')
        return self

    def search(self, value: str):
        """
        :param value: Value to search for. If no field is passed, search is performed on the default column.
        """
        self._operations.append(f'search "{value}";')
        return self

    def build(self):
        """
        Build the query into a full query string.
        :return: The built query string.
        """
        return ' '.join(self._operations)