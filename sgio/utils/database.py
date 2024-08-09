from __future__ import annotations

class DataBase():
    """Collection of a type of data/object.

    Parameters
    ----------
    name : str, optional
        Name of the database, by default ''.
    data : list, optional
        List of data, by default [].
    """
    def __init__(self, name:str='', data:list=[]):
        self._name = name
        self._data = data

    def __repr__(self):
        s = ['-'*10,]
        for _d in self._data:
            s.append(str(_d))
            s.append('-'*10)
        return '\n'.join(s)

    @property
    def name(self): return self._name
    @property
    def data(self): return self._data

    def setName(self, name): self._name = name

    def getItemByName(self, name):
        """Get an item by name.

        Parameters
        ----------
        name : str
            Name of the item.

        Returns
        -------
        object
            Item with the given name.
        """
        for _item in self._data:
            if _item.name == name:
                return _item

        return None

    def addItem(self, item):
        """Add an item to the database.

        Parameters
        ----------
        item : object
            Item to be added.
        """
        self._data.append(item)

    def update(self, db:list|DataBase):
        """Update the database with a list of items or another database.

        Parameters
        ----------
        db : list|DataBase
            List of items or another database.
        """
        if isinstance(db, list):
            self._data.extend(db)
        elif isinstance(db, DataBase):
            self._data.extend(db.data)

    def toDictionary(self, **kwargs) -> dict:
        """Convert the database to a dictionary.
        """
        _items = []
        for _item in self._data:
            _items.append(_item.toDictionary(**kwargs))
        _dict = {self._name: _items}
        return _dict
