# School on Quantum Simulation, Milan 9-11 September 2026

## Slides directory

* slides of the course

## Notebooks directory

* hello_world_lagrange_IBM.ipynb (and corresponding py file): introduction to login on both Lagrange and IBM quantum platform. Backend construction in both cases and execution of a simple circuit.

### Jupyter lab

In general, it would be best not to track ipynb notebook files, unless their output is cleared each time before git commit, otherwise the repository is polluted by unnecessary data. By using the jupyter extension jupytext one can automatically generate and update .py files when saving the ipynb files. Then those py files can be git tracked.
```
conda install jupyter jupyterlab jupytext jupyterlab-git
```

After cloning the repository, the first thing to do is to generate the .ipynb notebook from each tracked .py file (e.g. thisfile.py):
```
jupytext --to notebook thisfile.py
```
or, you can simply open the script in Jupyter lab, Open it as a Notebook, and save it. The ipynb is then automatically created and you can open it.

Each time some branch is git-pulled, or a git-checkout is made, it is advised to first open the .py file in jupyter notebook or lab, and save it.

This way the .ipynb notebook is updated and there are no inconsistencies. Then the .py is to be closed and the .ipynb opened.

