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

## Folder Structure
```bash
~/{dataset}
    | orig/ # original raw images
        | image1.tif # an example image
    | images_background/ # background images generated from generate_background.ipynb
    | images_background_corrected/ # background corrected images generated from correct_background.ipynb
    | weka/ # weka generated binary images from Fiji Weka plugin
    | vaa3d/ # soma_identification.ipynb file prepares images and soma positions in this directory and vaa3d.ipynb generates .swc files into ~/gcut/ directory
        | image1/
            | image1.tif # weka image flipped for vaa3d
            | image1.tif_ini.swc # ignore
            | image1_each_1.txt # soma position with index 1
            | image1_each_1.swc # vaa3d output for a possible neuron1 
            | image1_each_2.txt # another soma position with index 2
            | image1_each_2.swc # vaa3d output for a possible neuron2 
    | gcut/ # gcut.ipynb separates and filters the swc files into ~/trace/ directory
        | image1/
            | image1_each1/
                | image1_each_1_soma=1.swc
                | image1_each_1_soma=2.swc
            | image1_each_1.swc # vaa3d output for a possible neuron 1
            | image1_each_1_soma_ind_fixed.txt # two or more cell bodies' positions in x and y                
    | trace/ # Fiji macro pre_straightening.py processes files in this directory
    | swc_paths_data/
    | tree_data/
    | ROI_to_be_straightened/
    | reconstruction/
    | sholl/
    | sholl.csv
    | Results.csv
    | Log.txt       
```

## HOW_TO
($conda activate morphan)
1. create a dataset directory with a name such as "EXP_1"
2. create a directory "orig" and prepares raw images in .tif format and place them into the directory
3. run background_generation.ipynb with the paths specified for images_dir=~/EXP_1/orig and output_dir=~/EXP_1/images_background
4. run background_correction.ipynb with paths specified for images_dir, background_dir, and output_dir
5. manually idenfity soma positions using FIJI and run soma_identification.ipynb with the paths specified inside the notebook
6. Segment the background corrected images using FIJI's Weka plugin and place them in ~/weka directory
7. run vaa3d.ipynb
8. run gcut.ipynb
9. run pre_straightening.py in Fiji macro with ~/trace file selected
10. run straightening.ipynb for the final analysis

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
1. Use the prepared macro in FIJI to first extract necessary information from the tracing files in .swc format in /trace folder.
2. Then, Straightening notebook can be used to further process the extracted data from the macro to generate a reconstructed image of the neuron and its rectified sholl analysis data.

## Post-process
  * Statistical Analysis - Dr. Umed T. Boltaev
