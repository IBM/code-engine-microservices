class ItemNotFoundException(Exception):
    def __init__(self, id):
        super().__init__("{0} Not found in DB".format(id))
        self.errors = "Item Not Found Exception"
        print(self.errors)
