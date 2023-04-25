from liana.multi import to_tensor_c2c, adata_to_views, lrs_to_views, get_variable_loadings, get_factor_scores
from liana.testing import sample_lrs, get_toy_adata

import numpy as np
import pandas as pd

import cell2cell as c2c

adata = get_toy_adata()


def test_to_tensor_c2c():
    """Test to_tensor_c2c."""
    liana_res = sample_lrs(by_sample=True)
    
    liana_dict = to_tensor_c2c(liana_res=liana_res,
                               sample_key='sample',
                               score_key='specificity_rank',
                               return_dict=True
                               )
    assert isinstance(liana_dict, dict)
    
    tensor = to_tensor_c2c(liana_res=liana_res,
                           sample_key='sample',
                           score_key='specificity_rank')
    assert isinstance(tensor, c2c.tensor.tensor.PreBuiltTensor)
    assert tensor.sparsity_fraction()==0.0
    

def test_lrs_to_views():
    """Test lrs_to_views."""
    liana_res = sample_lrs(by_sample=True)
    adata.uns['liana_results'] = liana_res
    
    mdata = lrs_to_views(adata=adata,
                         sample_key='sample',
                         score_key='specificity_rank',
                         uns_key = 'liana_results',
                         obs_keys = ['case'],
                         lr_prop=0.1,
                         lrs_per_sample=0,
                         lrs_per_view=5,
                         samples_per_view=0,
                         min_variance=-1, # don't filter
                         verbose=True
                         )
    
    assert mdata.shape == (4, 16)
    assert 'case' in mdata.obs.columns
    assert len(mdata.varm_keys())==3

    

def test_adata_to_views():
    """Test adata_to_views."""
    mdata = adata_to_views(adata,
                           groupby='bulk_labels',
                           sample_key='sample',
                           obs_keys=None,
                           min_cells=5,
                           min_counts=10,
                           mode='sum',
                           verbose=True,
                           use_raw=True,
                           skip_checks=True # skip because it's log-normalized (it's OK because toydata)
                           )
    
    assert len(mdata.varm_keys())==8
    assert 'case' not in mdata.obs.columns
    assert mdata.shape == (4, 5403)
    
    #test feature level filtering (with default values)
    mdata = adata_to_views(adata,
                           groupby='bulk_labels',
                           sample_key='sample',
                           obs_keys=None,
                           args={'filter_by_expr':{}, 'filter_by_prop':{}},
                           min_cells=5,
                           min_counts=10,
                           mode='sum',
                           verbose=True,
                           use_raw=True,
                           skip_checks=True # skip because it's log-normalized (it's OK because toydata)
                           )

    #test feature level filtering (passing arguments)
    mdata = adata_to_views(adata,
                           groupby='bulk_labels',
                           sample_key='sample',
                           obs_keys=None,
                           args={'filter_by_expr':{'min_count': 10}, 'filter_by_prop':{ 'min_prop':0.2, 'min_smpls':2}},
                           min_cells=5,
                           min_counts=10,
                           mode='sum',
                           verbose=True,
                           use_raw=True,
                           skip_checks=True # skip because it's log-normalized (it's OK because toydata)
                           )

    
    
    
def test_get_funs():
    liana_res = sample_lrs(by_sample=True)
    adata.uns['liana_results'] = liana_res
    
    mdata = lrs_to_views(adata=adata,
                         sample_key='sample',
                         score_key='specificity_rank',
                         uns_key = 'liana_results',
                         lr_prop=0.1,
                         lrs_per_sample=0,
                         lrs_per_view=5,
                         samples_per_view=0,
                         min_variance=-1, # don't filter
                         verbose=True
                         )
    
    # generate random loadings
    mdata.varm['LFs'] = np.random.rand(mdata.shape[1], 5)
    
    loadings = get_variable_loadings(mdata, view_separator=':', variable_separator='^', pair_separator='&')
    assert isinstance(loadings, pd.DataFrame)
    assert loadings.shape == (16, 9)
    
    # dont drop columns & and don't separate
    loadings = get_variable_loadings(mdata, drop_columns=False)
    assert isinstance(loadings, pd.DataFrame)
    assert loadings.shape == (16, 6)
    
    
    # generate random factor scores
    mdata.obsm['X_mofa'] = np.random.rand(mdata.shape[0], 5)
    
    scores = get_factor_scores(mdata)
    assert isinstance(scores, pd.DataFrame)
    assert scores.shape == (4, 6)
