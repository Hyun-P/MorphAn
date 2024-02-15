# MorphAn

### Requirements
  * Python 3.8
  * Anaconda
  * FIJI (FIJI Is Just ImageJ)
  * Vaa3D
  * GCut
    * https://www.nature.com/articles/s41467-019-09515-0

## Installation
  * git clone https://github.com/Hyun-P/MorphAn.git
  * cd MorphAn
  * git clone https://bitbucket.org/muyezhu/gcut.git
  * conda env create -f environment.yml

## Background Generation
Background generation algorithm is a multiprocessing algorihtm that uses a iterative process of calculating nonlinear fit models.
The algorithm uses a set of predetermined parameters that are used in controlling acceptable/unacceptable pixel values from the calculated nonlinear fit.
To determine the parameters, open a representative image from a dataset.
Aassess histograms of rows and determine which row would best represent the given image.
The best representing row would be where the variations between foreground and background are large.

For example, in the below image, I would choose the row that crosses the soma of a neuron (highlighted in mint green) because soma's high intensity would greatly skew the nonlinear fit when it calculates.

![microdish_ctx_20x_DIV7_plateA_P3_1---with_overlay_for_bg_gen](https://github.com/Hyun-P/MorphAn/assets/114594534/30cd46bf-d120-4110-8e4e-3d714cb63631)

Note the index of the chosen row, and use that in the code to assess how the nonlinear fit model becomes close to the actual background.

## Background Correction
This notebook simply uses CellProfiler's Illumination Correction plugin in python.
Select a directory of raw images, a directory of generated background images from above, and a directory where you want to save the background corrected images.

## Soma Identification
This process is first completed using FIJI, manually finding positions of somas.
Then, the prepared notebook is used to process data for automated tracing in Vaa3D.

## WEKA
Use FIJI's Trainable Weka Segmentation plugin to segment images.
Three different classes are needed: Background, Soma, and Object (the order matters!).
Since the positions of somas are identified manually, Soma classes merely serves as a placeholder for the further development of this protocol.
Classify backgrounds and objects (aka the whole neuron).
This will generate segmented images with the following pixel values: (ensure this is correct)
  * 0 = background
  * 1 = none
  * 2 = objects
It is paramount to prepare segmented images with the above pixel values for the following processes.

## Vaa3D
You would need to install Vaa3D softare first.
The notebook requires a system path to the softare where the execuable file can be found.

## GCut
This notebook uses GCut algorithm that you cloned during the installation step.
Ensure that you clone GCut inside the MorphAn directory.

## Straightening
Use the prepared macro in FIJI to first extract necessary information from the tracing files in .swc format.
Then, Straightening notebook can be used to further process the extracted data from the macro to generate a reconstructed image of the neuron and its rectified sholl analysis data.

## Post-process
  * Statistical Analysis - Dr. Umed T. Boltaev
