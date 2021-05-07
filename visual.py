import argparse
import os

from tkinter import *
from PIL import Image
from PIL import ImageTk
from functools import partial

from utils import process_skeleton
from trace_reconstruction import TraceReconstructor


def _exit(window):
	window.destroy()
	exit()


def close(window):
	window.destroy()


def center_window(window, width=300, height=200):
	screen_width = window.winfo_screenwidth()
	screen_height = window.winfo_screenheight()

	x = (screen_width/2) - (width/2)
	y = (screen_height/2) - (height/2)
	window.geometry('+%d+%d' % (x, y))


class PrintTrace:
	def __init__(self, trace, strokes, rate):
		self.cur_stroke = 0
		self.cur_idx = 0
		self.trace = trace
		self.strokes = strokes
		self.rate = rate

	def __call__(self, event, canvas):
		if self.cur_stroke < len(self.trace):
			trace = self.trace[self.cur_stroke][self.cur_idx:self.cur_idx + self.rate]

			if self.strokes[self.cur_stroke] == 'simple':
				color = 'red'
			elif self.strokes[self.cur_stroke] == 'cyclic':
				color = 'blue'
			elif self.strokes[self.cur_stroke] == 'vertical':
				color = 'green'
			elif self.strokes[self.cur_stroke] == 'semivertical':
				color = 'yellow'

			canvas.create_line(*trace, fill=color, width=2.5)

			if self.cur_idx + self.rate >= len(self.trace[self.cur_stroke]):
				self.cur_stroke += 1
				self.cur_idx = 0
			else:
				self.cur_idx += self.rate - 1


def build_trace(skeleton_path, scale):
	nodes, edges = process_skeleton(skeleton_path)
	trace_reconstructor = TraceReconstructor(nodes, edges)
	stroke_trace, trace = trace_reconstructor.trace()
	skeleton_graph = trace_reconstructor.skeleton_graph.nx_graph

	node_trace = []
	stroke_names = []

	for i in range(len(trace)):
		cc_stroke_trace, cc_trace = stroke_trace[i], trace[i]
		for stroke in cc_trace:
			node_trace.append(
				[(skeleton_graph.nodes[v]['x'] * scale, skeleton_graph.nodes[v]['y'] * scale) for v in stroke])
		stroke_names += [stroke.name for stroke in cc_stroke_trace]

	return node_trace, stroke_names


def print_words(images_path, skeletons_path, rate=10):

	if os.path.isdir(images_path):
		imgs = [os.path.join(images_path, f) for f in os.listdir(images_path) if f[-4:] == '.png' or f[-4:] == '.bmp']
	else:
		imgs = [images_path]

	for img_path in imgs:
		img = Image.open(img_path)

		# create window
		window = Tk()
		window.title(img_path)

		w = window.winfo_screenwidth() // 2

		scale = w / img.size[0]
		h = int(scale * img.size[1])

		img = img.resize((w, h))
		img = ImageTk.PhotoImage(img)

		center_window(window, w, h)

		c = Canvas(window, width=w, height=h)
		c.create_image(0, 0, anchor=NW, image=img)
		c.pack(fill=BOTH, expand=1)

		# process skeleton
		base = os.path.basename(img_path)
		img_name, _ = os.path.splitext(base)
		skeleton_path = os.path.join(skeletons_path, img_name + '.txt')
		node_trace, stroke_names = build_trace(skeleton_path, scale)

		pt = PrintTrace(node_trace, stroke_names, rate)

		func_print = partial(pt, canvas=c)
		func_close = partial(close, window=window)
		func_exit = partial(_exit, window=window)

		Button(window, text="Close", command=func_exit).pack(side=RIGHT, padx=5, pady=5)
		Button(window, text="Next", command=func_close).pack(side=RIGHT)
		window.bind('<space>', func_print)

		window.mainloop()


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('--images-path', required=True)
	parser.add_argument('--skeletons-path', required=True)
	parser.add_argument('--rate', default=10, required=False)
	args = parser.parse_args()
	print_words(args.images_path, args.skeletons_path, args.rate)
