import bpy,sys,pathlib,json
dest=pathlib.Path(sys.argv[sys.argv.index('--')+1]).resolve()
dest.mkdir(parents=True,exist_ok=True)
s=bpy.context.scene
assert bpy.app.version[:3]==(4,5,3)
groups={name:bpy.data.collections.new(name) for name in ('Dinosaur','Hero','Coastal environment','Camera and lighting')}
for c in groups.values():s.collection.children.link(c)
def ancestor(o):
    while o.parent:o=o.parent
    return o
for o in list(s.objects):
    a=ancestor(o)
    if a.name.startswith('Brachiosaurus root') or o.name.startswith(('Dinosaur skeletal rig','Brachiosaurus continuous skin')):key='Dinosaur'
    elif a.name.startswith('Hero'):key='Hero'
    elif o.type in ('CAMERA','LIGHT'):key='Camera and lighting'
    else:key='Coastal environment'
    c=groups[key]
    c.objects.link(o)
    for prior in list(o.users_collection):
        if prior!=c:prior.objects.unlink(o)
for c in groups.values():
    assert len(c.objects)>0,c.name
    c.asset_mark()
bpy.ops.wm.save_as_mainfile(filepath=str(dest/'asset-library.blend'))
(dest/'library-report.json').write_text(json.dumps({k:len(c.objects) for k,c in groups.items()},indent=2))
