"""Fetch and verify the unmodified official ICLR 2027 LaTeX style.

Only formatting needs network access; the experiments run entirely offline.
The Git blob SHA was verified against ICLR/Master-Template on 2026-09-17.
"""
from pathlib import Path
from urllib.request import urlopen
import hashlib
ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'paper'/'iclr2027_conference.sty'
EXPECTED='f61ad7efce0855557694078c0945e6c33feb8236'
URL='https://raw.githubusercontent.com/ICLR/Master-Template/master/iclr2027/iclr2027_conference.sty'

def blob_sha(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def main():
    if TARGET.exists() and blob_sha(TARGET.read_bytes())==EXPECTED:
        print('Official style already present and hash-verified.');return
    with urlopen(URL,timeout=30) as response: data=response.read()
    if blob_sha(data)!=EXPECTED:
        raise RuntimeError('Official style changed: inspect it before updating the pinned hash.')
    TARGET.write_bytes(data)
    print('Downloaded and verified official ICLR 2027 style.')

if __name__=='__main__': main()
