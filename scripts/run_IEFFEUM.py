#!/usr/bin/env python
from IEFFEUM import utils
import torch
import argparse
from tqdm import tqdm
import os


def create_arg_parser():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    """"Creates and returns the ArgumentParser object."""
    parser = argparse.ArgumentParser(description='Run IEFFEUM.')
    
    parser.add_argument( '-i', '--input-list', required=True, type=str,
                        help='A path to a LIST file containing input protein(s) list. ' +
                        'This was generated by the script `scripts/prepare_IEFFEUM_input.py`.')
    
    parser.add_argument( '-m', '--model-path', required=False, type=str, default=os.path.join(script_dir, '..', 'weights', 'params.pth'),
                        help='A path to a model parameters PTH file.')
    
    parser.add_argument( '-o', '--out-path', required=False, type=str, default=None,
                        help='A path for output CSV file.')
    
    parser.add_argument( '-b', '--batch-size', required=False, type=int, default=1,
                        help='A batchsize. (default: 1)')
    
    parser.add_argument( '--per-resi', action='store_true',
                        help='Report per-residue dG contributions too. (default: False)')
    
    return parser

if __name__ == '__main__':
    parser = create_arg_parser()
    args = parser.parse_args()
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'Using device: {device}')
    
    out_path = args.out_path if args.out_path else args.input_list.split('/')[-1].replace('.list','.csv')
    
    # Create dataset and dataloader
    dataloader, IEFFEUM = utils.get_dataloader_and_model(args.input_list, args.model_path, device, int(args.batch_size))
    
    NAMES, P_DGS, P_DGS_PER_RESI = [], [], []
    
    # Iterate through a batch
    for batch in tqdm(dataloader):
        names, seqs, seq_embds, str_embds, target_Fs_cords, mask_2ds, mask_1ds = utils.batch_to_device(batch, device)
        target_Fs_onehot = utils.get_target_F_onehot(target_Fs_cords)
        
        results = IEFFEUM(target_Fs_onehot, seq_embds, str_embds, mask_1ds, mask_2ds) # p_ensembles, p_dGs, p_dGs_per_resi, _ = results
        
        NAMES, P_DGS, P_DGS_PER_RESI = utils.gather_batch_results(names, results, NAMES, P_DGS, P_DGS_PER_RESI)
        
    results = utils.save_results_to_csv(NAMES, P_DGS, P_DGS_PER_RESI, out_path, args.per_resi)
    print(f'Predictions saved to {out_path}')