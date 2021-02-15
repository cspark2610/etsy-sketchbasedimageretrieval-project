class Outline:
    id = 1
    clusters = {}
    frame = None
    canvas = None

    def __init__(self):
        pass

    # Reset the scrollbar to the top, assumes the parent widget is a canvas with a scrollbar
    @classmethod
    def scroll_to_top(cls):
        Outline.canvas.yview_moveto('0.0')

    @classmethod
    def set_clusters(cls, images_clusters):
        Outline.clusters = images_clusters

    @classmethod
    def get_clusters(cls):
        return Outline.clusters

    @classmethod
    def set_frame(cls, frame):
        Outline.frame = frame

    @classmethod
    def get_frame(cls):
        return Outline.frame

    @classmethod
    def set_canvas(cls, canvas):
        Outline.canvas = canvas

    @classmethod
    def get_canvas(cls):
        return Outline.canvas

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Id: {id} "
