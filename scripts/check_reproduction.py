"""Regenerate scientific CSVs and compare by value (or strict identical bytes)."""
from pathlib import Path
import argparse,subprocess,sys,tempfile,json,hashlib
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--strict',action='store_true');args=parser.parse_args()
    checked=[]
    with tempfile.TemporaryDirectory() as tmp:
        out=Path(tmp)
        subprocess.run([sys.executable,str(ROOT/'experiments/run_all.py'),'--out',tmp],check=True)
        subprocess.run([sys.executable,str(ROOT/'experiments/additional_checks.py'),tmp],check=True)
        for p in sorted((ROOT/'results').glob('*.csv')):
            other=out/p.name
            if not other.exists():raise AssertionError(f'Missing reproduced CSV: {p.name}')
            identical=p.read_bytes()==other.read_bytes()
            a,b=pd.read_csv(p),pd.read_csv(other)
            if a.shape!=b.shape or list(a.columns)!=list(b.columns):raise AssertionError(f'Shape mismatch: {p.name}')
            for c in a:
                if pd.api.types.is_numeric_dtype(a[c]):
                    if not np.allclose(a[c],b[c],rtol=1e-9,atol=2e-10,equal_nan=True):
                        raise AssertionError(f'Numerical mismatch: {p.name}/{c}')
                elif not a[c].equals(b[c]):raise AssertionError(f'Text mismatch: {p.name}/{c}')
            if args.strict and not identical:raise AssertionError(f'Byte mismatch: {p.name}')
            checked.append({'file':p.name,'rows':len(a),'identical_bytes':identical})
    report={'scientific_csvs':len(checked),'strict':args.strict,'all_numerically_equal':True,'files':checked}
    (ROOT/'results'/'reproduction_check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
