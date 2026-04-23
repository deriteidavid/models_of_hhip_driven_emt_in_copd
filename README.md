This repository contains code to reproduce the key results of our paper entitled: <br>
# HHIP’s Dynamic Role in Epithelial Wound Healing Reveals a Potential Mechanism of COPD Susceptibility
available on bioRxiv: https://www.biorxiv.org/content/10.1101/2024.09.05.611545v1.abstract 

## Abstract 
Genetic variants near HHIP have been consistently associated with increased risk for Chronic Obstructive Pulmonary Disease (COPD), the third leading cause of death worldwide. However, HHIP’s role in COPD pathogenesis remains elusive. Canonically, HHIP is a negative regulator of the Hedgehog pathway and downstream GLI1 and GLI2 activation. The Hedgehog pathway plays an important role in wound healing, specifically in activating transcription factors that drive the epithelial mesenchymal transition (EMT), which in its intermediate state (partial EMT) is necessary for the collective movement of cells closing a wound. Herein, we use a systems biology approach to propose a mechanism to explain HHIP’s role in faulty epithelial wound healing, which could contribute to the development of emphysema, a key feature of COPD. Using two different Boolean models, we show dysfunctional HHIP results in a lack of negative feedback on GLI, triggering a full EMT, where cells become mesenchymal and do not properly close the wound. We validate these Boolean models with experimental evidence gathered from published scientific literature. Finally, we show evidence supporting our hypothesis in single-cell and single-nucleus RNA-Seq data from different COPD cohorts and Hhip heterozygous knockout mice. Overall, our analyses suggest that aberrant wound healing due to dysfunctional HHIP, combined with chronic epithelial damage through cigarette smoke exposure, may be a primary cause of COPD-associated emphysema.

## Significance Statement
COPD is one of the deadliest diseases worldwide. Genetic and functional studies indicate that the gene HHIP is associated with COPD susceptibility but its role in the disease is unknown. In this work we use network modeling to propose a mechanism for COPD susceptibility by showing how HHIP dysfunction can cause aberrant wound healing in the lung. We demonstrate the validity of our proposed mechanism and show evidence of it in lung gene expression data collected from human subjects and mice. Current treatments for COPD are limited partially because the disease mechanisms are not fully understood. The models presented in this paper may be an important step in understanding a COPD mechanism and provide insights for potential new therapies. 

## python libraries used:
* BooleanNet: https://github.com/ialbert/booleannet 
* Boolean2PEW: https://github.com/deriteidavid/boolean2pew
* Cubewalkers: https://github.com/jcrozum/cubewalkers  (requires Nvidia GPU and cuda)
* AEON.py: https://github.com/sybila/biodivine-aeon-py
* pystablemotifs: https://github.com/jcrozum/pystablemotifs  

## Documentation
This section describes how to reproduce each figure/result from our paper. 
* For Figures 5, S3, S4, S5, S6, S7, S5 you'll need to install the Haskell software *dynmod* available at https://github.com/Ravasz-Regan-Group/dynmod.
* Figure 6 uses data that is publicly available but it's not uploaded to this repository.
* The → in the table represents *code* → *generated output file*
* Unless otherwise specified the code should be ran using Jupyter Notebook or IPython
* It is sufficient to run each unique *dynmod* command only once, it will generate all the necessary files.

|Figure | How to reproduce | Final figure location| 
|---|---|---|
| Figure 1 | https://www.biorender.com/; License and invoice location: /Paper_Figures/Fig1_biorender_license/ |/Paper_Figures/Figure 1.png(pdf.) |
|Figure 2|Figure1_automation.ipynb → /models_of_hhip_driven_emt_in_copd/figures/Figure1_raw.graphml; <br> manually edited using yED (3.21) based on data compiled in Supplementary Table 1 (interactions); <br> Edited graphml location: /network_figures/Figure1.graphml; | /Paper_Figures/Figure1.png(.pdf) |
|Figure 3|HHIP_EMT_dynamical_figures_Figure3.ipynb → /models_of_hhip_driven_emt_in_copd/figures/Figure3.png(.pdf) |/Paper_Figures/Figure3.png(.pdf)|
|Figure 4| within dynmod_model/ run:  *dynmod COPD_EMT_CellCycle_Apoptosis.dmms -g* → dynmod_model/COPD_EMT_CellCycle_Apoptosis.gml <br> manually edited using yED (3.21) and Keynote;<br>files location: /network_figures/Figure4/*|/Paper_Figures/Figure4.png (.pdf, .key)|
|Figure 5| within dynmod_model/ run:  *dynmod COPD_EMT_CellCycle_Apoptosis.dmms -e COPD_Figures.vex* → <br> **A**: dynmod_model/_EXP/General_Time_Series/Fig_4A_WT_AV_short/NodeTC/bc12101221211_Fig_4A_WT_AV_short.pdf <br> **B**: dynmod_model/_EXP/General_Time_Series/Fig_4B_HHIP_Haplo_AV_short/NodeTC/bc12101221211_Fig_4B_HHIP_Haplo_AV_short.pdf <br> **C**: dynmod_model/_EXP/General_Time_Series/Fig_4C_WT_Time/PhBCh/bc12101221211_Fig_4C_WT_Time.pdf (top middle panel)<br>dynmod_model/_EXP/General_Time_Series/Fig_4C_HHIP_Haplo_Time/PhBCh/bc12101221211_Fig_4C_HHIP_Haplo_Time.pdf (top middle panel)<br>dynmod_model/_EXP/General_Time_Series/Fig_4C_HHIP_KO_Time/PhBCh/bc12101221211_Fig_4C_HHIP_KO_Time.pdf (top middle panel)<br> manually cropped for manuscript | /Paper_Figures/Figure5.pdf
|Figure 6| **Data not uploaded to repository.** <br> COPD Atlas Data (single cell RNA-Seq) is available at  https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE136831. <br>  **A**: /RNA_Seq_analysis/COPDAtlas_single_cell_analysis.ipynb → /RNA_Seq_analysis/figures/Figure6A.png <br> **B**: Analysis done in a separate R repository, please contact authors for more details | /Paper_Figures/Figure6.png (.pdf)<br>
