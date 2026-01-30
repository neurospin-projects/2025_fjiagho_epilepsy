This folder is constitued of two repositories "epilepsy_PBS" and "PEPR_Marseille", representing the two epileptic datasets that I used, and a file 
"mask_interrupted_cs.csv", presenting for all the subjects in UKB, if he has an interrupted central sulcus or not. 

# epilepsy_PBS

The folder "epilepsy_PBS" contains the results with the dataset "epilepsy_PBS". It is composed by many subfolders:

* In "CCD", we try to reproduce the results of
Louise Guillon with training the beta-VAE on HCP and testing it on CCD.

* In the repository "ABCD", there are the results when training the beta-VAE on ABCD.

In all the others subfolders, it is when training on UKB. 

* In "SC-sylv_right_UKB_16-20-03_123", we have the output files when training the beta-VAE on the
right central sulcus of UKB. 

* In the folder "epilepsyPBS", there are the results(cross entropy and UMAP) when training the model on some regions.

* In the repository "age_side_epilepsyPBS", the goal is to plot the reconstruction error in epilepsy_PBS as a function of the age of the subjects. 

* In addition, in the folder "Z-score", the goal was to compute the Z-score using the cross entropy. Here, we computed a Z-score naivel with the formula (Z= (u-m)/sigma). 
But given the fact that the repartition of the cross entropy is not really a gaussian, this formula is not the more appropriate one. Thus,

* in "Standard deviation per voxel", we compute a more sophisticated one (we noticed that this Z-score didn't perform better than the cross entropy, so we quickly forgot this idea).

* In "Latent space", we study some anomaly detection methods on the latent space for the right central sulcus, 

* while in "Analyse", we analyze the result of some 
anomaly detection methods for some regions. 

* Moreover, in the repository "with interrupted central sulcus", we consider the subjects having an interrupted central
sulcus in order to see if we can detect this pattern.  

* Finally, in the folder "with_all_the_regions", we put the codes after training the VAE on all the sulcal regions. In particular, the file "visu_all_regions" help to show a colored map of the brain according to a numeric value in a csv file. We just have to change the path of the corresponding file.

# PEPR_Marseille

On the other hand, the folder "PEPR_Marseille" contains the results with the dataset "F-TRACT". It has three subfolders. 

. Firstly, in "all_the_regions", we have the
same file as priviously: "visu_all_regions". 

. Secondly, in "All the subjects", we have the results using all the 1035 patients of the database. This repository has many subfolders: 

* "SC-sylv-right" where  we put the analyze of the central sulcus,

* "all_the_regions" containing the analyze of all the sulcal regions,

*  "For each subject", where the anomaly 
detection method is applied for some patients, 

* and "histogram_non_zero", where we do the Quality Check.

. Thirdly, in "Selected subjects", we made the study on only the 825 patients selected after the Quality Check (The indexes of the selected subjects are in ./PEPR_Marseille/All the subjects/histogram_non_zero/index_to_save.npy). 

* First of all, we analyze the central sulcus in "SC-sylv-right". 

* Then, we classify the patients according to their lesion type in the subfolder "Lesion_type". 

* After that, we make a study on all the regions in
"all_the_regions". In particular, the redidualization of all the latent spaces are done in the file Residualization_SVM.ipynb

* Then, we visualize the correlation between our three metrics on the central sulcus in the repository "comparaison des métriques". In particular, the plot of the slide 25 in the "café sillon presentation" is obtained while running the file "Residualisation_comparaison.ipynb"

* Finally, our anomaly detection methods are applied inside the folder "For each subject".

Concerning this previous subfolder, it has a file "find_subjects.ipynb" where we selected the subject to whom we'll apply the anomaly detection method, and many others repositories. 

* Given the fact that the implementation of the VAe returns a csv file with the cross entropy for every subject, we create a same file
containing, for every patients in F-TRACT, the value of the Chamfer distance and the anomaly score for each region, thus avoiding to recalculate them every time. The codes for this is in the subfolders "Residualisation_Save_score_SVM", "Save_chamfer_distance" and "Save_score_bagging". 

* In "Save_quantile", we compute, for each metric and for each region, the quantile of the score given by this metric for each patients among all the others patients. 

* Then, in the repository "Study some patients", we apply the anomaly detection method for some pateints. 

* Finally, in the folder "Evaluation_metrics_with_v4", we compute
some evaluation metrics for our methods. (v4 meaning the 4th version of the code by Denis, which is the file "show_sulcal_point_v4 inside the folder "Evaluation_metrics_with_v4". This file return a figure as on the slide 28). In particular, in the folder "Classification_precentral_temporal, we try to solve the easier task of classifying subject among those with a problem on the temporal region and all the othes (using the precentral latent space)


# Link between the notebooks and the figures in the "café sillon" presentation

* To get the colored brain map as in the slides 10, 11, 12, 19, 20, 21, 23, 24, 26, 28 and 29, we have to firstly create a csv file with two columns: a column "region" containing the name of all the regions, and a column "p" containing a numerical value for each value. Then, we should run the code ./fred/epilepsy_PBS/with_all_the_regions/visu_all_regions.ipynb or /fred/PEPR_Marseille/all_the_regions/visu_all_regions.ipynb (there are exactly the same code), but just by changing the path of the corresponding csv file in the variables "path_summary" and "path_file". For example, to plot the graph on the slide 19, We create a csv file using the notebook ./fred/PEPR_Marseille/Selected subjects/all_the_regions/cross_entropy.ipynb, and the corresponding csv file is ./fred/PEPR_Marseille/Selected subjects/all_the_regions/Distance_between_ukb_and_PEPR_for_all_regions. 

* To plot the figures on the slide 31, we should go in the directory ./fred/PEPR_Marseille/Selected_subjects/For each subject/Evaluation_metrics_v4/Quantile for each subject, and run the code Histogram_quantile.ipynb and shuffle/random.ipynb

* Similarly, to plot the graphs on slides 33 and 34, we should run the notebook auc_roc.ipynb and auc_roc_shuffle.ipynb in ./fred/PEPR_Marseille/Selected_subjects/For each subject/Evaluation_metrics_v4/AUC_ROC


# To train the beta-VAE and generate the embeddings

We are in the folder "BETAVAE"

* To train the beta-VAE, we should first change the configs in /configs/config.yaml, by mentionning the dataset(and the sulcal region). For this, the corresponding yaml file must exist in configs/dataset/cristobal. (There is a file which help to create the yaml files for each region for a particular dataset. It's /yaml_all_regions/create_yaml.py. It use the file /yaml_all_regions/ref.yaml as reference). After changing the config, we have to run " python3 main.py n=75" (n being the size of the latent space.)

* To generate the embeddings, we have to first check if the configs are good (as previously), and eventually change the variable config.test_model_dir in the line 124 in generate_embeddings.py, then run "python3 generate_embeddings.py n=75"


# Slurm on Jean-Zay

To create slurm 
files=$(ls ../2023_jlaval_STSbabies/betaVAE/configs/dataset/cristobal/UKB/)

for f in $files; do ./create\_slurm\_from\_template.sh ${f%.*}; done


# Note

At the begining, all the models for all the regions where in /neurospin/tmp/fred/models/2025-11-10. But at the end, we move all these models in /neurospin/dico/fred/Runs/01_betaVAE/Output. This is why, in some notebooks, it is the previous path that is mentionned and in oters, it's the new one.