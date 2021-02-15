class TileIcon:
    id = 1
    tiles = []

    def __init__(self, filename, img):
        self.filename = filename
        self.id = TileIcon.id
        self.img = img
        TileIcon.tiles.append(self)
        TileIcon.id += 1

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Id: {self.id} Filename: {self.filename}"
