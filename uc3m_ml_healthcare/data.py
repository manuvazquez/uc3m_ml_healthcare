# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/10_data.ipynb.

# %% auto 0
__all__ = ['make_periodic_dataset', 'CollateFunction']

# %% ../nbs/10_data.ipynb 3
# import pathlib
# import itertools
import types

from fastcore.utils import patch

# import pandas as pd
# import numpy as np
import torch
import torch.distributions
from torch.distributions import uniform

# from latent_ode.generate_timeseries import Periodic_1d
from .generate_timeseries import Periodic_1d

# %% ../nbs/10_data.ipynb 8
def make_periodic_dataset(
    timepoints: int, # Number of time instants
    extrap: bool, # Whether extrapolation is peformed
    max_t: float, # Maximum value of time instants
    n: int, # Number of examples
    noise_weight: float # Standard deviation of the noise to be added
) -> tuple[torch.Tensor, torch.Tensor]: # Time and observations
    
    # so that we can use the original code "verbatim" (plus some comments)
    args = types.SimpleNamespace(timepoints=timepoints, extrap=extrap, max_t=max_t, n=n, noise_weight=noise_weight)
    
    # --------- Rubanova (see above)

    n_total_tp = args.timepoints + args.extrap

    # better understood as max_t_extrap = n_total_tp / args.timepoints * args.max_t (you adjust `max_t` if extrapolation is requested)
    # if `args.extrap` is `False`, then this is exactly equal to `n_total_tp` since `n_total_tp = args.timepoints`
    max_t_extrap = args.max_t / args.timepoints * n_total_tp

    distribution = uniform.Uniform(torch.Tensor([0.0]),torch.Tensor([max_t_extrap]))
    time_steps_extrap =  distribution.sample(torch.Size([n_total_tp-1]))[:,0] # last part is just "squeezing"
    time_steps_extrap = torch.cat((torch.Tensor([0.0]), time_steps_extrap)) # 0 is always there
    time_steps_extrap = torch.sort(time_steps_extrap)[0]

    # frequencies are not passed (and henced sampled internally)
    dataset_obj = Periodic_1d(
        init_freq = None, init_amplitude = 1.,
        final_amplitude = 1., final_freq = None, 
        z0 = 1.)

    dataset = dataset_obj.sample_traj(time_steps_extrap, n_samples = args.n, noise_weight = args.noise_weight)
    
    # ---------
    
    return time_steps_extrap, dataset

# %% ../nbs/10_data.ipynb 12
class CollateFunction:
    
    def __init__(self,
                 time: torch.Tensor, # Time axis [time]
                 n_points_to_subsample: int # Number of points to be "subsampled"
                ):
        
        self.time = time
        self.n_points_to_subsample = n_points_to_subsample
        
        self._n_time_instants = len(time)
        self._half_n_time_instants: int = self._n_time_instants // 2
        
    def __call__(self,
                 batch: list # Observations [batch]
                ) -> dict:
        
        # [batch, time, feature]
        batch = torch.stack(batch)
        
        # ----------- splitting on training and to-predict
        
        # for observations
        observed_data = batch[:, :self._half_n_time_instants, :].clone()
        to_predict_data = batch[:, self._half_n_time_instants:, :].clone()
        
        # for time
        observed_time = self.time[:self._half_n_time_instants].clone()
        to_predict_at_time = self.time[self._half_n_time_instants:].clone()
        
        # ----------- mask
        
        # CAVEAT: only on observed data
        observed_mask = torch.ones_like(observed_data, device=observed_data.device)
        
        # if we are to sample ALL the points in the observed data...
        if self._half_n_time_instants == self.n_points_to_subsample:
            
            # ...there is nothing to do here
            pass
        
        else:
            
            raise Exception('not implemented')
            
        # ----------- observation-less time instants
        
        # # summing across "batch" and "feature" dimensions
        # non_missing = (observed_data.sum(dim=(0, 2)) != 0.)
        
        
        return dict(
            observed_time=observed_time, observed_data=observed_data,
            to_predict_at_time=to_predict_at_time, to_predict_data=to_predict_data,
            observed_mask=observed_mask)
        
    def __str__(self):
        
        return f'Collate function expecting {self._n_time_instants} time instants, subsampling {self.n_points_to_subsample}.'
    
    # a object is represented by its string
    __repr__ = __str__
    
    def to(self, device):
        
        self.time = self.time.to(device=device)

# %% ../nbs/10_data.ipynb 31
@patch
def to(self: CollateFunction, device):
    
    self.time = self.time.to(device=device)
