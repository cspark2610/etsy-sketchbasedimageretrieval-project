class ThumbnailImage:
    id = 1
    thumbnails = []

    def __init__(self, filename, img, widget):
        self.filename = filename
        self.id = ThumbnailImage.id
        self.img = img
        self.widget = widget
        ThumbnailImage.thumbnails.append(self)
        ThumbnailImage.id += 1

    @classmethod
    def delete_objects(cls):
        for thumb in ThumbnailImage.thumbnails:
            # Using forget cause performance issues after more and more clicking
            thumb.widget.destroy()
        ThumbnailImage.thumbnails = []

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Id: {self.id} Filename: {self.filename}"