class Version():
    def __init__(self, sver):
        self.sver = sver
        self.ver_major = 0
        self.ver_minor = 0
        self.ver_patch = 0

        self.setVersion(self.sver)


    def setVersion(self, sver):
        ivers = list(map(int, sver.split('.')))
        self.ver_major = ivers[0]
        try:
            self.ver_minor = ivers[1]
        except IndexError:
            pass
        try:
            self.ver_patch = ivers[2]
        except IndexError:
            pass
        return


    def __str__(self):
        return '.'.join(list(map(str, [self.ver_major, self.ver_minor, self.ver_patch])))


    def __eq__(self, v2):
        if isinstance(v2, str):
            v2 = Version(v2)

        if self.ver_major != v2.ver_major:
            return False
        if self.ver_minor != v2.ver_minor:
            return False
        if self.ver_patch != v2.ver_patch:
            return False
        return True


    def __ne__(self, v2):
        return not self == v2


    def __gt__(self, v2):
        if isinstance(v2, str):
            v2 = Version(v2)

        if self.ver_major > v2.ver_major:
            return True
        elif self.ver_major < v2.ver_major:
            return False
        else:
            if self.ver_minor > v2.ver_minor:
                return True
            elif self.ver_minor < v2.ver_minor:
                return False
            else:
                if self.ver_patch > v2.ver_patch:
                    return True
                else:
                    return False


    def __lt__(self, v2):
        return (not self == v2) and (not self > v2)


    def __ge__(self, v2):
        return not self < v2


    def __le__(self, v2):
        return not self > v2
