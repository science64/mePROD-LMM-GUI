# mePROD-LMM-GUI  
  
A graphical user interface for analyzing proteomics data using linear mixed models (LMM) and t-tests, specifically designed for Multiplexed enhanced Protein Dynamic mass spectrometry (mePROD MS) experiments. Supports both **MS2** and **MS3** workflows.

## Versions

mePROD-LMM-GUI **v3.0.0** (2026-03-26)

DynaTMT-py **v2.9.4** (2026-03-19) — [GitHub](https://github.com/science64/DynaTMT)

PBLMM **v2.1.3** (2026-02-02) — [GitHub](https://github.com/science64/PBLMM)

## What's New in v3.0.0

- **MS2 / MS3 workflow selection** — choose your acquisition method directly in the GUI  
  - MS2: Injection time adjustment + baseline correction (as before)  
  - MS3: No IT adjustment, no baseline correction; uses `PSMs_to_Peptide` instead  
- **Updated DynaTMT integration** (v2.9.4) — new `PD_input` constructor API, `filter_PSMs()`, `PSMs_to_Peptide()`  
- **Updated PBLMM integration** (v2.1.3) — `HypothesisTesting(Defaults())` API, still supports both LMM and t-test  
- **Restructured project** — source code moved to `src/` folder; `main.py` remains at root as entry point  
- **Improved GUI layout** — uses grid-based layout with `LabelFrame` sections for better organization  
- **pandas <= 2.3.3** compatibility (no pandas v3 support)  

## Overview  
  
mePROD-LMM-GUI is a specialized tool for processing and analyzing proteomics data from mePROD experiments, focusing on protein synthesis measurements. The application provides a user-friendly interface for data normalization, statistical analysis, and identification of mitochondrial proteins.

Multiplexed enhanced Protein Dynamic mass spectrometry (mePROD MS) can be used for protein translation (mePROD) and mitochondrial protein import (mePROD^mt) MS results.  

## Features  
  
- **MS2 and MS3 Support**: Select your acquisition method; the app automatically applies the correct processing pipeline  
- **Data Processing**: Filter PSMs, adjust for injection time variations (MS2), and apply normalization  
- **Statistical Analysis**: Peptide-based linear mixed model (PBLMM) or unpaired t-tests  
- **Protein Annotation**: Annotate proteins with gene names using UniProt database  
- **Mitochondrial Protein Identification**: Identify mitochondrial proteins using MitoCarta 3.0 database  
- **Comprehensive Reporting**: Generate detailed Excel reports with analysis results  

## MS2 vs MS3 Workflow

| Feature | MS2 | MS3 |
|---------|-----|-----|
| IT Adjustment | **Required** | Not needed |
| Baseline Correction | **Required** | Not needed (baseline channel removed) |
| Co-isolation Interference | Higher | Lower |
| PSM → Peptide | Via `baseline_correction()` | Via `PSMs_to_Peptide()` |

## Project Structure

```
mePROD-LMM-GUI/
├── main.py                  # Entry point — run this
├── src/
│   ├── __init__.py
│   ├── gui.py               # Tkinter GUI (MyWindow class)
│   └── functions.py         # mePROD processing engine
├── files/
│   ├── database.xlsx         # MitoCarta 3.0 database
│   ├── Uniprot_database_2021.xlsx  # UniProt gene name mapping
│   └── icon.ico
├── condtions.txt            # Default conditions
├── pairs.txt                # Default pairs
├── requirements.txt
├── Example data/            # Example PSMs files
```

## System Requirements  
  
- Python 3.8 or higher
- tkinter (included with most Python installations)
- Git (for installing DynaTMT and PBLMM from GitHub)
  
## Installation  

### Step 1: Clone this repository

```bash
git clone https://github.com/science64/mePROD-LMM-GUI.git
cd mePROD-LMM-GUI
```

### Step 2: Create a virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Step 3: Install all dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages including DynaTMT (v2.9.4) and PBLMM (v2.1.3) directly from GitHub.

### Alternative: Install packages individually

```bash
pip install pandas==2.3.3 numpy matplotlib scipy statsmodels seaborn openpyxl requests
pip install git+https://github.com/science64/DynaTMT.git
pip install git+https://github.com/science64/PBLMM.git
```

## Usage  

### Running the Application

```bash
python main.py
```

### Step-by-Step

1. **Select MS Level**: Choose MS2 or MS3 depending on your acquisition method  
2. **Select Normalization**: Total intensity (default), Median, or TMM  
3. **Select Statistics**: Linear mixed model (default) or Unpaired t-test  
4. **Browse for PSMs file**: Load your PSM data file (`.txt` or `.xlsx`)  
5. **Enter output name**: Name for the results file  
6. **Configure conditions**: Comma-separated list (e.g., `Light,DMSO,DMSO,DMSO,Treatment,Treatment,Treatment,Boost`)  
7. **Configure pairs**: Semicolon-separated pairs (e.g., `Treatment/DMSO;Treatment2/DMSO`)  
8. **Click RUN** to process the data  
9. **Click Open Result** to view the Excel output  

## Configuration Files  

1. **Conditions File** (`condtions.txt`): Comma-separated list of condition names for each TMT channel  
   - For MS2: Include a baseline channel (Light, Baseline, Base, or Noise)  
   - For MS3: Include a baseline channel (it will be automatically removed)  
   - Use `skip` or `Boost` for channels to exclude  

2. **Pairs File** (`pairs.txt`): Semicolon-separated condition comparisons  
   - Format: `Treatment/Control;Treatment2/Control`  
   - Leave empty for simple protein rollup without statistical testing  

## Data Processing Workflow  

### MS2 Pipeline
1. Filter PSMs → IT adjustment → Normalization → Extract heavy → Baseline correction → Statistics  

### MS3 Pipeline
1. Filter PSMs → Normalization → Extract heavy → PSMs to Peptide → Statistics  

## Output  

The application generates an Excel report with two sheets:

1. **Info Sheet**: Version, peptide/protein counts, mitochondrial counts, parameters used  
2. **Results Sheet**: Protein data with measurements, gene names, MitoCarta annotations, p-values, q-values, and significance markers  

## Reference Databases  

1. **UniProt Database** (`Uniprot_database_2021.xlsx`): Maps protein accession numbers to gene symbols  
2. **MitoCarta 3.0 Database** (`database.xlsx`): Identifies mitochondrial proteins  

## References

1. Klann K, Tascher G, Münch C. *Molecular Cell*. 2020;77(4):913-925.e4. [DOI: 10.1016/j.molcel.2019.11.010](https://doi.org/10.1016/j.molcel.2019.11.010)  
2. Schäfer JA, Bozkurt S, et al. *Molecular Cell*. 2022;82(2):435-446.e7. [DOI: 10.1016/j.molcel.2021.11.004](https://doi.org/10.1016/j.molcel.2021.11.004)  
3. Bozkurt S, Parmar BS, Münch C. *Methods in Enzymology*. 2024;706:449-474. [DOI: 10.1016/bs.mie.2024.07.017](https://pubmed.ncbi.nlm.nih.gov/39455229/)  

## License  

MIT License

Copyright (c) 2023-2026 Süleyman Bozkurt

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Author  

Süleyman Bozkurt (2022-2026)  

## Contact  

Email: bozkurt@med.uni-frankfurt.de
