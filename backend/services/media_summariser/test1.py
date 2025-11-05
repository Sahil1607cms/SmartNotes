import torch, subprocess
print("torch:", torch.__version__)
print("cuda available:", torch.cuda.is_available())
print("cuda devices:", torch.cuda.device_count())
# run once in terminal:
# nvidia-smi
