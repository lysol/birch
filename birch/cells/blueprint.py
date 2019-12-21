class BlueprintCell:

    def __init__(self, cls, args=[], kwargs={}):
        self.cls = cls
        self.args = args
        self.kwargs = kwargs

    def update_arg(self, index, arg):
        self.args[index] = arg

    def to_cell(self):
        return self.cls(*self.args, **self.kwargs)
