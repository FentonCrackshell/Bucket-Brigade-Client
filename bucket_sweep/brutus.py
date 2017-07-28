class Brute(object):

    brute_list = None
    current = None

    def __init__(self, target, brute_list):
        self.brute_list = brute_list
        self.current = target

    @property
    def next(self):
        ret_val = []
        scan_chrs = 0
        try:
            for k in self.current:
                if k == '*':
                    scan_chrs += 1
                else:
                    ret_val.append(self.brute_list.index(k))
        except ValueError:
            raise ValueError("invalid characters in target")
        target = ret_val

        val = [x for x in target]
        mod = len(self.brute_list)
        p = 0
        stepping = True
        try:
            while stepping:
                val[~p] = (val[~p]+1)%mod
                if val[~p] == 0:
                    p += 1
                else:
                    stepping = False
        except IndexError:
            val.insert(0, 0)

        return "".join([self.brute_list[x] for x in val] + ["*" for x in range(scan_chrs)])

    @property
    def previous(self):
        ret_val = []
        scan_chrs = 0
        try:
            for k in self.current:
                if k == '*':
                    scan_chrs += 1
                else:
                    ret_val.append(self.brute_list.index(k))
        except ValueError:
            raise ValueError("invalid characters in target")
        target = ret_val

        val = [x for x in target]
        mod = len(self.brute_list)
        p = len(val)-1
        stepping = True
        step_down = False
        try:
            while stepping:
                val[p] = (val[p]-1)%mod
                if val[p] == mod-1:
                    if p == 0:
                        step_down = True
                    p -= 1
                else:
                    stepping = False
        except IndexError:
            val.insert(0, 0)
        if step_down:
            val.pop()

        return "".join([self.brute_list[x] for x in val] + ["*" for x in range(scan_chrs)])