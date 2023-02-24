#!/bin/bash

cd /vols/cms/jwd18/Hee/MLCategorisation/CMSSW_10_2_0/src/HToEE
source setup.sh

#declare -a systs=("jesTotalUp" "jesTotalDown" "jerUp" "jerDown" "ElPtScaleUp" "ElPtScaleDown")
declare -a systs=("jesTotalUp" "jesTotalDown" "jerUp" "jerDown" "EELowR9ElPtScaleUp" "EELowR9ElPtScaleDown" "EEHighR9ElPtScaleUp" "EEHighR9ElPtScaleDown" "EBLowR9ElPtScaleUp" "EBLowR9ElPtScaleDown" "EBHighR9ElPtScaleUp" "EBHighR9ElPtScaleDown" "NonLinearityUp" "NonLinearityDown")
#declare -a systs=("jesTotalUp")

##2016-A
#usual systs
#for syst in "${systs[@]}"
#do
#    python categoryOpt/generic_tagger.py -c configs/OneTwenty/tag_seq_config_2016A.yaml -M configs/mva_boundaries_config.yaml -d -S "$syst" 
#done
#weight systs (plus nominal branches)
#python categoryOpt/generic_tagger.py -c configs/OneTwenty/tag_seq_config_2016A.yaml -M configs/mva_boundaries_config.yaml -d -W

#2016-B
#usual systs
#for syst in "${systs[@]}"
#do
#    python categoryOpt/generic_tagger.py -c configs/OneTwenty/tag_seq_config_2016B.yaml -M configs/mva_boundaries_config.yaml -d -S "$syst"
#done
#weight systs (plus nominal branches)
#python categoryOpt/generic_tagger.py -c configs/OneTwenty/tag_seq_config_2016B.yaml -M configs/mva_boundaries_config.yaml -d -W

##2017
#usual systs
#for syst in "${systs[@]}"
#do
#    python categoryOpt/generic_tagger.py -c configs/OneTwenty/tag_seq_config_2017.yaml -M configs/mva_boundaries_config.yaml -d -S "$syst"
#done
#weight systs (plus nominal branches)
#python categoryOpt/generic_tagger.py -c configs/OneTwenty/tag_seq_config_2017.yaml -M configs/mva_boundaries_config.yaml -d -W -r

##2018
##usual systs
#for syst in "${systs[@]}"
#do
#    python categoryOpt/generic_tagger.py -c configs/OneTwenty/tag_seq_config_2018.yaml -M configs/mva_boundaries_config.yaml -d -S "$syst"
#done
##weight systs (plus nominal branches)
#python categoryOpt/generic_tagger.py -c configs/OneTwenty/tag_seq_config_2018.yaml -M configs/mva_boundaries_config.yaml -d -W
