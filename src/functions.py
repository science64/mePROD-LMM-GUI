import warnings
import DynaTMT as DynaTMT
import PBLMM
from PBLMM import HypothesisTesting, Defaults
import requests
import pandas as pd

warnings.filterwarnings("ignore")


class mePROD:
    def __init__(self, location, randomReportName):
        self.mito_database = pd.read_excel('./files/database.xlsx')
        self.geneNameDatabase = pd.read_excel('./files/Uniprot_database_2021.xlsx')
        self.reports = open(f'{location}/{randomReportName}.txt', 'w+')
        self.status = ''

    def engine(self, psms, conditions, pairs, normalization_type, statistics_type, ms_level='MS2'):
        """
        Main processing engine supporting MS2 and MS3 workflows.

        MS2: IT adjustment -> normalization -> extract heavy -> baseline correction -> statistics
        MS3: no IT adjustment, no baseline correction, uses PSMs_to_Peptide instead
        """
        channels = [col for col in psms.columns if 'Abundance:' in col]
        if channels == []:
            channels = [col for col in psms.columns if 'Abundance' in col]

        # to remove abundances to skip (empty channels) or boosters
        skip_terms = ['skip', 'boost', 'booster', 'mitobooster', 'wholecellbooster']
        s = 0
        for condition in conditions:
            if condition.lower() in skip_terms:
                psms.drop(channels[s], axis=1, inplace=True)
            s += 1

        conditions = [x for x in conditions if not any(term in str(x).lower() for term in skip_terms)]

        # Determine baseline index from conditions (needed for MS2)
        lower_conditions = [item.lower() for item in conditions]

        if ms_level == 'MS2':
            if 'light' in lower_conditions:
                baselineIndex = lower_conditions.index('light')
            elif "baseline" in lower_conditions:
                baselineIndex = lower_conditions.index("baseline")
            elif "base" in lower_conditions:
                baselineIndex = lower_conditions.index("base")
            elif "noise" in lower_conditions:
                baselineIndex = lower_conditions.index("noise")
            else:
                return 0
        elif ms_level == 'MS3':
            # For MS3, remove the baseline channel instead of correction
            baseline_keywords = ['light', 'baseline', 'base', 'noise']
            baseline_idx = None
            for kw in baseline_keywords:
                if kw in lower_conditions:
                    baseline_idx = lower_conditions.index(kw)
                    break

            if baseline_idx is not None:
                # Get updated channels after skip removal
                channels_updated = [col for col in psms.columns if 'Abundance:' in col]
                if channels_updated == []:
                    channels_updated = [col for col in psms.columns if 'Abundance' in col]
                # Remove the baseline channel column
                baseline_col = channels_updated[baseline_idx]
                psms.drop(baseline_col, axis=1, inplace=True)
                conditions.pop(baseline_idx)

        # Initialize DynaTMT processor (v2.9.4 API: takes data in constructor)
        process = DynaTMT.PD_input(psms)

        # Step 1: Filter PSMs (v2.9.4: filter_PSMs replaces filter_peptides)
        filtered_peptides = process.filter_PSMs(psms)

        if ms_level == 'MS2':
            # Step 2: IT adjustment (MS2 only)
            ITadjusted_peptides = process.IT_adjustment(filtered_peptides)
        else:
            # MS3: Skip IT adjustment
            ITadjusted_peptides = filtered_peptides

        self.reports.write('The number of total peptides: {}\n'.format(len(ITadjusted_peptides.index)))

        # Step 3: Normalization
        normFinal = ''
        if normalization_type == 'total':
            normFinal = process.total_intensity_normalisation(ITadjusted_peptides)
        elif normalization_type == 'TMM':
            normFinal = process.TMM(ITadjusted_peptides)
        elif normalization_type == 'median':
            normFinal = process.Median_normalisation(ITadjusted_peptides)

        # Step 4: Extract heavy peptides
        heavy = process.extract_heavy(normFinal)

        self.reports.write('The number of heavy peptides: {}\n'.format(len(heavy.index)))

        self.status = 'heavy'
        self.mito_count(heavy)

        if ms_level == 'MS2':
            # Step 5a (MS2): Baseline correction
            peptide_data = process.baseline_correction(heavy, threshold=5, i_baseline=baselineIndex, random=True)
        else:
            # Step 5b (MS3): PSMs to Peptide (no baseline correction)
            peptide_data = process.PSMs_to_Peptide(heavy)

        conditions = [i.strip() for i in conditions]
        conditions = [i.lstrip() for i in conditions]

        channels = [col for col in peptide_data.columns if 'Abundance:' in col]
        if channels == []:
            channels = [col for col in peptide_data.columns if 'Abundance' in col]
        columnDict = {channels[i]: conditions[i] for i in range(len(channels))}

        if pairs == [['']]:
            pairs = None

        if pairs is not None:
            defaults = Defaults()
            hypo = HypothesisTesting(defaults)
            if statistics_type == 'LMM':
                result = hypo.peptide_based_lmm(peptide_data, conditions=conditions, pairs=pairs)
            elif statistics_type == 'ttest':
                result = hypo.ttest(peptide_data, conditions=conditions, pairs=pairs)
        else:
            roll = PBLMM.Rollup()
            protein_data = roll.protein_rollup_sum(
                input_file=peptide_data, channels=channels)

            columnDict = {channels[i]: conditions[i] for i in range(len(channels))}
            protein_data = protein_data.rename(columns=columnDict)

            # Drop rows where the sum across the row is 0
            result = protein_data[protein_data.sum(axis=1) != 0]

        result = result.rename(columns=columnDict)
        self.reports.write('The number of heavy proteins: {}\n'.format(len(result.index)))

        result['Accession'] = result.index
        result['Gene Symbol'] = ''

        self.status = 'protein'
        self.mito_count(result)

        self.reports.close()

        # summary numbers
        print(f"# of PSMs: {len(psms.index)}")
        print(f"# of filtered PSMs: {len(filtered_peptides.index)}")
        print(f"# of processed peptides: {len(ITadjusted_peptides.index)}")
        print(f"# of normalized peptides: {len(normFinal.index)}")
        print(f"# of heavy peptides: {len(heavy.index)}")
        print(f"# of peptides after processing: {len(peptide_data.index)}")

        return result

    def GeneNameEngine(self, Data):
        # Convert the database to a dictionary for quicker lookups
        accession_to_gene = dict(zip(self.geneNameDatabase['Accession'], self.geneNameDatabase['Gene Symbol']))

        # Try to get the 'Master Protein Accessions' column, if not, get the 'Accession' column
        accession = Data.get('Master Protein Accessions', Data.get('Accession', pd.Series(dtype='object')))

        # Process the Accession numbers
        def process_accession(acc):
            if ';' in acc:
                return acc.split(';')[0]
            elif ' ' in acc:
                return acc.split(' ')[0]
            else:
                return acc

        # Fetch gene symbol
        def get_gene_symbol(final):
            if final in accession_to_gene:
                return accession_to_gene[final]
            else:
                try:
                    url = f'https://www.ebi.ac.uk/proteins/api/proteins/{final}'
                    req = requests.get(url)
                    result = req.json()
                    return result['gene'][0]['name']['value']
                except Exception:
                    return ''

        processed_accessions = accession.apply(process_accession)
        Data['Gene Symbol'] = processed_accessions.apply(get_gene_symbol)

        return Data

    def mito_human(self, Data):
        # Try to get the 'Master Protein Accessions' column, if not, get the 'Accession' column
        AccessionNum = Data.get('Master Protein Accessions', Data.get('Accession', pd.Series(dtype='object')))

        # Read the database
        MitoSymbol = set(self.mito_database['Human_Mitochondrial'])

        # Process the Accession numbers
        def process_accession(acc):
            if ';' in acc:
                return acc.split(';')[0]
            elif '-' in acc:
                return acc.split('-')[0]
            else:
                return acc

        processed_accessions = AccessionNum.apply(process_accession)

        # Check if each processed accession number is in MitoSymbol
        Data['MitoCarta3.0'] = processed_accessions.apply(lambda x: '+' if x in MitoSymbol else '')

        return Data

    def mito_count(self, Data):
        # Try to get the 'Master Protein Accessions' column, if not, get the 'Accession' column
        AccessionNum = Data.get('Master Protein Accessions', Data.get('Accession', pd.Series(dtype='object'))).astype(
            str)

        MitoSymbol_Set = set(self.mito_database['Human_Mitochondrial'].astype(str))

        # Process the Accession numbers
        def process_accession(acc):
            if ';' in acc:
                return acc.split(';')[0]
            elif '-' in acc:
                return acc.split('-')[0]
            else:
                return acc

        processed_accessions = AccessionNum.apply(process_accession)
        count_mito = sum(1 for acc in processed_accessions if acc in MitoSymbol_Set)

        if self.status == 'heavy':
            self.reports.write('The number of mitochondrial heavy peptides: {}\n'.format(count_mito))
        if self.status == 'protein':
            self.reports.write('The number of mitochondrial heavy proteins: {}\n'.format(count_mito))

        return

    def significantAssig(self, Data):
        # Get all columns with 'p_value' and 'q_value' in their names
        pvalue_columns = [col for col in Data.columns if 'p_value' in col]
        qvalue_columns = [col for col in Data.columns if 'q_value' in col]

        # Iterate over the columns
        for i in range(0, len(pvalue_columns)):
            pcol = pvalue_columns[i]

            # Create a new column name for each p_value column
            p_col_name = f'{pcol} < 0.05'

            # Assign '+' to rows where p_value is less than 0.05
            Data[p_col_name] = Data[pcol].apply(lambda x: '+' if x < 0.05 else '')

            if qvalue_columns != []:
                qcol = qvalue_columns[i]
                q_col_name = f'{qcol} < 0.05'
                Data[q_col_name] = Data[qcol].apply(lambda x: '+' if x < 0.05 else '')

        return Data
