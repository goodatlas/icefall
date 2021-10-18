# CONFORMER CTC
## Training info 
- At Switch NIPA
- Date: 2021.10.06.
- With 
	- Number of GPUs: 2
	- GPU model: `Tesla V100-SXM2-32GB`
		```
		$ nvidia-smi --query-gpu=name --format=csv,noheader
		Tesla V100-SXM2-32GB
		Tesla V100-SXM2-32GB
		```
- Training time: `25.5` hr
  - 2021-10-06 14:49:47,136 INFO [train.py:631] (0/2) Training started
  - 2021-10-07 16:23:50,760 INFO [train.py:719] (0/2) Done!
## Evaluation CER
- rescoring with attention-decoder scheme
	```
	settings	CER
	ngram_lm_scale_1.1_attention_scale_1.0	5.09
	```

# TDNN-LSTM CTC
## Training info 
- At Atlas IDC Jupiter
- Date: 2021.10.01.
- With 
	- Number of GPUs: 3 
	- GPU model: `Nvidia GeForce RTX 2080 Ti (11G)`
		```
		$ nvidia-smi --query-gpu=name --format=csv,noheader
		GeForce RTX 2080 Ti
		GeForce RTX 2080 Ti
		GeForce RTX 2080 Ti
		```
- Training time: `15` hr
	- 2021-10-01 01:38:21,241 INFO [train.py:515] (0/3) Training started
	- 2021-10-01 16:41:55,379 INFO [train.py:596] (0/3) Done!

## Evaluation CER
- rescoring with whole-lattice-rescoring
	```bash
	settings	CER
	lm_scale_0.9	13.85
	```