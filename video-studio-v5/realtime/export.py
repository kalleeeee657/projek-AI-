import bpy,sys,pathlib,json,struct
out=pathlib.Path(sys.argv[sys.argv.index('--')+1]).resolve()
out.parent.mkdir(parents=True,exist_ok=True)
s=bpy.context.scene
assert bpy.app.version[:3]==(4,5,3)
s.frame_start=1;s.frame_end=300;s.render.fps=60
s.frame_set(1)
collection=bpy.data.collections['Dinosaur']
bpy.ops.object.select_all(action='DESELECT')
for o in collection.objects:
    o.hide_set(False);o.select_set(True)
    if o.type=='MESH':
        for slot in o.material_slots:
            m=slot.material
            if m and m.use_nodes:
                p=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
                if p:
                    for key in ('Base Color','Normal'):
                        for link in list(p.inputs[key].links):m.node_tree.links.remove(link)
                    p.inputs['Base Color'].default_value=m.diffuse_color
                    p.inputs['Roughness'].default_value=.68
        # The original voxel skin is smooth and already sufficiently dense.
        for mod in list(o.modifiers):
            if mod.type=='SUBSURF':o.modifiers.remove(mod)
bpy.context.view_layer.objects.active=next(o for o in collection.objects if o.type=='ARMATURE')
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='SCENE',export_force_sampling=True,export_frame_range=True,export_yup=True,export_apply=False)
raw=out.read_bytes()
magic,ver,total=struct.unpack_from('<4sII',raw)
assert magic==b'glTF' and ver==2 and total==len(raw)
n,kind=struct.unpack_from('<I4s',raw,12);assert kind==b'JSON'
g=json.loads(raw[20:20+n])
assert g.get('skins') and g.get('animations') and g.get('meshes')
assert any('Brachiosaurus' in x.get('name','') for x in g['nodes'])
report={'bytes':len(raw),'nodes':len(g['nodes']),'meshes':len(g['meshes']),'skins':len(g['skins']),'animations':[{'name':a.get('name'),'channels':len(a['channels'])} for a in g['animations']], 'material':'simplified base PBR; procedural detail in Three.js, not baked Cycles textures'}
out.with_suffix('.json').write_text(json.dumps(report,indent=2));print(report)
