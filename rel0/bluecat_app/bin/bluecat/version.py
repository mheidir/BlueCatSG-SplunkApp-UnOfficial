

class version(str):

    def __init__(self, ver):
        """
        Version class that has custom comparators to work with version numbers. Should be given a string of '#.#.#' format.

        :param ver:
        """
        if not ver:
            self._version = '0'
        else:
            self._version = ver


    def __eq__(self, other):
        if not other:
            other = '0'
        my_version = map(int, self.split('.'))
        other_version = map(int, other.split('.'))
        if len(my_version) == len(other_version):
            for i in range(0, len(my_version)):
                if my_version[i] != other_version[i]:
                    return False
            return True
        return False

    def __ne__(self, other):
        if self == other:
            return False
        return True


    def __gt__(self, other):
        """Returns true if this version number is higher than the other version number. Returns false otherwise."""

        if not other:
            other = '0'
        if (self != other):
            my_version = map(int, self.split('.'))
            other_version = map(int, other.split('.'))
            if len(my_version) <= len(other_version):
                for i in range(0, len(my_version)):
                    if my_version[i] > other_version[i]:
                        return True
                    elif my_version[i] < other_version[i]:
                        return False
                return False
            else:
                for i in range(0, len(other_version)):
                    if my_version[i] > other_version[i]:
                        return True
                    elif my_version[i] < other_version[i]:
                        return False
                return True
            return False
        return False

    def __lt__(self, other):
        if self > other or self == other:
            return False
        return True

    def __ge__(self, other):
        if self > other or self == other:
            return True
        return False

    def __le__(self, other):
        if self > other:
            return False
        return True

    def split(self, pattern):
        return self._version.split(pattern)

