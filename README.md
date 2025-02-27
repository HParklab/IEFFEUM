# IEFFEUM
IEFFEUM (***I***n silico ***E***valuation of Un***f***olding ***F***ree ***E***nergy with ***U***nfolded states ***M***odeling, 이쁨)
![image](ieffeum.png)
Please read the [manuscript](https://www.biorxiv.org/content/10.1101/2025.02.10.637420v1) before you use IEFFEUM.

We thank those who support open science. Without them, developing IEFFEUM was impossible.

## Citation
If you use the code, please cite:
```
@article{
    doi:10.1101/2025.02.10.637420,
    author = {Heechan Lee and Hahnbeom Park},
    title = {Protein folding stability estimation with an explicit consideration of unfolded states},
    journal = {bioRxiv},
    year = {2025},
    doi = {10.1101/2025.02.10.637420},
    URL = {https://www.biorxiv.org/content/10.1101/2025.02.10.637420v1},
}
```

## Before You Start

**Important Note on GPU Usage:**

Running IEFFEUM on different GPUs (e.g., A5000 vs. A6000) might result in slightly different predicted Δ*G* values.  The exact cause of this discrepancy is currently unknown. (마이유비 설명)

## Installation

IEFFEUM requires [ProtT5](https://github.com/agemagician/ProtTrans) and [ESM](https://github.com/facebookresearch/esm) (specifically, ESM-IF1).  While ESMFold is highly recommended for optimal performance, it's optional. You can provide pre-computed structures from any source.

**Prerequisites:**

1.  **NVIDIA GPU:**  Ensure your system has a compatible NVIDIA GPU and the drivers are correctly installed. Verify with:

    ```bash
    nvidia-smi
    ```

2.  **Conda:**  We strongly recommend using [miniconda](https://docs.anaconda.com/miniconda/install/).

**Installation Steps:**

Due to the archival of the ESM repository, installation requires a few specific steps.  These commands have been tested, but they differ slightly from those used in the training process.

```
# 1. Create and activate the Conda environment (this may take some time):
conda env create -f environment.yaml
conda activate IEFFEUM

# 2. Clone the IEFFEUM repository and install it:
git clone https://github.com/HParklab/IEFFEUM.git
cd IEFFEUM
pip install -e .
```

## Preparing Input Data
To run IEFFEUM (in batch), you need:
1. **Input FASTA File** (`.fasta`):  A FASTA file containing the amino acid sequences of the proteins you want to analyze.  This is **required**.
    ```
    # example: MyUb.fasta
    >MyUb_WT
    GTKKYDLSKWKYAELRDTINTSCDIELLAACREEFHRRLKVYH
    >MyUb_R1117A
    GTKKYDLSKWKYAELRDTINTSCDIELLAACREEFHRALKVYH
    ```
    **Important**: IEFFEUM processes sequences in batches for the efficiency, padding them to the length of the longest sequence in each batch. For optimal GPU memory usage, group proteins with similar sequence lengths into the same FASTA file.

2. **Structure Files (Optional)**:  You have two options for providing structural information (target folded state):
    - **Option A**: **Provide PDB Files (recommended for longer proteins)**:  Place your `.pdb` files in a directory (e.g., `/PATH/TO/PDBs`).  The filenames should match the sequence identifiers in your FASTA file (e.g., `MyUb_WT.pdb`).
    ```
    # example: /PATH/TO/PDBs
    /PATH/
    └── TO/
        └── PDBs/
            ├── MyUb_WT.pdb 
            └── MyUb_R1117A.pdb
    ```

    - **Option B**: **Use ESMFold (easier)**: If you don't provide PDB files, `prepare_IEFFEUM.py` will automatically run ESMFold to predict the structures.

**Running** `prepare_IEFFEUM.py`:

This script generates the necessary files for IEFFEUM.

- **With Pre-computed PDB Files**:
    ```
    ./scripts/prepare_IEFFEUM.py --fasta <FASTA file> --pdb </PATH/TO/PDBs>
    # Example:
    # ./scripts/prepare_IEFFEUM.py --fasta examples/MyUb.fasta --pdb examples/MyUb_PDBs
    ```
    This will create a directory `/PATH/TO/PDBs/pt/` containing the `.pt` files.

- **Using ESMFold for Structure Prediction**:
    ```
    ./scripts/prepare_IEFFEUM.py --fasta <FASTA file>
    # Example:
    # ./scripts/prepare_IEFFEUM.py --fasta examples/MyUb.fasta
    ```

After running `prepare_IEFFEUM.py`, you should have:

1. `<FASTA_DIR>/<TARGET>.list`.  For example, if your FASTA file is `/home/usr/IEFFEUM/example/MyUb.fasta`, the generated file will be` /home/usr/IEFFEUM/example/MyUb.list`.
2. One of the following:
    - `/PATH/TO/PDBs/pt/` directory containing `.pt` files (if you provided PDBs).
    - `/PATH/TO/FASTA/TARGET-esmfold/` directory containing `.pdb` and `TARGET-esmfold/pt/` with `.pt` files (if you used ESMFold).

        **Important Note on ESMFold Results:** It is highly recommended to the users to visually inspect the ESMFold-predicted structures.  [Poorly predicted structures can negatively impact IEFFEUM's accuracy](https://www.biorxiv.org/content/10.1101/2025.02.10.637420v1). Consider using pre-computed, high-quality structures (consider using [AF3](https://alphafoldserver.com/)).

## Running IEFFEUM

Once the input data is prepared, you can run IEFFEUM to calculate the Δ*G*. Note that IEFFEUM will use GPU whenever visible.

```
./scripts/run_IEFFEUM.py \
    -i <LIST file> \
    -m <path for model params (default: /PATH/TO/IEFFEUM/weights/params.pth)> \
    -o <path for result CSV file (default: ./TARGET.csv)> \
    -b <batch size (default: 1)>
    퍼 레지듀 설명

# Example:
# ./scripts/run_IEFFEUM.py -i examples/MyUb.list -o ../MyUb_out.csv -b 100
```

## Inspecting the Output
