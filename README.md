# Mito-ANFs

## 1. Install dependency library (GPU: TITAN RTX 24G Memory)
Pytorch==1.10.1+cu111<br/>
Torchvision==0.11.2+cu111<br/>
Python==3.9.12<br />
NumPy==1.21.6<br />
h5py==3.8.0<br />

## 2. Dataset
Two mid-cochlea datasets at the spatial resolution of 12 × 12 × 50 $nm^3$ (dataset-1: 60 × 55 × 42 $μm^3$, dataset-2: 88 × 46 × 60 $μm^3$) 

[Two training datasets](https://pan.baidu.com/s/1pF2snx4IPPwlRptBL8spkg), each consisting of 1536 × 1536 × 100 voxels.


## 3. Model (mitochondria segmentation)
### Model architecture
![image](picture/network.png)
The model was based on the residual 3D U-Net architecture (Lee et al., 2017). The model code can be downloaded by [pytorch_connectomics](https://github.com/zudi-lin/pytorch_connectomics).
### Train
`python -u main.py --config-base configs/MitoEM/MitoEM-R-Base.yaml --config-file configs/MitoEM/MitoEM-R-BC.yaml`

Model parameter: [Weight](https://onedrive.live.com/?id=F64849A5930EAEE7%21s1c74574f0d234187baf57bf1a1d11028&cid=F64849A5930EAEE7) (latest)
### Inference
`python -u main.py --config-base configs/MitoEM/MitoEM-R-Base.yaml --config-file configs/MitoEM/MitoEM-R-BC.yaml --inference --checkpoint datasets/output/checkpoint_200000.pth.tar`



## 4. Measurement
The volume of mitochondria is the sum of voxels. ANF-associated mitochondria were divided into super voxels with a unit volume of (0.07 $μm^3$) along the longest axis (see code).

## 5. References
Lee, K., Zung, J., Li, P.H., Jain, V., and Seung, H.S. (2017). Superhuman Accuracy on the SNEMI3D Connectomics Challenge. ArXiv abs/1706.00120. <br />
Wei, D., Lin, Z., Franco-Barranco, D., Wendt, N., Liu, X., Yin, W., Huang, X., Gupta, A., Jang, WD., Wang, X., Arganda-Carreras, I., Lichtman, JW., and Pfister, H. (2020). MitoEM Dataset: Large-scale 3D Mitochondria Instance Segmentation from EM Images. Med Image Comput Comput Assist Interv. 12265: 66-76. <br />
Lin, Z., Wei, D., Lichtman, J.W., & Pfister, H. (2021). PyTorch Connectomics: A Scalable and Flexible Segmentation Framework for EM Connectomics. ArXiv, abs/2112.05754.

## Citation
For a detailed description, please read this [paper](https://link.springer.com/article/10.1007/s10162-024-00957-y). If you use the method in your research, please cite:  
Lu, Y., Jiang, Y., Wang, F. et al. Electron Microscopic Mapping of Mitochondrial Morphology in the Cochlear Nerve Fibers. JARO 25, 341–354 (2024). https://doi.org/10.1007/s10162-024-00957-y
