"""Idempotent title/code-block layout fixes; never rewrites scientific prose."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BLOCK=("\\begin{verbatim}\n"
       "python -m pip install -r requirements.txt\n"
       "python -m pytest -q\n"
       "python experiments/run_all.py\n"
       "python experiments/additional_checks.py\n"
       "python experiments/make_figures.py\n"
       "make paper\n\\end{verbatim}")

def main():
    p=ROOT/'paper/main.tex'; text=p.read_text()
    text=text.replace('Sharp Cold-Start Limits and Joint-History Audit Schedules}',
                      r'Sharp Cold-Start Limits and Joint-History\\Audit Schedules}')
    p.write_text(text)
    p=ROOT/'paper/appendix.tex'; text=p.read_text()
    wrapped='\\begin{minipage}{\\linewidth}\n'+BLOCK+'\n\\end{minipage}'
    if wrapped not in text: text=text.replace(BLOCK,wrapped)
    p.write_text(text)
    print('Title and code-block layout checked; scientific prose unchanged.')

if __name__=='__main__': main()
