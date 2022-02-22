import pytest
import pandas as pd
import numpy as np
from kipoiseq.extractors.vcf import MultiSampleVCF
# from kipoiseq.extractors.vcf_query import to_sample_csv
from splicing_outlier_prediction import SpliceOutlier, SpliceOutlierDataloader, CatInference, SplicingOutlierResult
from splicing_outlier_prediction.ensemble import train_model_ebm
from conftest import fasta_file, vcf_file, multi_vcf_file, \
    ref_table5_kn_testis, ref_table3_kn_testis,  \
    ref_table5_kn_lung, ref_table3_kn_lung, \
    count_cat_file_lymphocytes,  count_cat_file_blood, \
    spliceai_path, mmsplice_path, mmsplice_cat_path, \
    gene_tpm_path, gene_map_path, var_samples_path, gene_tpm_path, pickle_absplice_DNA, pickle_absplice_RNA



def test_real_data():
    dir_path = '/home/wagnern/Projects/gitlab_gagneurlab/splicing-outlier-prediction/tests/data/test_real_data/'
    count_table_path = dir_path + 'count_table_all_updated_no_chr.csv'
    splicemap3_path = dir_path + 'Prokisch_Fibroblasts_splicemap_psi3_method=kn_event_filter=median_cutoff.csv'
    splicemap5_path = dir_path + 'Prokisch_Fibroblasts_splicemap_psi5_method=kn_event_filter=median_cutoff.csv'
    var_samples_path = dir_path + 'EXT_WAR_001_vcf_annotation.csv'
    mmsplice_splicemap_path = dir_path + 'EXT_WAR_001_mmsplice_splicemap_event_filter=median_cutoff.csv'
    df = pd.read_csv(mmsplice_splicemap_path)
    df_samples = pd.read_csv(var_samples_path)
    df_gene_tpm = pd.read_csv(gene_tpm_path)
    _df = df_gene_tpm[df_gene_tpm['tissue'] == 'Cells_Cultured_fibroblasts']
    _df = _df.replace({'Cells_Cultured_fibroblasts': 'Prokisch_Fibroblasts'})
    df_gene_tpm = pd.concat([df_gene_tpm, _df])
    
    from splicemap.splice_map import SpliceMap
    sm = SpliceMap.read_csv(splicemap5_path)
    print('hello')
    cat_dl = CatInference(
        splicemap5=splicemap5_path,
        splicemap3=splicemap3_path,
        count_cat=count_table_path,
        name='Prokisch_Fibroblasts'
    )

    result = SplicingOutlierResult(
        df_mmsplice = mmsplice_splicemap_path,
        gene_tpm = df_gene_tpm,
    )

    result.add_samples(pd.read_csv(var_samples_path))

    result.infer_cat(cat_dl, progress=True)
    
    result.df_mmsplice_cat.shape[0] > 0
    '10:135215749-135216195:+' in result.df_mmsplice_cat.index.get_level_values('junction')
    
    
    # overlapping genes: 
#                                       gene_id
# junctions                                
# 10:135215749-135216195:+  ENSG00000254536
# 10:135215749-135216195:+  ENSG00000148824


def test_splicing_outlier_result__init__absplice_dna_input(gene_tpm, gene_map):
    # Initialize with mmsplice_cat
    sor_absplice_dna = SplicingOutlierResult(
        df_mmsplice=mmsplice_path, 
        df_spliceai=spliceai_path, 
        gene_tpm=gene_tpm,
        gene_map=gene_map
    )
    df_absplice_dna_input = sor_absplice_dna.absplice_dna_input
    sor = SplicingOutlierResult(
        df_absplice_dna_input=df_absplice_dna_input
    )
    assert sor.absplice_dna_input.shape[0] > 0
    
def test_splicing_outlier_result__init__absplice_rna_input(gene_tpm, gene_map):
    # Initialize with mmsplice_cat
    sor_absplice_rna = SplicingOutlierResult(
        df_mmsplice=mmsplice_path, 
        df_spliceai=spliceai_path, 
        df_mmsplice_cat=mmsplice_cat_path, 
        gene_tpm=gene_tpm,
        gene_map=gene_map,
        df_var_samples = var_samples_path
    )
    df_absplice_rna_input = sor_absplice_rna.absplice_rna_input
    sor = SplicingOutlierResult(
        df_absplice_rna_input=df_absplice_rna_input
    )
    assert sor.absplice_rna_input.shape[0] > 0
    
    
def test_splicing_outlier_result__init__(gene_tpm, gene_map):
    df_mmsplice = pd.read_csv(mmsplice_path)
    df_spliceai = pd.read_csv(spliceai_path)
    # _gene_tpm = gene_tpm[gene_tpm['tissue'] == 'Whole_Blood']
    
    # Initialize with DataFrame
    sor = SplicingOutlierResult(
        df_mmsplice=df_mmsplice, 
        df_spliceai=df_spliceai, 
        gene_tpm=gene_tpm
    )
    assert sor.df_mmsplice.shape[0] > 0
    assert sor.df_spliceai.shape[0] > 0

    # Initialize with str
    sor2 = SplicingOutlierResult(
        df_mmsplice=mmsplice_path, 
        df_spliceai=spliceai_path, 
        gene_tpm=gene_tpm
    )
    assert sor2.df_mmsplice.shape[0] > 0
    assert sor2.df_spliceai.shape[0] > 0
    
    # Initialize with spliceai only
    sor = SplicingOutlierResult(
        df_spliceai=df_spliceai, 
        gene_map=gene_map,
        gene_tpm=gene_tpm
    )
    
    assert sor.df_spliceai.shape[0] > 0
    assert sor.df_mmsplice is None
    
    # Initialize with mmsplice only
    sor = SplicingOutlierResult(
        df_mmsplice=df_mmsplice
    )
    
    assert sor.df_spliceai is None
    assert sor.df_mmsplice.shape[0] > 0
    
    # Initialize with mmsplice_cat
    sor3 = SplicingOutlierResult(
        df_mmsplice=mmsplice_path, 
        df_spliceai=spliceai_path, 
        df_mmsplice_cat=mmsplice_cat_path, 
        gene_tpm=gene_tpm
    )
    assert sor3.df_mmsplice.shape[0] > 0
    assert sor3.df_spliceai.shape[0] > 0
    
    # Initialize with mmsplice_cat only
    sor = SplicingOutlierResult(
        df_mmsplice_cat=mmsplice_cat_path
    )
    
    assert sor.df_spliceai is None
    assert sor.df_mmsplice is None
    assert sor.df_mmsplice_cat.shape[0] > 0
    
    
def test_write_sample_csv():   
    vcf = MultiSampleVCF(multi_vcf_file)
    variant_queryable = vcf.query_all()
    variant_queryable.to_sample_csv(var_samples_path)

def test_tissues(outlier_results):
    assert sorted(outlier_results.df_mmsplice['tissue'].unique()) == sorted(
        ['Testis', 
        #  'Lung'
         ])

def test_splicing_outlier_result_add_spliceai(outlier_dl, outlier_dl_multi, df_var_samples, outlier_model):
    # single sample vcf
    results = outlier_model.predict_on_dataloader(outlier_dl)
    results.add_spliceai(spliceai_path, gene_map_path)
    assert results.df_spliceai.shape[0] > 0
    assert 'delta_score' in results.df_spliceai.columns
    # multi sample vcf
    results = outlier_model.predict_on_dataloader(outlier_dl_multi)
    results.add_spliceai(spliceai_path, gene_map_path)
    assert results.df_spliceai.shape[0] > 0
    assert 'delta_score' in results.df_spliceai.columns


def test_splicing_outlier_result_add_samples(outlier_dl, outlier_dl_multi, df_var_samples, outlier_model):
    # TODO: spliceai_path has no samples here
    results = outlier_model.predict_on_dataloader(outlier_dl_multi)
    results.add_spliceai(spliceai_path, gene_map_path)
    
    variants_mmsplice = set(results.df_mmsplice.set_index(['variant']).index)
    variants_spliceai = set(results.df_spliceai.set_index(['variant']).index)
    variants = set(df_var_samples.set_index(['variant']).index)
    samples_mmsplice = set(df_var_samples.set_index(['variant']).loc[variants_mmsplice.intersection(variants)]['sample'])
    samples_spliceai = set(df_var_samples.set_index(['variant']).loc[variants_spliceai.intersection(variants)]['sample'])
    
    results.add_samples(df_var_samples)
    assert len(samples_mmsplice.difference(set(results.df_mmsplice['sample'].values))) == 0
    assert len(samples_spliceai.difference(set(results.df_spliceai['sample'].values))) == 0
    
    
def test_splicing_outlier_result_init_add_samples(gene_tpm, df_var_samples):
    df_mmsplice = pd.read_csv(mmsplice_path)
    df_spliceai = pd.read_csv(spliceai_path)

    sor = SplicingOutlierResult(
        df_mmsplice=df_mmsplice, 
        df_spliceai=df_spliceai, 
        df_var_samples = df_var_samples,
    )
    
    sor2 = SplicingOutlierResult(
        df_mmsplice=df_mmsplice, 
        df_spliceai=df_spliceai, 
    )
    sor2.add_samples(df_var_samples)
    
    assert sor.df_mmsplice.equals(sor2.df_mmsplice)
    assert sor.df_spliceai.equals(sor2.df_spliceai)
    

def test_splicing_outlier_result_psi(outlier_results):
    results = outlier_results.psi5
    assert all(results.psi5.df_mmsplice['event_type'] == 'psi5')

    results = outlier_results.psi3
    assert all(results.psi3.df_mmsplice['event_type'] == 'psi3')


def test_splicing_outlier_result_splice_site(outlier_results):
    assert sorted(outlier_results.splice_site.index) \
        == sorted(set(outlier_results.df_mmsplice.set_index(['splice_site', 'gene_id', 'tissue']).index))


def test_splicing_outlier_result_gene_mmsplice(outlier_results, outlier_results_multi):
    assert sorted(set(outlier_results.gene_mmsplice.index)) \
        == sorted(set(outlier_results.df_mmsplice.set_index(['gene_id', 'tissue']).index))

    assert sorted(set(outlier_results_multi.gene_mmsplice.index)) \
        == sorted(set(outlier_results_multi.df_mmsplice.set_index(['gene_id', 'tissue', 'sample']).index))
    # assert sorted(set(outlier_results_multi.gene_mmsplice.index)) \
    #     == sorted(set(outlier_results_multi._explode(outlier_results_multi.df_mmsplice, 
    #                                                  col='samples', new_name='sample').set_index(
    #                                                      ['gene_id', 'sample', 'tissue']
    #                                                      ).index))

def test_splicing_outlier_result_gene_mmsplice_cat(outlier_dl_multi, outlier_results, cat_dl, outlier_model, df_var_samples):
    results = outlier_model.predict_on_dataloader(outlier_dl_multi)
    results.add_samples(df_var_samples)
    results.infer_cat(cat_dl)
    
    assert results.df_mmsplice_cat is not None
    assert 'tissue_cat' in results.df_mmsplice_cat.columns
    
    # all missing junctions do not have variant in vicinity (no mmsplice predictions either)
    df = results.df_mmsplice_cat[results.df_mmsplice_cat['tissue_cat'] == cat_dl[0].ct.name]
    common_junctions = cat_dl[0].common_junctions3[0].union(cat_dl[0].common_junctions5[0])
    assert len(set(results.df_mmsplice['junction']).intersection(common_junctions.difference(df.index.get_level_values('junction')))) == 0

def test_splicing_outlier_result_gene_spliceai(outlier_results, outlier_results_multi, gene_map, gene_tpm, df_var_samples):
    outlier_results.gene_map = gene_map
    outlier_results.add_spliceai(spliceai_path, gene_map_path)
    outlier_results.df_spliceai = outlier_results.df_spliceai[
        ~outlier_results.df_spliceai['gene_id'].isna()
    ]
    assert sorted(set(outlier_results.gene_spliceai.index)) \
        == sorted(set(outlier_results.df_spliceai.set_index(['gene_id']).index))

    outlier_results_multi.gene_map = gene_map
    outlier_results_multi.add_spliceai(spliceai_path, gene_map_path)
    outlier_results_multi.df_spliceai = outlier_results_multi.df_spliceai[
        ~outlier_results_multi.df_spliceai['gene_id'].isna()
    ]
    outlier_results_multi.add_samples(df_var_samples)
    assert sorted(set(outlier_results_multi.gene_spliceai.index)) \
        == sorted(set(outlier_results_multi.df_spliceai.set_index(['gene_id', 'sample']).index))
        
    df_spliceai_gene_no_tissue = outlier_results_multi.gene_spliceai.copy()
    outlier_results_multi.gene_tpm = gene_tpm
    outlier_results_multi.df_spliceai = None
    outlier_results_multi.add_spliceai(spliceai_path, gene_map_path)
    outlier_results_multi._add_tissue_info_to_spliceai()
    outlier_results_multi.df_spliceai = outlier_results_multi._df_spliceai_tissue #store spliceai_path tissue in spliceai_path
    assert 'tissue' in outlier_results_multi.df_spliceai.columns
    
    assert sorted(set(outlier_results_multi.gene_spliceai.index)) \
        == sorted(set(df_spliceai_gene_no_tissue.index))


def test_splicing_outlier_result_absplice_input_dna(outlier_dl, outlier_dl_multi, df_var_samples, outlier_model, gene_map, gene_tpm):
    results = outlier_model.predict_on_dataloader(outlier_dl_multi)
    results.gene_map = gene_map
    results.gene_tpm = gene_tpm
    results.add_spliceai(spliceai_path, gene_map)
    results.add_samples(df_var_samples)
    
    df_spliceai = results._add_tissue_info_to_spliceai()
    indices_mmsplice = results.df_mmsplice.set_index(['variant', 'gene_id', 'tissue', 'sample']).index.unique()
    indices_spliceai = df_spliceai.set_index(['variant', 'gene_id', 'tissue', 'sample']).index.unique()
    indices_all = indices_mmsplice.union(indices_spliceai)
    
    assert results.absplice_dna_input.shape[0] > 0
    assert len(set(results.absplice_dna_input.index).difference(indices_all)) == 0
    
    assert results.df_mmsplice_cat is None

def test_splicing_outlier_result_absplice_input_rna(outlier_dl, outlier_dl_multi, df_var_samples, outlier_model, gene_map, gene_tpm, cat_dl):
    results = outlier_model.predict_on_dataloader(outlier_dl_multi)
    results.gene_map = gene_map
    results.gene_tpm = gene_tpm
    results.add_spliceai(spliceai_path, gene_map)
    results.add_samples(df_var_samples)
    results.infer_cat(cat_dl)
    
    df_spliceai = results._add_tissue_info_to_spliceai()
    indices_mmsplice = results.df_mmsplice.set_index(['variant', 'gene_id', 'tissue', 'sample']).index.unique()
    indices_spliceai = df_spliceai.set_index(['variant', 'gene_id', 'tissue', 'sample']).index.unique()
    indices_all = indices_mmsplice.union(indices_spliceai)
    
    assert results.absplice_rna_input.shape[0] > 0
    assert len(set(results.absplice_rna_input.index).difference(indices_all)) == 0
    
    assert results.df_mmsplice_cat is not None
    assert len(set(['delta_score', 'delta_psi', 'delta_psi_cat']).difference(results.absplice_rna_input.columns)) == 0

    
def test_splicing_outlier_result_predict_absplice_dna(outlier_dl, outlier_dl_multi, df_var_samples, outlier_model, gene_map, gene_tpm):
    results = outlier_model.predict_on_dataloader(outlier_dl_multi)
    results.gene_map = gene_map
    results.gene_tpm = gene_tpm
    results.add_spliceai(spliceai_path, gene_map_path)
    results.add_samples(df_var_samples)
    
    results.predict_absplice_dna()
    assert 'AbSplice_DNA' in results.absplice_dna.columns
    
    
def test_splicing_outlier_result_predict_absplice_rna(outlier_dl, outlier_dl_multi, df_var_samples, outlier_model, gene_map, gene_tpm, cat_dl):
    results = outlier_model.predict_on_dataloader(outlier_dl_multi)
    results.gene_map = gene_map
    results.gene_tpm = gene_tpm
    results.add_spliceai(spliceai_path, gene_map_path)
    results.add_samples(df_var_samples)
    results.infer_cat(cat_dl)
    
    results.predict_absplice_rna()
    assert 'AbSplice_RNA' in results.absplice_rna.columns
    
    
def test_splicing_outlier_result_gene_absplice_dna(outlier_dl, outlier_dl_multi, df_var_samples, outlier_model, gene_map, gene_tpm):
    results = outlier_model.predict_on_dataloader(outlier_dl_multi)
    results.gene_map = gene_map
    results.gene_tpm = gene_tpm
    results.add_spliceai(spliceai_path, gene_map_path)
    results.add_samples(df_var_samples)
    
    results.predict_absplice_dna()
    assert 'variant' in results.absplice_dna.index.names
    assert 'variant' not in results.gene_absplice_dna.index.names
    assert 'AbSplice_DNA' in results.gene_absplice_dna.columns
    
    
def test_splicing_outlier_result_gene_absplice_rna(outlier_dl, outlier_dl_multi, df_var_samples, outlier_model, gene_map, gene_tpm, cat_dl):
    results = outlier_model.predict_on_dataloader(outlier_dl_multi)
    results.gene_map = gene_map
    results.gene_tpm = gene_tpm
    results.add_spliceai(spliceai_path, gene_map_path)
    results.add_samples(df_var_samples)
    results.infer_cat(cat_dl)
    
    results.predict_absplice_rna()
    assert 'variant' in results.absplice_rna_input.index.names
    assert 'variant' not in results.gene_absplice_rna.index.names
    assert 'AbSplice_RNA' in results.gene_absplice_rna.columns
    
      
def test_splicing_outlier_complete_dna(gene_map, gene_tpm, df_var_samples):
    
    results = SplicingOutlierResult(
        df_mmsplice = mmsplice_path,
        df_spliceai = spliceai_path,
        gene_map = gene_map,
        gene_tpm = gene_tpm,
    )
    
    results.add_samples(df_var_samples)
    results.predict_absplice_dna()
    
    assert results.absplice_dna.shape[0] > 0 
    assert 'AbSplice_DNA' in results.absplice_dna.columns
    
def test_splicing_outlier_complete_rna(gene_map, gene_tpm, df_var_samples):
    
    results = SplicingOutlierResult(
        df_mmsplice = mmsplice_path,
        df_spliceai = spliceai_path,
        df_mmsplice_cat = mmsplice_cat_path,
        gene_map = gene_map,
        gene_tpm = gene_tpm,
    )
    
    results.add_samples(df_var_samples)
    results.predict_absplice_rna()
    
    assert results.absplice_rna.shape[0] > 0 
    assert 'AbSplice_RNA' in results.absplice_rna.columns
     
     
def test_splicing_outlier_complete_dna_init(gene_map, gene_tpm, df_var_samples):
    
    results = SplicingOutlierResult(
        df_mmsplice = mmsplice_path,
        df_spliceai = spliceai_path,
        gene_map = gene_map,
        gene_tpm = gene_tpm,
    )
    
    results.add_samples(df_var_samples)
    df_absplice_dna_input = results.absplice_dna_input
    
    results_init = SplicingOutlierResult(
        df_absplice_dna_input = df_absplice_dna_input
    )
    assert results_init.absplice_dna_input.shape[0] > 0
    
def test_splicing_outlier_complete_rna_init():
    
    results = SplicingOutlierResult(
        df_mmsplice = mmsplice_path,
        df_spliceai = spliceai_path,
        gene_map = gene_map_path,
        gene_tpm = gene_tpm_path,
    )
    
    results.add_samples(var_samples_path)
    df_absplice_dna_input = results.absplice_dna_input
    
    results_init = SplicingOutlierResult(
        df_absplice_dna_input = df_absplice_dna_input,
        df_mmsplice_cat = mmsplice_cat_path,
    )
    assert results_init.absplice_rna_input.shape[0] > 0
    
def test_splicing_outlier_result__add_tissue_info_to_spliceai(outlier_dl, outlier_dl_multi, outlier_model, gene_map, gene_tpm, df_var_samples):
    results = outlier_model.predict_on_dataloader(outlier_dl_multi)
    results.gene_map = gene_map
    results.gene_tpm = gene_tpm
    results.add_spliceai(spliceai_path, gene_map)
    results.add_samples(df_var_samples)
    
    df_spliceai_tissue = results._add_tissue_info_to_spliceai()
    
    assert len(set(results.df_mmsplice['tissue']).difference(set(df_spliceai_tissue['tissue']))) == 0
    assert len(set(df_spliceai_tissue['tissue'])) > 0
    
    # df_spliceai_tpm = results._add_tissue_info_to_spliceai()
    
    # # add tissue info without gene_tpm provided
    # results.gene_tpm = None
    # df_spliceai_no_tpm = results._add_tissue_info_to_spliceai()
    
    # assert 'gene_tpm' in df_spliceai_tpm.columns
    # assert 'gene_tpm' not in df_spliceai_no_tpm.columns
    
    # spliceai_tpm_index = df_spliceai_tpm.set_index(['variant', 'gene_id', 'tissue', 'sample']).index.unique()
    # spliceai_no_tpm_index = df_spliceai_no_tpm.set_index(['variant', 'gene_id', 'tissue', 'sample']).index.unique()
    
    # assert len(spliceai_tpm_index[~spliceai_tpm_index.get_level_values('tissue').isna()]\
    #     .difference(spliceai_no_tpm_index)) == 0
    # # Some gene_ids are NA, because could not be found in gene_map (e.g. FakeGene)
    # # assert len(spliceai_no_tpm_index.difference(spliceai_tpm_index)) >= 0
    # assert len(spliceai_no_tpm_index[~spliceai_no_tpm_index.get_level_values('gene_id').isna()]\
    #     .difference(spliceai_tpm_index[~spliceai_tpm_index.get_level_values('gene_id').isna()])) >= 0
    # assert len(spliceai_tpm_index) == df_spliceai_tpm.shape[0]
    # assert len(spliceai_no_tpm_index) == spliceai_no_tpm_index.shape[0]
        

def test_outlier_results_multi_vcf(outlier_dl_multi, outlier_model, df_var_samples):
    results = outlier_model.predict_on_dataloader(outlier_dl_multi)
    results.add_samples(df_var_samples)
    # assert results.gene_mmsplice.index.names == ['gene_name', 'sample', 'tissue']
    # assert sorted(results.gene_mmsplice.index.tolist()) == sorted([
    #     ('BRCA1', 'NA00002', 'Lung'),
    #     ('BRCA1', 'NA00003', 'Lung'),
    #     ('BRCA1', 'NA00002', 'Testis'),
    #     ('BRCA1', 'NA00003', 'Testis'),
    # ])
    assert results.gene_mmsplice.index.names == ['gene_id', 'tissue', 'sample']
    assert sorted(results.gene_mmsplice.reset_index().set_index(['gene_name', 'sample', 'tissue']).index.tolist()) == sorted([
        # ('BRCA1', 'NA00002', 'Lung'),
        # ('BRCA1', 'NA00003', 'Lung'),
        ('BRCA1', 'NA00002', 'Testis'),
        ('BRCA1', 'NA00003', 'Testis'),
    ])

# # def test_outlier_results_filter_samples_with_RNA_seq(outlier_results_multi, outlier_model):
# def test_outlier_results_filter_samples_with_RNA_seq(outlier_dl, outlier_dl_multi, df_var_samples, outlier_model, gene_map, gene_tpm):
#     # TODO: after filter_samples_with_RNA_seq spliceai_path contains tissue info (maybe remove)
#     samples_for_tissue = {
#         'Testis': ['NA00002'],
#         'Lung': ['NA00002', 'NA00003']
#     }

#     results = outlier_model.predict_on_dataloader(outlier_dl_multi)
#     results.gene_map = gene_map
#     results.gene_tpm = gene_tpm
#     results.add_spliceai(spliceai_path, gene_map_path)
#     results.add_samples(df_var_samples)
    
#     # results = outlier_results_multi
#     # results.add_spliceai(spliceai_path, gene_mapping=False)
#     # assert results.df_mmsplice[['tissue', 'sample']].set_index('tissue').to_dict() == \
#     assert results.df_mmsplice[['tissue', 'sample']].groupby('tissue')['sample'].apply(lambda x: ';'.join(sorted(list(set(x))))).to_dict() == \
#         {
#             # 'Lung': 'NA00002;NA00003', 
#             'Testis': 'NA00002;NA00003'}
        
#     df_spliceai_tpm = results._add_tissue_info_to_spliceai()
#     assert df_spliceai_tpm[['tissue', 'sample']].groupby('tissue')['sample'].apply(lambda x: ';'.join(sorted(list(set(x))))).to_dict() == \
#         {
#             # 'Lung': 'NA00002;NA00003', 
#             'Testis': 'NA00002;NA00003'}

#     results.filter_samples_with_RNA_seq(samples_for_tissue)

#     assert results.df_mmsplice[['tissue', 'sample']].groupby('tissue')['sample'].apply(lambda x: ';'.join(sorted(list(set(x))))).to_dict() == \
#         {
#             # 'Lung': 'NA00002;NA00003', 
#             'Testis': 'NA00002'}
#     assert results.df_spliceai[['tissue', 'sample']].groupby('tissue')['sample'].apply(lambda x: ';'.join(sorted(list(set(x))))).to_dict() == \
#         {
#             # 'Lung': 'NA00002;NA00003', 
#             'Testis': 'NA00002'}
    

def test_outlier_results_infer_cat(outlier_dl_multi, outlier_results, cat_dl, outlier_model, df_var_samples):

    results = outlier_model.predict_on_dataloader(outlier_dl_multi)
    results.add_samples(df_var_samples)
    results.infer_cat(cat_dl)

    assert sorted(results.df_mmsplice_cat.columns.tolist()) == sorted([
        'event_type', 'variant', 'Chromosome', 'Start', 'End', 'Strand',
        'events', 'splice_site', 'ref_psi', 'k', 'n', 'median_n',
        'novel_junction', 'weak_site_acceptor', 'weak_site_donor',
        'gene_name', 'transcript_id', 'gene_type', 'gene_tpm',
        'delta_psi', 'delta_logit_psi',
        'ref_acceptorIntron', 'ref_acceptor', 'ref_exon', 'ref_donor', 'ref_donorIntron',
        'alt_acceptorIntron', 'alt_acceptor', 'alt_exon', 'alt_donor', 'alt_donorIntron',
        'tissue_cat', 'count_cat', 'psi_cat', 'ref_psi_cat', 'k_cat', 'n_cat', 'median_n_cat',
        'delta_logit_psi_cat', 'delta_psi_cat'])

    # Note: previously max aggregation was done in gene property (would have to do aggregation for delta_psi and delta_psi_cat)
    # assert sorted(results.gene_mmsplice.columns.tolist()) == sorted([
    #     'junction', 'event_type', 'variant', 'Chromosome', 'Start', 'End', 'Strand',
    #     'events', 'splice_site', 'ref_psi', 'k', 'n', 'median_n',
    #     'novel_junction', 'weak_site_acceptor', 'weak_site_donor',
    #     'gene_id', 'transcript_id', 'gene_type', 'gene_tpm',
    #     'delta_psi', 'delta_logit_psi',
    #     'ref_acceptorIntron', 'ref_acceptor', 'ref_exon', 'ref_donor', 'ref_donorIntron',
    #     'alt_acceptorIntron', 'alt_acceptor', 'alt_exon', 'alt_donor', 'alt_donorIntron',
    #     'tissue_cat', 'count_cat', 'psi_cat', 'ref_psi_cat', 'k_cat', 'n_cat', 'median_n_cat',
    #     'delta_logit_psi_cat', 'delta_psi_cat'])

    assert results.df_mmsplice_cat.loc[(
        '17:41201211-41203079:-', 'ENSG00000012048', 'Testis', 'NA00002',)] is not None

    
# # DEBUG
# import pytest
# import pandas as pd
# import numpy as np
# from kipoiseq.extractors.vcf import MultiSampleVCF
# # from kipoiseq.extractors.vcf_query import to_sample_csv
# from splicing_outlier_prediction import SpliceOutlier, SpliceOutlierDataloader, CatInference
# from splicing_outlier_prediction.ensemble import train_model_ebm
# from conftest import fasta_file, vcf_file, multi_vcf_file, multi_vcf_samples, \
#     ref_table5_kn_testis, ref_table3_kn_testis,  \
#     ref_table5_kn_lung, ref_table3_kn_lung, \
#     combined_ref_tables5_testis_lung, combined_ref_tables3_testis_lung, \
#     count_cat_file_lymphocytes,  count_cat_file_blood, \
#     spliceai_path, pickle_DNA, pickle_DNA_CAT
    
# from kipoiseq.extractors.vcf_query import VariantIntervalQueryable
# from kipoiseq.dataclasses import Variant, Interval


# # @pytest.fixture
# # def variant_queryable():
# #     vcf = MultiSampleVCF(vcf_file)
# #     return VariantIntervalQueryable(vcf, [
# #         (
# #             [
# #                 Variant('chr1', 12, 'A', 'T'),
# #                 Variant('chr1', 18, 'A', 'C', filter='q10'),
# #             ],
# #             Interval('chr1', 10, 20)
# #         ),
# #         (
# #             [
# #                 Variant('chr2', 120, 'AT', 'AAAT'),
# #             ],
# #             Interval('chr2', 110, 200)
# #         )
# #     ])

# def test_write_vcf_condensed():
#     # variant_queryable.to_vcf(vcf_file_condensed, remove_samples=True, clean_info=True)
#     # [x.__str__() for x in MultiSampleVCF(vcf_file).query_all().filter(lambda variant: variant.pos in [41201201, 41279042, 41276032])]
#     MultiSampleVCF(multi_vcf_file).query_all().filter(lambda variant: variant.pos in [41201201, 41279042, 41276032]).to_vcf(vcf_file.replace('.gz', ''), remove_samples=True, clean_info=True)
    
#     # [x for x in VariantIntervalQueryable(vcf_file, [([Variant('chr17', 41201201, 'TTC', 'CA')], Interval('chr17', 41201101, 41201209))])]
#     # VariantIntervalQueryable(vcf_file, [([Variant('chr17', 41201201, 'TTC', 'CA')], Interval('chr17', 41201101, 41201209))]).to_vcf(vcf_file_condensed, remove_samples=True)
    
# # def tabix_vcf():
# #     bgzip vcf_file.replace('.gz', '')
# #     tabix vcf_file