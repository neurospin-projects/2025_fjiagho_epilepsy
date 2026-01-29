This folder is constitued of two repositories "epilepsy_PBS" and "PEPR_Marseille", representing the two epileptic datasets that I used, and a file 
"mask_interrupted_cs.csv", representing for all the subjects in UKB, if he has an interrupted central sulcus or not. 


The folder "epilepsy_PBS" contains the results with the dataset "epilepsy_PBS". It is composed by many subfolders. In "CCD", we try to reproduce the results of
Louise Guillon with training the beta-VAE on HCP and testing it on CCD.In the repository "ABCD", there are the results when training the beta-VAE on ABCD.
In all the others subfolders, it is when training on UKB. In "SC-sylv_right_UKB_16-20-03_123, we have the output files When training the beta-VAE on the
right central sulcus of UKB. And in the folder "epilepsy_PBS", there are the results(cross entropy and UMAP) when training the model on some regions.

In the repository "age_side_epilepsyPBS", the goal is to plot the reconstruction error in epilepsy_PBS as a function of the age of the subjects. In addition, 
in the folder "Z-score", the goal was to compute the Z-score using the cross entropy. Here, we computed a Z-score naivel with the formula (Z= (u-m)/sigma). 
But given the fact that the reapatition of the cross entropy is not really a gaussian, this formula is not the more appropriate one. Thus, in "Standard deviation
per voxel", we compute a more sophisticated one (we noticed that this Z-score didn't perform better than the cross entropy, so we quickly forgot this idea).

In "Latent space", we study some anomaly detection methods on the latent space for the right central sulcus, while in "Analyse", we analyze the result of some 
anomaly detection methods for some regions. Moreover, in the repository "with interrupted central sulcus", we consider the subjects having an interrupted central
sulcus in order to see if we can detect this pattern.  Finally, in the folder "with_al_the_regions", we put the codes after training the VAE on all the sulcal
regions. In particular, the file "visu_all_regions" help to show a colored map of the brain according to a numeric value in a csv file. We just have to change 
the path of the corresponding file.



On the other hand, the folder "PEPR_Marseille" contains the results with the dataset "F-TRACT". It has three subfolders. Firstly, in "all_the_regions", we have the
same file as priviously. 

Secondly, in "All the subjects", we have the results using all the 1035 patients of the database. This repository has many subfolders: "SC-sylv-right" where 
we put the analyzing of the central sulcus,"all_the_regions" containing the analyzing of all the sulcal regions, "For each subject", where the anomaly 
detection metho is applied for some patients, and "histogram_non_zero", where we do the Quality Check.

Thirdly, in "Selected subjects", we made the study on only the 825 patients selected after the Quality Check. First of all, we analyze the central sulcus in
"SC-sylv-right". Then, we classify the patients according to their lesion type in the subfolder "Lesion_type". After that, we make a study on all the regions in
"all_the_regions". Then, we visualize the correlation between our three metrics on the central sulcus in the repository "comparaison des métriques".
Finally, our anomaly detection methods are applied inside the folder "For each subject".

Concerning this previous subfolder, it has a file "find_subjects.ipynb" where we selected the subject to whom we'll apply the anomaly detection method, and many
others repositories. Given the fact that the implementation of the VAe returns a csv file with the cross entropy for every subject, we create a same file
containing, for every patients in "F-TRACT", the value of the Chamfer distance and the anomaly score for each region, thus avoiding to recalculate them every
time. The codes for this is in the subfolders "Residualisation_Save_score_SVM", "Save_chamfer_distance" and "Save_score_bagging". In "Save_quantile", we 
compute, for each metric and for each region, the quantile of the score given by this metric for each patients among all the others patients. Then, in the
repository "Study some patients", we apply the anomaly detection method for some pateints. Finally, in the folder "Evaluation_metrics_with_v4", we compute
some evaluation metrics for our methods. (v4 meaning the 4th version of the code by Denis, which is the file "show_sulcal_point_v4 inside the folder
"Evaluation_metrics_with_v4")