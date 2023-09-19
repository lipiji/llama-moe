#!/usr/bin/bash

set -vx

tokenizer_dir=/mnt/petrelfs/share_data/quxiaoye/models/llama_7B
data_dir=/mnt/petrelfs/zhutong/smoe/resources/clustering_samples
out_dir=/mnt/petrelfs/share_data/quxiaoye/data/8clusters
logs_dir=logs

mkdir -p $out_dir
mkdir -p $logs_dir

# for loop in: en_arxiv, en_book, en_c4, en_cc, en_stack, en_wikipedia, github
for data_type in $(ls $data_dir)
do
    log_path=logs/tokenize_${data_type}_8clusters.log
    nohup srun -p MoE -N1 -n1 --cpus-per-task=32 -x "SH-IDCA1404-10-140-54-[12,18,33,38,41,43,63,70-71,74,83,85]" \
        python -m smoe.utils.tokenize \
            -f jsonl \
            -t $tokenizer_dir \
            -i $data_dir/$data_type \
            -o $out_dir/$data_type \
        1>${log_path} 2>&1 &
    echo "$data_type > $log_path"
done
