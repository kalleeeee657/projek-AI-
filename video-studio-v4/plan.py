import json,pathlib,os,re
root=pathlib.Path(__file__).resolve().parent
p=json.loads((root/'project.json').read_text())
report=json.loads(pathlib.Path('benchmark/benchmark.json').read_text())
assert report['CYCLES']['ok']
seen=set();items=[]
for i,s in enumerate(p['scenes']):
    assert re.fullmatch('[a-z0-9-]+',s['id']) and s['id'] not in seen
    seen.add(s['id'])
    assert s['asset']=='mandalika-dino-v2' and s['motion']=='natural-walk'
    assert s['camera'] in ('original','detail')
    assert type(s['sec']) is int and s['sec']>=1 and type(s['first']) is int and 1<=s['first']<=s['first']+s['sec']*60-1<=300
    assert s['engine'] in ('CYCLES','EEVEE')
    assert s['line'].strip()
    engine='EEVEE' if s['engine']=='EEVEE' and os.getenv('ALLOW_EEVEE')=='true' and report.get('EEVEE',{}).get('ok') and report.get('eevee_speedup',0)>1 else 'CYCLES'
    visual={k:s[k] for k in ('asset','motion','first','sec','camera')}
    visual['engine']=engine
    items.append({'index':i,'id':s['id'],'spec':json.dumps(visual,separators=(',',':'))})
assert 1<=len(items)<=60
with open(os.environ['GITHUB_OUTPUT'],'a') as f:f.write('matrix='+json.dumps({'include':items},separators=(',',':'))+'\n')
