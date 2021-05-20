class TagNotFoundException(Exception):
    def __init__(self, tag):
        super().__init__("Tag {0} does not exist.".format(tag))
        self.errors = "Tag Not Found Exception"
        print(self.errors)
