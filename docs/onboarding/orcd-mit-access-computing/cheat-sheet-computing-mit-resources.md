# Cheat sheet to access Computing (GPU) MIT Resources (for free)

## Table of Contents

- [Quick start](#quick-start)
  - [Preliminary steps](#preliminary-steps)
  - [To start a new server session each time](#to-start-a-new-server-session-each-time)
  - [Disclosure](#disclosure)
- [Further settings](#further-settings)
  - [Configure VSCode](#configure-vscode)
  - [Essential Commands](#essential-commands)
  - [Single Node Access: Request Specific GPU Type](#single-node-access-request-specific-gpu-type)
  - [Using Batch Jobs](#using-batch-jobs)
  - [Multi-Node Access: Requesting Multiple Nodes](#multi-node-access-requesting-multiple-nodes)
  - [Multi-Node PyTorch Setup](#multi-node-pytorch-setup)
  - [HuggingFace Cache Configuration](#huggingface-cache-configuration)
- [Available GPU Resources](#available-gpu-resources)
- [Partitions Available](#partitions-available)
- [Storage Locations](#storage-locations)
- [Further Reading & Resources](#further-reading--resources)

---

## Quick start

### Preliminary steps

1. Login with MIT account in https://engaging-ood.mit.edu/
   - In *Files / Home Directory* you can upload on drag and drop your Jupyter codes or file (.csv, etc..)
   - **Do not** use Interactive Apps option since they are updating it and it can't allow you to use the more powerful GPUs

2. Download Globus and configure the accessible paths in order to transfer big dataset from your computer (https://orcd-docs.mit.edu/filesystems-file-transfer/transferring-files/#globus and put image data in `~/orcd/scratch`).

### To start a new server session each time:

| Step | Action | Alternative Action |
|------|--------|-------------------|
| 1 | Open a terminal and type<br><br>`ssh <USER>@orcd-login001.mit.edu`<br><br>Example for the user fga: `ssh fga@orcd-login001.mit.edu`<br><br>Put your password, type 1, (the first time it asks also you to type yes), follow and complete authentication instructions. | |
| 2 | Start a job and asking for allocating resource (with GPU). Type:<br><br>`salloc -N 1 -n 4 -G 1` | If you don't want the default time option, but a maximum of 6 hours:<br><br>`salloc -N 1 -n 4 -G 1 -t 06:00:00`<br><br>There are other features in terms also of memory, more reference here https://orcd-docs.mit.edu/running-jobs/requesting-resources/ |
| 3 (opt) | To verify you can access a GPU correctly, type and check:<br><br>`nvidia-smi` | |
| 4 | Type:<br><br>`module load miniforge` | |
| 5 | Create an Anaconda environment (Reference https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).<br><br>Type (change the name of the environment *test_env* as you need):<br><br>`conda create -n test_env jupyterlab pytorch`<br><br>Add all the packages you need. | If you have already created it previously, just activate it:<br><br>`conda activate test_env`<br><br>Ps. The server is Linux, so it is very probably that environment created from exported `.yml` from other operating system such Windows do not succeed. Suggestion: first time, create it from scratch. |
| 6 | Type:<br><br>`port=$(python -c 'import socket; s=socket.socket(); s.bind(("", 0)); print(s.getsockname()[1]); s.close()')`<br><br>For more reference about port forwarding: https://orcd-docs.mit.edu/recipes/jupyter/ | |
| 7 | Type:<br><br>`jupyter-lab --ip=0.0.0.0 --port=$port` | |
| 8 | Now you can read something like this:<br><br>`To access the server, open this file in a browser:`<br>`  file:///orcd/home/002/fga/.local/share/jupyter/runtime/jpserver-2737427-open.html`<br>`Or copy and paste one of these URLs:`<br>`  http://node3302:52229/lab?token=cc20c18685910cc3e9e7f99290c17499c4380c8c93fbbf9e`<br>`  http://127.0.0.1:52229/lab?token=cc20c18685910cc3e9e7f99290c17499c4380c8c93fbbf9e`<br><br>In this example the **node** is 3302 and the port **52229**.<br><br>**Look** at the second link of the screenshot (in this case): `http://127.0.0.1:52229/lab?token=cc20c18685910cc3e9e7f99290c17499c4380c8c93fbbf9e` | |
| 9 | Open a **new** window terminal in your local machine<br><br>`ssh -L <port>:<node>:<port> <USER>@orcd-login001.mit.edu`<br><br>Example based on the image before (based on my MIT user fga):<br><br>`ssh -L 52229:node3302:52229 fga@orcd-login001.mit.edu` | |
| 10 | Follow authentication instruction and log in. | |
| 11 | Copy the link you read in step 8 from the first terminal windows (in this example `http://127.0.0.1:52229/lab?token=cc20c18685910cc3e9e7f99290c17499c4380c8c93fbbf9e`) and paste it a **new browser internet windows**. | |
| 12 | When you create a new notebook, choose "Python 3 (ipykernel)". The name of your conda environment will not display at this point.<br><br>Enjoy coding! | |

P.s. The paths in a server are indicating as:
`/home/<USER>/…`

Example for data for the user fga:
`/home/fga/orcd/scratch/…`

---

### Disclosure

This document is the result of consulting sessions with ORCD and a summary of the publicly available documentation that can be found through Google or ORCD Engaging resources. It does not aim to be exhaustive, but rather to provide a quick and practical way to access key resources.

Useful to know, regular in-person office hours https://orcd.mit.edu/news-and-events/office-hours:
- **Tuesdays, 10-11 AM** - Room 46-4199
- **Thursdays, 2-3 PM** - GIS & Data Lab, Rotch Library

Last update: 30 October 2025

By Francesca

---

## Further settings

### Configure VSCode

| Steps | Action | Alternative Action |
|-------|--------|-------------------|
| 1 | **Generate an SSH Key.** This command creates a secure ed25519 key, which is recommended:<br>`ssh-keygen -t ed25519 -C "USERNAME@mit.edu"` | More info on SSH with VSCode here: https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh |
| 2 | **Copy the Public Key to the Remote Server** - confirm with your password and authentication with Duo App:<br>`ssh-copy-id USERNAME@orcd-login001.mit.edu` | |
| 3 | **Configure Your SSH config File:**<br>`touch ~/.ssh/config`<br>`chmod 600 ~/.ssh/config`<br>`gedit ~/.ssh/config` | |
| 4 | **Test Login Connection** (Duo App):<br>`ssh orcd-login` | |
| 5 | **Request for GPU** and take note of the node used. Login as described in the quick-start section:<br>`srun --pty -N 1 -n 4 --gres=gpu:l40s:1 -t 03:00:00 bash` | |
| 6 | **Update** `~/.ssh/config` with the compute node config (see below) | |
| 7 | **Connect with VS Code:**<br>1. Install the [Remote - SSH](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh) extension<br>2. Open Command Palette (Ctrl+Shift+P or Cmd+Shift+P)<br>3. Type "Remote-SSH: Connect to Host..."<br>4. Choose orcd-compute | |

Your `~/.ssh/config` should have:

```
# General settings for the login node
Host orcd-login
    HostName orcd-login001.mit.edu
    User USERNAME
    ControlMaster auto
    ControlPath ~/.ssh/%r@%h:%p
    ControlPersist 300s
    IdentityFile ~/.ssh/id_ed25519

Host orcd-compute
    HostName node4201  # Replace with YOUR actual node from 'hostname' command
    User USERNAME
    ProxyJump orcd-login
    IdentityFile ~/.ssh/id_ed25519
```

---

### Essential Commands

| Steps | Action | Alternative Action |
|-------|--------|-------------------|
| 1 | **Job Management:**<br>• Check your jobs: `squeue --me`<br>• Watch job queue: `watch -n 5 squeue --me`<br>• Cancel a job: `scancel <job_id>`<br>• Job details: `scontrol show job <job_id>`<br>• Access running job: `srun --jobid=<job_id> --pty /bin/bash` | More on these commands here: https://orcd-docs.mit.edu/running-jobs/overview/ |
| 2 | **GPU & Node Info:**<br>• View available GPUs: `sinfo -o "%20N %10c %10m %25f %10G" \| grep gpu`<br>• Check GPU on node: `nvidia-smi`<br>• Monitor GPU usage: `watch -n 1 nvidia-smi`<br>• Check partition limits: `scontrol show partition mit_normal_gpu` | |

---

### Single Node Access: Request Specific GPU Type

| Steps | Action | Alternative Action |
|-------|--------|-------------------|
| 1 | **1 L40S GPU (most available):**<br>`salloc -N 1 -n 4 --gres=gpu:l40s:1 -t 12:00:00` | Alternatively you can submit a sbatch job as shown below |
| 2 | **1 H100 GPU:**<br>`salloc -N 1 -n 4 --gres=gpu:h100:1 -t 06:00:00` | |

---

### Using Batch Jobs

| Steps | Action | Alternative Action |
|-------|--------|-------------------|
| 1 | Create a file `gpu_job.sh` (see below) | |
| 2 | **Submit the job:**<br>`sbatch gpu_job.sh` | |
| 3 | **Check job status:**<br>`squeue --me` | |

Example `gpu_job.sh`:

```bash
#!/bin/bash
#SBATCH --partition=mit_normal_gpu
#SBATCH --gres=gpu:l40s:1
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --time=12:00:00
#SBATCH --output=job_%j.out
#SBATCH --error=job_%j.err

# Load modules
module load miniforge/24.3.0-0

# Activate environment
source activate myenv

# Run your script
python train.py
```

---

### Multi-Node Access: Requesting Multiple Nodes

| Steps | Action | Alternative Action |
|-------|--------|-------------------|
| 1 | **Monitor job queue:**<br>`watch -n 5 squeue --me` | Jobs might take a while to get assigned a node based on availability. |
| 2 | **2 nodes, 1 GPU each:**<br>`salloc -N 2 -n 8 --gres=gpu:l40s:1 -t 12:00:00` | |

---

### Multi-Node PyTorch Setup

| Steps | Action | Alternative Action |
|-------|--------|-------------------|
| 1 | For distributed training across multiple nodes, create `distributed_train.sh` (see below) | |
| 2 | **Submit the job:**<br>`sbatch distributed_train.sh` | |

Example `distributed_train.sh`:

```bash
#!/bin/bash
#SBATCH --partition=mit_normal_gpu
#SBATCH --gres=gpu:l40s:4
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=4
#SBATCH --time=12:00:00

module load miniforge/24.3.0-0
source activate myenv

export MASTER_ADDR=$(scontrol show hostname $SLURM_NODELIST | head -n 1)
export MASTER_PORT=12345

srun python -m torch.distributed.launch \
    --nproc_per_node=4 \
    --nnodes=$SLURM_NNODES \
    --node_rank=$SLURM_NODEID \
    --master_addr=$MASTER_ADDR \
    --master_port=$MASTER_PORT \
    train_distributed.py
```

---

### HuggingFace Cache Configuration

| Steps | Action | Alternative Action |
|-------|--------|-------------------|
| 1 | **Critical:** Configure HuggingFace to use scratch storage to avoid filling your 200GB home directory. Run the commands below. | Update your USERNAME. |

```bash
cat >> ~/.bashrc << 'EOF'
export HF_HOME="/home/USERNAME/orcd/scratch/.huggingface"
export TRANSFORMERS_CACHE="/home/USERNAME/orcd/scratch/.huggingface/hub"
export HF_DATASETS_CACHE="/home/USERNAME/orcd/scratch/.huggingface/datasets"
mkdir -p $HF_HOME $TRANSFORMERS_CACHE $HF_DATASETS_CACHE
EOF

source ~/.bashrc
ls /home/USERNAME/orcd/scratch/.huggingface
```

**Troubleshooting**

The error happened because `/orcd/scratch/.huggingface` wasn't writable for your user. The `.bashrc` had old environment variables pointing there, so each time it ran it tried to create that folder and failed.

**Fix:**
1. Open `~/.bashrc` and remove or comment out any line exporting `HF_HOME`, `TRANSFORMERS_CACHE`, or `HF_DATASETS_CACHE` pointing to `/orcd/scratch/`....

2. Add these lines at the end:

```bash
export HF_HOME="/home/USERNAME/orcd/scratch/.huggingface"
export TRANSFORMERS_CACHE="$HF_HOME/hub"
export HF_DATASETS_CACHE="$HF_HOME/datasets"
[ ! -d "$HF_HOME" ] && mkdir -p "$HF_HOME" "$TRANSFORMERS_CACHE" "$HF_DATASETS_CACHE"
```

3. Reload with `source ~/.bashrc`.

**Check:**
```bash
echo $HF_HOME
ls -ld $HF_HOME
```

They should show your personal path and have proper permissions.

---

## Available GPU Resources

*Note: GPU counts are approximate as of November 2025. MIT continuously adds new hardware to the Engaging cluster. For the most current GPU inventory, run:* `sinfo -o "%20N %10c %10m %25f %10G" | grep gpu`

| GPU Type | ~Total GPUs | GPU Memory | Architecture | Node RAM | Best For |
|----------|-------------|------------|--------------|----------|----------|
| **H200** | ~104 | 141GB HBM3e | Hopper | ~2TB | Large language models, massive datasets |
| **L40S** | ~200 | 48GB GDDR6 | Ada Lovelace | ~1TB | General deep learning, computer vision |
| **H100** | ~32 | 80GB HBM3 | Hopper | ~1-2TB | Training large models, HPC workloads |
| **A100** | ~64 | 40-80GB HBM2e | Ampere | ~515GB | Training, inference, research |

---

## Partitions Available

| Partition | Max Time | Notes |
|-----------|----------|-------|
| `mit_normal_gpu` | 6 hours | Default GPU partition, guaranteed access. Has L40S and H200 GPUs available. |
| `mit_preemptable` | 2 days | Can be preempted, longer jobs allowed. Use `--requeue` flag. |
| `mit_normal` | 12 hours | CPU only (no GPUs) |

---

## Storage Locations

| Location | Path | Quota | Use For |
|----------|------|-------|---------|
| **Home** | `/home/USERNAME/` | 200GB | Code, scripts, git repos. Backed up. |
| **Scratch** | `/home/USERNAME/orcd/scratch/` | 200GB | Training data, model cache, temp files. NOT backed up. Files deleted after 6 months. |
| **Pool** | `/home/USERNAME/orcd/pool/` | 1TB | Final models, results, archives. Backed up. |

---

## Further Reading & Resources

- **Main Documentation:** https://orcd-docs.mit.edu/
- **Getting Started Guide:** https://orcd-docs.mit.edu/getting-started/

Last update: 4 November 2025

**By Sebastian**
