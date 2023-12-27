# Mito-ANFs

## 1. Install dependency library (GPU: TITAN RTX 24G Memory)
Pytorch==1.10.1+cu111<br/>
Torchvision==0.11.2+cu111<br/>
Python==3.9.12<br />
NumPy==1.21.6<br />
h5py==3.8.0<br />

## 2. Dataset
Two mid-cochlea datasets at the spatial resolution of 12 × 12 × 50 $nm^3$ (dataset-1: 60 × 55 × 42 $μm^3$, dataset-2: 88 × 46 × 60 $μm^3$) 

## 3. Model (mitochondria segmentation)
![image](picture/network.png)
The model was based on the residual 3D U-Net architecture.

Model parameter: [weight](https://pan.baidu.com/s/1ygFEJoowlZb588PJW9iMRw), code:mito

## 4. Measurement
The volume of mitochondria is the sum of voxels. ANF-associated mitochondria were divided into super voxels with a unit volume of (0.07 $μm^3$) along the longest axis (code).
