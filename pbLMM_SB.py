import statsmodels.formula.api as smf
import pandas as pd
from statsmodels.stats.multitest import multipletests
import numpy as np

class Defaults:

    def __init__(self) -> None:

        self.MasterProteinAccession = "Master Protein Accessions"
        self.sequence = 'Annotated Sequence'
        self.AbundanceColumn = "Abundance:"
        self.file_id = "File ID"
        self.contaminant = 'Contaminant'
        self.modifications = "Modifications"

    def processor(self, list_of_df, function, *args, **kwargs):
        '''Processor function that applies a certain function to a list of dataframes, to allow rapid batch processing.
        Returns a list of processed dataframes
        '''
        results = []
        for count, value in enumerate(list_of_df):
            results.append(function(value, *args, **kwargs))
        return results

    def get_channels(self, input_file, custom=None):
        '''Returns an array of all column names where Abundances are stored. Accesses Defaults object, but also custom string can be applied. However, its recommended
        to change defaults.AbundanceColumn for compatibility with all other functions. Its basically just a wrapper for python list comprehension.
        '''
        if custom is None:
            channels = [
                col for col in input_file.columns if self.AbundanceColumn in col]
        else:
            channels = [col for col in input_file.columns if custom in col]

        if channels == []:
            channels = [col for col in input_file.columns if 'Abundance' in col]
        return channels


class Rollup:
    def __init__(self, defaults=Defaults()):
        self.defaults = defaults

    def protein_rollup_sum(self, input_file, channels):
        '''
        This function takes Peptide level (or PSM) dataframes and performs a sum based rollup to protein level.
        the channels variable takes an array of column names that contain the quantifictions. You can create such an
        array via this command:
        channels = [col for col in PSM.columns if 'Abundance:' in col]

        mpa1 variable contains a string that is included in the Accession column. The function will search for the column containing the string
        and use it for rollup.

        Returns Protein level DF.
        '''

        mpa1 = self.defaults.MasterProteinAccession
        print('Calculate Protein quantifications from PSM')
        mpa = [col for col in input_file.columns if mpa1 in col]
        mpa = mpa[0]

        PSM_grouped = input_file.groupby(by=[mpa])
        result = {}
        for group in PSM_grouped.groups:
            temp = PSM_grouped.get_group(group)
            sums = temp[channels].sum()
            result[group] = sums

        protein_df = pd.DataFrame.from_dict(
            result, orient='index', columns=channels)
        print("Combination done")

        return protein_df

    def protein_rollup_median(self, input_file, channels):
        '''
        This function takes Peptide level (or PSM) dataframes and performs a Median based rollup to protein level.
        the channels variable takes an array of column names that contain the quantifictions. You can create such an
        array via this command:
        channels = [col for col in PSM.columns if 'Abundance:' in col]

        mpa1 variable contains a string that is included in the Accession column. The function will search for the column containing the string
        and use it for rollup.

        Returns Protein level DF.
        '''
        mpa1 = self.defaults.MasterProteinAccession
        print('Calculate Protein quantifications from PSM')
        mpa = [col for col in input_file.columns if mpa1 in col]
        mpa = mpa[0]

        PSM_grouped = input_file.groupby(by=[mpa])
        result = {}
        for group in PSM_grouped.groups:
            temp = PSM_grouped.get_group(group)
            sums = temp[channels].median()
            result[group] = sums

        protein_df = pd.DataFrame.from_dict(
            result, orient='index', columns=channels)
        print("Combination done")

        return protein_df

    def protein_rollup_mean(self, input_file, channels):
        '''
        This function takes Peptide level (or PSM) dataframes and performs a Mean based rollup to protein level.
        the channels variable takes an array of column names that contain the quantifictions. You can create such an
        array via this command:
        channels = [col for col in PSM.columns if 'Abundance:' in col]

        mpa1 variable contains a string that is included in the Accession column. The function will search for the column containing the string
        and use it for rollup.

        Returns Protein level DF.
        '''
        mpa1 = self.defaults.MasterProteinAccession
        print('Calculate Protein quantifications from PSM')
        mpa = [col for col in input_file.columns if mpa1 in col]
        mpa = mpa[0]

        PSM_grouped = input_file.groupby(by=[mpa])
        result = {}
        for group in PSM_grouped.groups:
            temp = PSM_grouped.get_group(group)
            sums = temp[channels].mean()
            result[group] = sums

        protein_df = pd.DataFrame.from_dict(
            result, orient='index', columns=channels)
        print("Combination done")

        return protein_df

class HypothesisTesting:
    # Calculate two-sided t-test statistics for pairwise comparisons

    def __init__(self, defaults = Defaults()):
        self.pair_names = []
        self.comparison_data = {}
        self.defaults=defaults

    def peptide_based_lmm(self, input_file, conditions, drop_missing=False, techreps=None, plexes=None, norm=None, pairs=None):

        columns =  [
            self.defaults.sequence,
            self.defaults.MasterProteinAccession,
            self.defaults.AbundanceColumn,
        ]
        self.pair_names = []
        channels = [col for col in input_file.columns if columns[2] in col]
        if channels == []:
            channels = [col for col in input_file.columns if 'Abundance' in col]

        if norm is not None:
            #input_file = norm(Preprocessing(self.defaults), input_file, channels)
            pass
        else:
            if drop_missing == True:
                input_file = input_file.dropna(subset=channels)
            else:
                pass
            print('No Normalization applied')
        # Protein level quantifications
        roll = Rollup(self.defaults)
        protein_data = roll.protein_rollup_sum(
            input_file=input_file, channels=channels)
        # Prepare Peptide data for LMM
        Peptides_for_LM = input_file[channels]

        sequence = [col for col in input_file.columns if columns[0] in col]

        sequence = sequence[0]

        Peptides_for_LM['Sequence'] = input_file[sequence]

        Acc = [col for col in input_file.columns if columns[1] in col]

        Acc = Acc[0]

        Peptides_for_LM['Accession'] = input_file[Acc]

        melted_Peptides = Peptides_for_LM.melt(
            id_vars=['Accession', 'Sequence'], value_vars=channels)
        # Replace column names with conditions

        if  techreps == None:
            pass
        else:
            melted_Peptides['Techreps' ] =melted_Peptides['variable']
            melted_Peptides['Techreps'].replace(to_replace=channels,
                                                value=techreps, inplace=True)

        if plexes == None:
            pass
        else:
            melted_Peptides['Multiplex' ] =melted_Peptides['variable']
            melted_Peptides['Multiplex'].replace(to_replace=channels,
                                                 value=plexes, inplace=True)

        print('Total Number of Datapoints: ', len(melted_Peptides.index))

        melted_Peptides['variable'].replace(to_replace=channels,
                                            value=conditions, inplace=True)

        if pairs != None:
            for pair in pairs:
                if pair[0][0] < pair[1][0]: # pair = ['1CDDO', '0DMSO'] pair = ['CDDO', 'DMSO'] to assing FC correctly
                    decisionOfColumnName = -1
                else:
                    decisionOfColumnName = 1

                print(pair, 'and decision:', decisionOfColumnName)

                temp = melted_Peptides[(melted_Peptides['variable'].str.fullmatch(pair[0])) | (
                    melted_Peptides['variable'].str.fullmatch(pair[1]))]

                temp['value'] = np.log2(temp['value'])
                temp = temp.dropna()

                grouped = temp.groupby(by=['Accession'])
                result_dict = {}
                fold_changes = []
                counter = 0

                for i in grouped.groups:

                    temp2 = grouped.get_group(i)

                    vc = {'Sequence': '0+Sequence'}

                    # Base model
                    model_form = "value ~ variable"

                    model = smf.mixedlm(
                        model_form, temp2, groups='Sequence', vc_formula=vc)

                    try:
                        result = model.fit()
                        if counter == 0:
                            # print(model_form)
                            # print(result.summary())
                            counter = counter + 1
                        else:
                            pass

                        fc = result.params[1] * decisionOfColumnName  # CDDO and DMSO change the order 1CDDO and 1DMSO
                        pval = result.pvalues[1]

                        fold_changes.append(fc)
                        result_dict[i] = pval
                    except:
                        pass

                result_df_peptides_LMM = pd.DataFrame.from_dict(
                    result_dict, orient='index', columns=['p_value'])

                result_df_peptides_LMM['fold_change'] = np.array(fold_changes)

                # Multiple testing correction:
                result_df_peptides_LMM['p_value'] = result_df_peptides_LMM['p_value'].fillna(
                    value=1)
                pvals = result_df_peptides_LMM['p_value'].to_numpy()

                reject, pvals_corrected, a, b = multipletests(
                    pvals, method='fdr_bh')

                result_df_peptides_LMM['q_value'] = pvals_corrected

                cols = ['fold_change', 'p_value', 'q_value']  # Changing columns index
                result_df_peptides_LMM = result_df_peptides_LMM[cols]

                result_df_peptides_LMM = result_df_peptides_LMM.rename(columns={'fold_change': f'log2({pair[0]}/{pair[1]})',
                                                                                'p_value': f'p_value {pair[0]}/{pair[1]}',
                                                                                'q_value': f'q_value {pair[0]}/{pair[1]}'})
                # Changing Column names




                # comparison = '_' + str(pair[1]) + '_vs_' + str(pair[0])
                # comparison = f'{pair[0]}/{pair[1]}' #log2(6h 8mM/Cont) p_value 6h 8mM/Cont q_value 6h 8mM/Cont
                # self.pair_names.append(comparison)
                # print(result_df_peptides_LMM)
                # result_df_peptides_LMM = result_df_peptides_LMM.add_suffix(
                #     comparison)
                # print(result_df_peptides_LMM)

                protein_data = protein_data.join(result_df_peptides_LMM)
            # self.comparison_data = self.export_comparison_strings()

        # print(self.comparison_data )
        return protein_data