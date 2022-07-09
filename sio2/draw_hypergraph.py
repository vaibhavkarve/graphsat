#!/usr/bin/env python3.9
"""Testing out HyperNetX package.

- documentation :: https://pnnl.github.io/HyperNetX/build/index.html
"""
import matplotlib.pyplot as plt  # type: ignore
from dat_management import read_dat
from hypernetx import Hypergraph, drawing  # type: ignore

criminals = read_dat('criminals.dat')



"""Writiing to csv so I can visualize a MHGraph using
   http://paovis.ddns.net/paoh.html"""


with open('test.csv', 'w') as writefile:
    for crim_index, crim in enumerate(criminals):
        for e_index, e in enumerate(crim.elements()):
            for v in e:
                writefile.write(f'{e_index + 1},{v},{crim_index+1}\n')


# Creates just a figure and only one subplot
#fig, ax = plt.subplots(10, 5)
#ax.set_title('Minimal unsatisfiable MHGraphs with |V|=6')
fig = plt.figure(tight_layout=True)
for index, c in enumerate(criminals):
    H = Hypergraph(list(c.elements()))
    ax = fig.add_subplot(5, 11, index+1, frame_on=False)
    drawing.rubber_band.draw(H, ax=ax, with_edge_labels=False)
plt.show()


