from json import dumps, loads


class Serializable:
    """ class parent for all serializable objects """
    def _save(self, filename):
        saving_dict = dict()
        for el in self.__dict__:
            try:
                assert (el not in self._filter_fields())
                dumps(self.__dict__[el])
                saving_dict[el] = self.__dict__[el]
            except Exception:
                pass
        with open(filename, 'w') as f:
            f.write(dumps(saving_dict))

    def _load(self, filename):
        with open(filename, 'r') as f:
            self.__dict__ = {**self.__dict__, **loads(f.read())}

    @staticmethod
    def _filter_fields() -> list:
        return []