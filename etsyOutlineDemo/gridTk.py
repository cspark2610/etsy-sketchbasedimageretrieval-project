import os

from tkinter import Tk, Image, PhotoImage, Canvas, Label, Frame, W, E, N, S
import tkinter.ttk as ttk
from tkinter.ttk import Scrollbar
from os import listdir, path
from os.path import isfile, join
import glob

from thumbnailimage import ThumbnailImage
from tile_icon import TileIcon
from PIL import Image as PILImage
from PIL import ImageTk

from outline import Outline

NUM_OUTLINE_COLS = 2
NUM_IMAGE_COLS = 4
NUM_COLS = NUM_IMAGE_COLS + NUM_OUTLINE_COLS
IMAGE_WIDTH = 230
IMAGE_HEIGHT = 230  # 180

WINDOW_WIDTH = 1330  # This is the width of the Etsy header bar
LHS_WIDTH = 300
RHS_WIDTH = WINDOW_WIDTH - LHS_WIDTH
SHOW_IMAGE_NOS = False

IMAGE_FOLDER = "./lampshades_images/il"
OUTLINE_FOLDER = "./images/Outlines"

global images_clusters
global frame_rhs


def monitor_height(root):
    h = root.winfo_screenheight()
    return h


def resize(img, new_width, new_height):
    # percent by which the image is resized

    if new_width is None:
        new_width = 512
    w, h = img.size

    scale_h_percent = new_height / h
    scale_w_percent = new_width / w
    scale_percent = min(scale_h_percent, scale_w_percent)

    # calculate the scale percent of original dimensions
    new_width = int(w * scale_percent)
    new_height = int(h * scale_percent)

    print(
        f"Org width: {w} Org height: {h} Scale percent: {scale_percent} new_width: {new_width} new_height: {new_height}")

    maxsize = (new_width, new_height)
    img.thumbnail(maxsize, PILImage.ANTIALIAS)
    return img


def get_files_in_folder(path, suffix):
    """ suffix is optional"""
    onlyfiles = []
    listing = listdir(path)
    for file in listing:
        if isfile(join(path, file)) and (not suffix or file.endswith(suffix)):
            onlyfiles.append(file)
    return onlyfiles


def display_outlines(frame, outline_dir, tiles_per_col, num_cols, Outline):
    TILE_WIDTH = 128
    onlyfiles = get_files_in_folder(outline_dir, '.jpg')
    onlyfiles = sorted(onlyfiles, reverse=True)
    print(f"Files: {onlyfiles}")
    tiles = []

    i = 0
    col = 0
    for img_file in onlyfiles:
        col = i % num_cols
        row = i // num_cols
        print(f"i: {i} row: {row} col: {col}")
        if col >= num_cols:
            break

        im = PILImage.open(outline_dir + "/" + img_file)
        maxsize = (TILE_WIDTH, TILE_WIDTH)
        im.thumbnail(maxsize, PILImage.ANTIALIAS)
        imgtk = ImageTk.PhotoImage(im)

        # photo = PhotoImage(file='lena.png')

        label = Label(frame, image=imgtk, bg="white")
        tile = TileIcon(img_file, imgtk)
        print(f"Created tile: {tile}")

        label.grid(column=col, row=row)
        eval_link = lambda tile, outlines: (lambda event: outline_clicked(tile, outlines, event))
        label.bind("<Button-1>", eval_link(tile, Outline))
        tiles.append(tile)
        i += 1
    return tiles


def add_tile_to_frame(frame, img_file):
    if not path.exists(img_file):
        print(f"File doesn't exist: {img_file}")
        return
    im = PILImage.open(img_file)
    # im = im.resize((IMAGE_WIDTH, IMAGE_WIDTH))
    imgtk = ImageTk.PhotoImage(im)
    label = Label(frame, image=imgtk, bg="white")
    tile = TileIcon(img_file, imgtk)
    label.grid(column=0, row=0)


# Images are destroyed when the frame is repopulated
def add_image_to_frame(frame, img_file, row, col, colspan=1):
    if not path.exists(img_file):
        print(f"File doesn't exist: {img_file}")
        return
    im = PILImage.open(img_file)
    # im = im.resize((IMAGE_WIDTH, IMAGE_WIDTH))
    imgtk = ImageTk.PhotoImage(im)
    label = Label(frame, image=imgtk, bg="white")
    ThumbnailImage(img_file, imgtk, label)
    label.grid(column=col, row=row, sticky=N, padx=0, pady=0, columnspan=colspan)


def display_images(frame, images, images_per_col, num_cols, show_image_nos: bool, clear_cache: bool):
    num_not_exists = 0
    num_cached = 0
    num_saved = 0

    add_image_to_frame(frame, 'etsyFrame/etsy-num-results.png', 0, 0, num_cols)
    i = num_cols
    col = 0
    for img_file in images:
        img_file = img_file.replace('/root/Etsy-sov/SBIR_regression/', './', 1)
        col = i % num_cols
        row = i // num_cols
        # print(f"i: {i} row: {row} col: {col}")
        if col >= num_cols:
            break

        (filename, ext) = os.path.splitext(img_file)
        thumb_file = filename + "-thumb" + ext
        if not clear_cache and path.exists(thumb_file):
            num_cached += 1
            im = PILImage.open(thumb_file)
        elif not path.exists(img_file):
            num_not_exists += 1
            continue
        else:
            im = PILImage.open(img_file)
            im = resize(im, IMAGE_WIDTH, IMAGE_HEIGHT)
            im.save(thumb_file, "JPEG")
            num_saved += 1

        imgtk = ImageTk.PhotoImage(im)

        if show_image_nos:
            label = Label(frame, text=f"{i + 1}", image=imgtk, compound='top', bg="white")
        else:
            label = Label(frame, image=imgtk, bg="white")
        thumb_image = ThumbnailImage(img_file, imgtk, label)

        label.grid(column=col, row=row, padx=5, pady=5, sticky='S')
        i += 1

    print(f"Num read from cache: {num_cached} num saved: {num_saved} num missing: {num_not_exists}")


def outline_clicked(tile, outline, event):
    print(f"clicked at {event.x}, {event.y}")
    print(f"tile: {tile}")
    ThumbnailImage.delete_objects()
    num_images_per_col = round(len(images_clusters[tile.filename]) / NUM_IMAGE_COLS)
    print(f"Num images per col: {num_images_per_col}")
    frame_rhs = outline.get_frame()
    clusters = outline.get_clusters()
    display_images(frame_rhs, clusters[tile.filename], num_images_per_col, NUM_IMAGE_COLS, SHOW_IMAGE_NOS, False)
    outline.scroll_to_top()


def read_outline_json():
    import json

    with open('outline_dict.json') as f:
        data = json.load(f)
    # print("In read_outline_json")
    # for k in data.keys():
    # print(f"key: {k} num images: {len(data[k])}")
    # print("End of read_outline_json")
    return data


def onFrameConfigure(canvas):
    '''Reset the scroll region to encompass the inner frame'''
    canvas.configure(scrollregion=canvas.bbox("all"))
    canvas.configure(background="white")


def scroll_arrow(canvas, event):
    if event.keysym == 'Up':
        canvas.yview_scroll(-1, "units")
    elif event.keysym == 'Down':
        canvas.yview_scroll(1, "units")


def scroll_mouse_wheel(canvas, event):
    # This is hard-coded to Apple's "natural" scroll
    if event.delta < 0:
        canvas.yview_scroll(1, "units")
    else:
        canvas.yview_scroll(-1, "units")


def create_frame_with_scroll(parent_widget, grid_col, grid_row, width, height):
    # Initialize style
    s = ttk.Style()
    # Create style used by default for all Frames
    s.configure('TFrame', background='blue')

    scroll_units = 25  # Number of pixels to scroll frame up or down
    canvas = Canvas(parent_widget, borderwidth=0, width=width, height=height, background="white")
    content = Frame(canvas, bg="white", highlightbackground="white", highlightcolor="white")
    vsb = Scrollbar(parent_widget, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set)
    canvas.configure(yscrollincrement=scroll_units)
    canvas.configure(background="white")
    eval_link = lambda canvas: (lambda event: scroll_arrow(canvas, event))
    eval_link_wheel = lambda canvas: (lambda event: scroll_mouse_wheel(canvas, event))
    canvas.bind_all("<Up>", eval_link(canvas))
    canvas.bind_all("<Down>", eval_link(canvas))
    canvas.bind_all("<MouseWheel>", eval_link_wheel(canvas))

    # canvas.bind("<Up>", lambda event: canvas.yview_scroll(-1 * event.delta, "units"))
    # canvas.bind("<Down>", lambda event: canvas.yview_scroll(1 * event.delta, "units"))

    # vsb.pack(side="right", fill="y")
    # canvas.pack(side="left", fill="both", expand=True)
    canvas.grid(column=grid_col, row=grid_row, sticky='NSEW')
    vsb.grid(column=grid_col + 1, row=grid_row, sticky='NS')

    canvas.create_window((0, 0), window=content, anchor="nw")
    content.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))
    return content, canvas


def main():
    global images_clusters
    global frame_rhs

    root = Tk()
    root.title("Etsy")
    root.configure(background="white")
    # style configuration
    style = ttk.Style(root)
    style.configure('TLabel', background='white')
    style.configure('TFrame', background='white')

    screen_height = monitor_height(root)
    WINDOW_HEIGHT = screen_height - 130
    print(f"Screen height: {screen_height} window height: {WINDOW_HEIGHT}")

    if False:
        image_files = glob.glob(IMAGE_FOLDER + "/*/*/*.jpg")
        print(f"Found {len(image_files)}")
        print(image_files[0], image_files[550])

    dpi_value = root.winfo_fpixels('1i')
    print(f"Default dpi: {dpi_value}")
    # dpi_value = 400
    # root.tk.call('tk', 'scaling', '-displayof', '.', dpi_value / 72.0)
    root.tk.call('tk', 'scaling','-displayof', '.', 4.0)
    # root.maxsize(1500, 400)
    root.grid_rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    # content = Frame(root, bg="white", borderwidth=0, highlightbackground="white", highlightcolor="white")
    content, canvas = create_frame_with_scroll(root, 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

    etsy_top_frame = Frame(content, borderwidth=0, width=RHS_WIDTH, height=200, bg="white")
    frame_lhs = ttk.Frame(content, borderwidth=0, width=LHS_WIDTH, height=400)
    # frame_lhs = create_frame_with_scroll(content, 0, 1, LHS_WIDTH, WINDOW_HEIGHT)
    frame_lhs_outlines = Frame(frame_lhs, bg="white", borderwidth=0)
    etsy_lhs_frame = Frame(frame_lhs, borderwidth=0, highlightbackground="white", highlightcolor="white",
                           width=LHS_WIDTH, height=200, bg="white")

    # frame_rhs = create_frame_with_scroll(content, 2, 1, RHS_WIDTH, WINDOW_HEIGHT)
    frame_rhs = Frame(content, bg="white")

    # This commented line screws up the scrolling
    # content.grid(column=0, row=0)
    etsy_top_frame.grid(column=0, row=0, columnspan=5, sticky='NW')
    frame_lhs.grid(column=0, row=1, padx=0, pady=0, sticky='N')
    frame_lhs_outlines.grid(column=0, row=1, sticky=N+S+E+W)
    etsy_lhs_frame.grid(column=0, row=0, sticky='N')
    frame_rhs.grid(column=2, row=1, sticky='N')

    num_outlines = len(get_files_in_folder(OUTLINE_FOLDER, '.jpg'))
    num_outlines_per_col = round(num_outlines / NUM_OUTLINE_COLS)
    print(f"Num outlines per col: {num_outlines_per_col}")

    images_clusters = read_outline_json()
    Outline.set_canvas(canvas)
    Outline.set_clusters(images_clusters)
    Outline.set_frame(frame_rhs)
    display_outlines(frame_lhs_outlines, OUTLINE_FOLDER, num_outlines_per_col, NUM_OUTLINE_COLS, Outline)

    add_tile_to_frame(etsy_top_frame, 'etsyFrame/topFrame.png')
    add_tile_to_frame(etsy_lhs_frame, 'etsyFrame/Etsy-Filter-version2.png')
    add_image_to_frame(frame_rhs, 'etsyFrame/etsy-num-results.png', 0, 0)
    add_image_to_frame(frame_rhs, 'etsyFrame/1st-background-small.png', 1, 0)
    add_image_to_frame(frame_rhs, 'etsyFrame/2nd-background-small.png', 2, 0)
    add_image_to_frame(frame_rhs, 'etsyFrame/3rd-background-small.png', 3, 0)
    add_image_to_frame(frame_rhs, 'etsyFrame/4th-background-small.png', 4, 0)
    # display_images(frame_rhs, images_clusters['outline21.jpg'], 15, 4)

    root.mainloop()


main()
