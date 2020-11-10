import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button, TextBox
from mpl_toolkits.axes_grid1.inset_locator import InsetPosition


class SketchBuilder:

    LINE_COLOR = "black"
    LINE_WIDTH = 1

    def __init__(self, figure, ax):
        self.lines = []   # [line]
        self.figure = figure
        self.ax = ax
        self.xs = []  # list(line.get_xdata())
        self.ys = []  # list(line.get_ydata())
        self.draw = False
        self.cidpress = self.figure.canvas.mpl_connect('button_press_event', self.on_click)
        # self.cidrelease = line.figure.canvas.mpl_connect('button_release_event',  self.on_click)
        self.cidmotion = self.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.x0 = 0
        self.y0 = 0
        self.filename = "test.png"
        self.curr_line, = self.get_empty_line()

    def get_empty_line(self):
        return self.ax.plot([0], [0], color=SketchBuilder.LINE_COLOR, linewidth=SketchBuilder.LINE_WIDTH)

    # We only have to draw the last line
    def render_last_line(self):
        if len(self.lines) == 0:
            return
        line = self.lines[len(self.lines) - 1]

        self.ax.plot(line.get_xdata(), line.get_ydata(), color=SketchBuilder.LINE_COLOR, linewidth=SketchBuilder.LINE_WIDTH)
        # for line in self.lines:
        # line.figure.canvas.draw()
        self.figure.canvas.draw()

    def render_all_lines(self):
        self.ax.cla()
        self.ax.set_title('Lamp Sketch')
        self.ax.set_autoscaley_on(False)
        self.ax.set_autoscalex_on(False)
        for ln in self.lines:
            ax.plot(ln.get_xdata(), ln.get_ydata(), color=SketchBuilder.LINE_COLOR, linewidth=SketchBuilder.LINE_WIDTH)
        self.figure.canvas.draw()
        # For some reason this line is critical to allow drawing to resume
        self.curr_line, = self.get_empty_line()

    def on_click(self, event):
        # print('mouse down', event)
        if event.inaxes is not None and event.inaxes != self.ax:
            return
        self.draw = not self.draw

        if self.draw:
            self.x0 = event.xdata
            self.y0 = event.ydata
            x_values = [self.x0]
            y_values = [self.y0]
            self.xs.extend(x_values)
            self.ys.extend(y_values)
        else:
            self.lines.append(self.curr_line)
            self.curr_line, = self.get_empty_line()
            self.xs = []
            self.ys = []

    def on_motion(self, event):
        # print('motion event', event)
        if event.inaxes is not None and event.inaxes != self.ax:
            return
        if self.draw:
            # Note that the current line doesn't have to be explicitly rendened - it just draws itself with the mouse!
            x_values = [self.x0, event.xdata]
            y_values = [self.y0, event.ydata]
            self.xs.extend(x_values)
            self.ys.extend(y_values)
            self.curr_line.set_data(self.xs, self.ys)
        self.x0 = event.xdata
        self.y0 = event.ydata

    # Not currently used
    def button_release(self, event):
        print("in button release")


    def save(self, event):
        # Only the contents within the axes
        extent = self.ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        self.figure.savefig(self.filename, format="png", bbox_inches=extent)
        print(f"Saved to file: {self.filename}")

    def undo(self, event):
        if len(self.lines) > 0:
            self.lines = self.lines[:-1]
            print(f"Num lines after undo: {len(self.lines)}")
            self.render_all_lines()

    def submitFilename(self, text, textbox):
        # If filename doesn't end with .png suffix it as such
        if not text.lower().endswith('.png'):
            text = text + ".png"
            textbox.set_val(text)
        self.filename = text
        print(f"Filename: {self.filename}")


# The second axis is to make space for the buttons indirectly. Bit hacky but couldn't find a better way
fig, (ax, axcut) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [9, 1]}, figsize=(6, 6))

axcut.axis('off')
ax.set_title('Lamp Sketch')

ax.set_autoscaley_on(False)
ax.set_autoscalex_on(False)
linebuilder = SketchBuilder(fig, ax)

# Put the buttons in a separate subplot
# ip = InsetPosition(ax, [0, 0, 0.2, 1.0]) #posx, posy, width, height
# axcut.set_axes_locator(ip)
bundo_ax = plt.axes([0.1, 0.1, 0.08, 0.08])
bundo = Button(bundo_ax, 'Undo', color='gray', hovercolor='darkgray')
bsave_ax = plt.axes([0.2, 0.1, 0.08, 0.08])
bsave = Button(bsave_ax, 'Save', color='gray', hovercolor='darkgray')
textbox_ax = plt.axes([0.3, 0.1, 0.2, 0.08])
text_box = TextBox(textbox_ax, '', initial=linebuilder.filename)
text_box.on_submit(lambda val: linebuilder.submitFilename(val, text_box))
bsave.on_clicked(linebuilder.save)
bundo.on_clicked(linebuilder.undo)
plt.show()
