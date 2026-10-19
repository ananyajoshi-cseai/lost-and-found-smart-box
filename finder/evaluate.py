"""Repeat the inherited frozen reasoning regression set without HTTP or a database."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
from finder_core.engine import parse, rank

BASE=Path(__file__).resolve().parent


def evaluate():
    items=json.loads((BASE/'evaluation/items-v1.json').read_text(encoding='utf-8-sig'))
    queries=json.loads((BASE/'evaluation/queries-v1.json').read_text(encoding='utf-8-sig'))
    runs=[]
    for query in queries:
        results=rank(parse(query['query']),items,query['broaden'])
        runs.append({**query,'returned_ids':[r['id'] for r in results],'results':results})
    positive=[r for r in runs if r['kind']=='positive']
    negative=[r for r in runs if r['kind']=='negative']
    metrics={'positive_queries':len(positive),'negative_queries':len(negative),
        'top1_hits':sum(bool(r['returned_ids']) and r['returned_ids'][0] in r['relevant_ids'] for r in positive),
        'top3_hits':sum(bool(set(r['returned_ids']) & set(r['relevant_ids'])) for r in positive),
        'negative_false_positives':sum(bool(r['returned_ids']) for r in negative)}
    for name,num,den in [('top1_rate','top1_hits','positive_queries'),('top3_rate','top3_hits','positive_queries'),
                          ('negative_false_positive_rate','negative_false_positives','negative_queries')]:
        metrics[name]=metrics[num]/metrics[den] if metrics[den] else None
    paths=list((BASE/'finder_core').glob('*.py'))+list((BASE/'evaluation').glob('*.json'))
    return {'generated_at_utc':datetime.now(timezone.utc).isoformat(),
        'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE,text=True).strip(),
        'dirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=BASE,text=True).strip()),
        'python':platform.python_version(),'platform':platform.platform(),
        'method':'Pure Python reasoning regression: inherited 20-item/18-query frozen set, not the 40-item UI seed or an independent new evaluation.',
        'sha256':{str(p.relative_to(BASE)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        'metrics':metrics,'query_runs':runs}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists(): parser.error('Choose a new output file; earlier evidence is never overwritten.')
    report=evaluate()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8') as stream:
        json.dump(report,stream,indent=2)
        stream.write('\n')
    print(json.dumps(report['metrics'],indent=2))
