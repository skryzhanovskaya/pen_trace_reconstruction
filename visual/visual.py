from tkinter import *
from PIL import Image 
from PIL import ImageTk
from functools import partial

from skeleton.skeleton import *
from trace_reconstruction.trace_reconstruction import TraceReconstructor


def close(event, window):
	window.destroy()


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


def write_word(input_path,  skeleton_lib, rate=10):

	skeletons, true_files = build_skeletons(input_path, skeleton_lib)

	for skel, img_path in zip(skeletons, true_files):
		# process image

		img = Image.open(img_path)

		window = Tk()
		window.title(img_path)

		w = window.winfo_screenwidth() // 2

		scale = w / img.size[0]
		h = int(scale * img.size[1])

		img = img.resize((w, h))
		img = ImageTk.PhotoImage(img)

		c = Canvas(window, width=w, height=h)
		c.create_image(0, 0, anchor=NW, image=img)
		c.pack(fill=BOTH, expand=1)

		nodes, edges = process_skeleton(skel)
		trace_reconstructor = TraceReconstructor(nodes, edges)
		stroke_trace, trace = trace_reconstructor.trace()
		skel_graph = trace_reconstructor.skeleton_graph.nx_graph

		node_trace = []
		stroke_names = []

		for i in range(len(trace)):
			cc_stroke_trace, cc_trace = stroke_trace[i], trace[i]
			for stroke in cc_trace:
				node_trace.append([(skel_graph.nodes[v]['x'] * scale, skel_graph.nodes[v]['y']  * scale) for v in stroke])
			stroke_names += [stroke.name for stroke in cc_stroke_trace]

		pt = PrintTrace(node_trace, stroke_names, rate)

		func_print = partial(pt, canvas=c)
		func_close = partial(close, window=window)

		window.bind('<space>', func_print)
		window.bind('<Escape>', func_close)

		window.mainloop()


# input_path = './data/img/'
# write_word(input_path)

