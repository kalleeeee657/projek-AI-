import bpy,sys,pathlib,json,struct
out=pathlib.Path(sys.argv[sys.argv.index('--')+1]).resolve()
out.parent.mkdir(parents=True,exist_ok=True)
s=bpy.context.scene
assert bpy.app.version[:3]==(4,5,3)
s.frame_start=1;s.frame_end=300;s.render.fps=60
s.frame_set(1)
collection=bpy.data.collections['Dinosaur']
# Rigid detail vertices use the SAME armature as the continuous skin.
# This avoids glTF exporting the separate empty-driven detail tracks out of sync.
from mathutils import Matrix
arm=next(o for o in collection.objects if o.type=='ARMATURE')
bpy.context.view_layer.update()
details=[o for o in collection.objects if o.type=='MESH' and o.name.split('.')[0] in ('Eye white','Pupil','Eye glint','Nostril','Toenail')]
assert len(details)>=8
def center(o):
    return sum((o.matrix_world@v.co for v in o.data.vertices),__import__('mathutils').Vector((0,0,0)))/len(o.data.vertices)
rep=[]
for o in details:
    old=center(o);driver=o.parent
    assert driver is not None,o.name
    bone=min(arm.pose.bones,key=lambda b:((arm.matrix_world@b.head)-driver.matrix_world.translation).length)
    # Rest-space point corresponding to the visible frame-1 location.
    inv=arm.matrix_world@bone.bone.matrix_local@bone.matrix.inverted()@arm.matrix_world.inverted()
    m=inv@o.matrix_world
    o.data=o.data.copy();o.data.transform(m)
    o.parent=None;o.matrix_world=Matrix.Identity(4)
    o.vertex_groups.clear();g=o.vertex_groups.new(name=bone.name);g.add(list(range(len(o.data.vertices))),1.0,'REPLACE')
    mod=o.modifiers.new('Rigid detail skin','ARMATURE');mod.object=arm
    bpy.context.view_layer.update()
    ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());new=center(ev)
    err=(new-old).length
    assert err<.03,(o.name,bone.name,err)
    rep.append({'object':o.name,'bone':bone.name,'frame1_error_m':err})
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
report={'bytes':len(raw),'nodes':len(g['nodes']),'meshes':len(g['meshes']),'skins':len(g['skins']),'animations':[{'name':a.get('name'),'channels':len(a['channels'])} for a in g['animations']], 'rigid_details':rep,'material':'simplified base PBR; procedural detail in Three.js, not baked Cycles textures'}
out.with_suffix('.json').write_text(json.dumps(report,indent=2));print(report)
