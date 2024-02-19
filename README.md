# Robotic Nerve Ultrasound Scanning
### Author:
 Carlo Cagnetta
### Supervisor:
Yordanka Velikova, Vanessa Gonzalez Duque, Felix Dülmer
### External Supervisor:
Michael Panchenko
### Department:
Chair of Computed Aided Medical Prociedures & Augmented Reality \
School of Computation, Information and Technology \
Technical University Munich

---

This repo contains the work of the Master Thesis of the author at the CAMPAR chair at TUM

## Setup
To quickly set up the environment we advice using a conda env.

## Structure

### Image Navigation
This folder contains all code used for 2D image navigation in 3D MRI labels model.

- <b>Notebooks:</b> Used for function development. Contain logic explanation and use examples of functions. Fucntions developed in the Notebooks are then copied into ´´´.py´´´ files soto be re-used.
    - <b>0_mri_visual:</b> How to extract image information from 3D model. Tried scipy interpolation. *OUTDATED*
    - <b>1_simple_clustering:</b> Simple clustering with center-symmetric structure matrix using ```scipy.ndimage.label```.
    Also developed loss function and linear sweep proof of concept.
    - <b>2_DBSCAN_clustering:</b> Better clustering algorithm using DBSCAN, tested on linear sweep loss.
    - <b>3_slicing:</b> Arbitrary linear sweep using simpleITK and euler matrix transformation.
    - <b>4_environment:</b> Showcase of how to get loss from an arbitrary slice.