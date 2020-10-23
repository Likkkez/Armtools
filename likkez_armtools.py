bl_info = {
    "name": "Armature tools",
    "author": "Likkez",
    "version": (1, 0),
    "blender": (2, 90, 0),
    "description": "Armature tools for game engines",
    "warning": "",
    "wiki_url": "",
    "category": "Animation",
}
import bpy

def trace_bone(bone, bone_arr):
    if not bone in bone_arr: 
        bone_arr.append(bone)
        if bone.parent:
            trace_bone(bone.parent, bone_arr)
    return bone_arr
        
        


class AT_OT_remove_bones(bpy.types.Operator):
    bl_description = "Select mesh objects and an armature. The script will determine the bones that affect the mesh and keep them and their parents, deleting everything else."
    bl_idname = 'armtools.remove_bones'
    bl_label = "Remove Bones"
    bl_options = set({'REGISTER', 'UNDO'}) 
    
    keep_selected: bpy.props.BoolProperty(
        name="Keep Selected",
        description="Keep selected bones.",
        default=True
        )
        
    def execute(self, context):
        meshes=[]
        arm=None
        for obj in bpy.context.selected_editable_objects:
            if obj.type=='ARMATURE':
                arm=obj
            elif obj.type=='MESH':
                meshes.append(obj)
        if arm:
            vgroups_list=[]
            for mesh in meshes:
                
                #mirror mod fix
                has_mirror=False
                for mod in mesh.modifiers:
                    if mod.type=='MIRROR' and mod.show_render:
                        has_mirror=True
                        mirror_dict={
                            'R':'L',
                            'r':'l',
                            'L':'R',
                            'l':'r',
                            }
                        mirror_dict_tuple=[]
                        for item in mirror_dict:
                            mirror_dict_tuple.append(item)
                        mirror_dict_tuple=tuple(mirror_dict_tuple)
                        
                        numbers=('0','1','2','3','4','5','6','7','8','9','.')
                        
                for v in mesh.data.vertices:
                    for g in v.groups:
                        if g.weight>0:
                            name=mesh.vertex_groups[g.group].name
                            if (not name in vgroups_list) and (not has_mirror):
                                vgroups_list.append(name)
                                
                                
                            if has_mirror:
                                vgroups_list.append(name)
                                end_numbers=''
                                while name.endswith(numbers):
                                    length=len(name)
                                    end_numbers+=name[length-1:length]
                                    name=name[:-1]
                                end_numbers=end_numbers[::-1]
                                
                                if name.lower().endswith(mirror_dict_tuple):
                                    length=len(name)
                                    name=name[:-1]+mirror_dict[name[length-1:length]]+end_numbers
                                    if not name in vgroups_list:
                                        vgroups_list.append(name)
            
            
            bpy.ops.object.mode_set(mode='OBJECT')
#            bpy.ops.object.select_all(action='DESELECT')
            arm.select_set(True)
            bpy.context.view_layer.objects.active=arm
            
            bpy.ops.object.mode_set(mode='EDIT')
            from_selected=False

            bone_list=[]
            for g in vgroups_list:
                try:
                    arm.data.edit_bones[g]
                    bone_list.append(arm.data.edit_bones[g])
                except:
                    pass
                
            if self.keep_selected:
                for bone in bpy.context.selected_editable_bones:
                    if not bone in bone_list:
                        bone_list.append(bone)
                
            bone_save = []
            for bone in bone_list:
                if not bone in bone_save: 
                    trace_bone(bone, bone_save)
                    

#            editbones = arm.data.edit_bones.copy()
            for bone in arm.data.edit_bones:
                if bone not in bone_save:
                    arm.data.edit_bones.remove(bone)
            return {'FINISHED'}
        return {'CANCELLED'}

class AT_PT_armtools(bpy.types.Panel):
    bl_category = "Armtools"
    bl_label = "Armtools"
    bl_idname = "SCENE_PT_Armtools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
#    bl_context = "armature_edit"

    @classmethod
    def poll(self, context):
        return True

    def draw(self, context):
        scene=bpy.context.scene
        layout = self.layout

        #tools
        box = layout.box()
        box.label(text="Tools")
        col = box.column(align = True)
        col.operator('armtools.remove_bones', text="Remove Bones")


classes = (
    AT_OT_remove_bones,
    AT_PT_armtools,
    )

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
       
def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

