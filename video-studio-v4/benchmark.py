import subprocess,sys,pathlib,json,time,os,statistics,struct
root=pathlib.Path(__file__).resolve().parent
blend=pathlib.Path(sys.argv[1]).resolve()
out=pathlib.Path(sys.argv[2]).resolve();out.mkdir(parents=True,exist_ok=True)
report={}
for engine in ('CYCLES','EEVEE'):
    d=out/engine;d.mkdir(exist_ok=True)
    cmd=['/tmp/blender/blender','-b',str(blend),'--python-exit-code','1','--python',str(root/'render.py'),'--','benchmark',json.dumps({'engine':engine,'frames':[120,121],'camera':'original'}),str(d)]
    env=os.environ.copy()
    if engine=='EEVEE':
        env['LIBGL_ALWAYS_SOFTWARE']='1';cmd=['xvfb-run','-a']+cmd
    t=time.monotonic()
    try:
        with (d/'render.log').open('w') as log:
            proc=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,env=env,timeout=720)
        if proc.returncode:raise RuntimeError(f'exit {proc.returncode}')
        timing=json.loads((d/'timing.json').read_text())
        for i in (1,2):
            with (d/f'frame-{i:04d}.png').open('rb') as f:h=f.read(24)
            assert h[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',h[16:24])==(1080,1920)
        report[engine]={'ok':True,'wall_seconds':round(time.monotonic()-t,2),'mean_frame_seconds':statistics.mean(x['seconds'] for x in timing['frames']),'timings':timing}
    except Exception as e:
        report[engine]={'ok':False,'reason':str(e),'wall_seconds':round(time.monotonic()-t,2)}
    print(engine,report[engine],flush=True)
report['recommendation']='CYCLES'
if report['CYCLES']['ok'] and report['EEVEE']['ok']:
    report['eevee_speedup']=round(report['CYCLES']['mean_frame_seconds']/max(.001,report['EEVEE']['mean_frame_seconds']),2)
    report['eevee_requires_visual_approval']=True
(out/'benchmark.json').write_text(json.dumps(report,indent=2))
if not report['CYCLES']['ok']:raise SystemExit('Cycles baseline failed')
