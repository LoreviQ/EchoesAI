#!/bin/bash

# Get requirements from virtual environment
source .venv/bin/activate
pip freeze > requirements.txt
deactivate

# Replace file dependent reqs 
pattern="torch @ file:///home/lorevi/workspace/github.com/LoreviQ/EchoesAI/.venv/torch-2.1.2%2Brocm6.1.3-cp310-cp310-linux_x86_64.whl#sha256=2cb85d429ce2108ba4b060297947ab09f86fac8c09468730d6db02a9221dc69e"
replacement="#torch - detatched mode deployment"
sed -i "s|$pattern|$replacement|g" requirements.txt
pattern="pytorch-triton-rocm @ file:///home/lorevi/workspace/github.com/LoreviQ/EchoesAI/.venv/pytorch_triton_rocm-2.1.0%2Brocm6.1.3.4d510c3a44-cp310-cp310-linux_x86_64.whl#sha256=34ee585edf922a163b3ae6dbb90b291317947b7c8b47c045db058d92ec79e2b0"
replacement="#pytorch-triton-rocm - detatched mode deployment"
sed -i "s|$pattern|$replacement|g" requirements.txt
pattern="torchvision @ file:///home/lorevi/workspace/github.com/LoreviQ/EchoesAI/.venv/torchvision-0.16.1%2Brocm6.1.3-cp310-cp310-linux_x86_64.whl#sha256=8949a908176563c7e310bcacbaba1fe2d6751a701051a85be976ca557ab435be"
replacement="#torchvision - detatched mode deployment"
sed -i "s|$pattern|$replacement|g" requirements.txt
pattern="transformers==4.45.2"
replacement="#transformers==4.45.2 - detatched mode deployment"
sed -i "s|$pattern|$replacement|g" requirements.txt
pattern="transformers==4.45.2"
replacement="#transformers==4.45.2 - detatched mode deployment"
sed -i "s|$pattern|$replacement|g" requirements.txt
pattern="accelerate==1.0.1"
replacement="#accelerate==1.0.1 - detatched mode deployment"
sed -i "s|$pattern|$replacement|g" requirements.txt
pattern="huggingface-hub==0.25.2"
replacement="#huggingface-hub==0.25.2 - detatched mode deployment"
sed -i "s|$pattern|$replacement|g" requirements.txt
pattern="safetensors==0.4.5"
replacement="#safetensors==0.4.5 - detatched mode deployment"
sed -i "s|$pattern|$replacement|g" requirements.txt