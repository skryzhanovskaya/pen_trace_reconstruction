# Pen Trace Reconstruction
This repo contains the source code for the paper [`Pen Trace Reconstruction with Skeleton Representation of a Handwritten Text Image`](http://ceur-ws.org/Vol-2744/paper27.pdf).

## Usage

#### Step 1: skeleton representation

```bash
skeleton_graph = SkeletonGraph(nodes, edges)
```

#### Step 2: building skeleton meta graph

```bash
meta_graph = MetaGraph(skeleton_graph)
```
#### Step 3: pen trace reconstruction

```bash
trace_reconstructor = TraceReconstructor(skeleton_graph, meta_graph)
trace = trace_reconstructor.trace()
```

## Interactive visualization
![vis](https://github.com/skryzhanovskaya/pen_trace_reconstruction/blob/master/vis.gif)

```bash
python visual.py --images-path IMAGES_PATH --skeletons-path SKELETONS_PATH
```
* `IMAGES_PATH` is the directory with binary images in `png` or `bmp` format (ex: `./data/russian_words/images/`)
* `SKELETONS_PATH` is the directory with corresponding skeletons in `txt` format (ex: `./data/russian_words/skeletons/`)

    Each file with a skeleton contains 4 space-separated float values x1, y1, x2, y2 on a line
            describing an edge between vertices with coordinates (x1, y1) and (x2, y2).
## Citation

```bibtex
@article{pentracereconstruction2020,
author = {Kryzhanovskaya, Svetlana and Arseev, Sergey and Mestetskiy, Leonid},
year = {2020},
month = {12},
pages = {paper27-1},
title = {Pen Trace Reconstruction with Skeleton Representation of a Handwritten Text Image},
journal = {Proceedings of the 30th International Conference on Computer Graphics and Machine Vision (GraphiCon 2020). Part 2},
doi = {10.51130/graphicon-2020-2-3-27}
}
```


 
