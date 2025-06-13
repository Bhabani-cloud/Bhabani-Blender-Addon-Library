bl_info = {
    "name": "Mesh Delete - Edit Mode (Toggle)",
    "blender": (4, 4, 0),
    "category": "3D View",
    "author": "ChatGPT",
    "description": "Use 'X' to toggle-delete pop-up"
}

import bpy
from bpy.types import Menu

# from .op_pie_wrappers import WM_OT_call_menu_pie_drag_only


class PIE_MT_mesh_delete(Menu):
    bl_idname = "PIE_MT_mesh_delete"
    bl_label = "Mesh Delete"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 4 - LEFT
        box = pie.split().column()
        box.operator(
            "mesh.dissolve_limited", text="Limited Dissolve", icon='STICKY_UVS_LOC'
        )
        box.operator("mesh.delete_edgeloop", text="Delete Edge Loops", icon='NONE')
        box.operator("mesh.edge_collapse", text="Edge Collapse", icon='UV_EDGESEL')
        # 6 - RIGHT
        box = pie.split().column()
        box.operator("mesh.remove_doubles", text="Merge By Distance", icon='NONE')
        box.operator("mesh.delete", text="Only Edge & Faces", icon='NONE').type = (
            'EDGE_FACE'
        )
        box.operator("mesh.delete", text="Only Faces", icon='UV_FACESEL').type = (
            'ONLY_FACE'
        )
        # 2 - BOTTOM
        pie.operator("mesh.dissolve_edges", text="Dissolve Edges", icon='SNAP_EDGE')
        # 8 - TOP
        pie.operator("mesh.delete", text="Delete Edges", icon='EDGESEL').type = 'EDGE'
        # 7 - TOP - LEFT
        pie.operator("mesh.delete", text="Delete Vertices", icon='VERTEXSEL').type = (
            'VERT'
        )
        # 9 - TOP - RIGHT
        pie.operator("mesh.delete", text="Delete Faces", icon='FACESEL').type = 'FACE'
        # 1 - BOTTOM - LEFT
        pie.operator(
            "mesh.dissolve_verts", text="Dissolve Vertices", icon='SNAP_VERTEX'
        )
        # 3 - BOTTOM - RIGHT
        pie.operator("mesh.dissolve_faces", text="Dissolve Faces", icon='SNAP_FACE')


class VIEW3D_OT_call_pie_delete(bpy.types.Operator):
    bl_idname = "wm.call_pie_delete"
    bl_label = "Call Delete Pie Menu"

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name=PIE_MT_mesh_delete.bl_idname)
        return {'FINISHED'}

addon_keymaps = []

def register():
    bpy.utils.register_class(PIE_MT_mesh_delete)
    bpy.utils.register_class(VIEW3D_OT_call_pie_delete)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='Mesh', space_type='EMPTY')
        kmi = km.keymap_items.new("wm.call_pie_delete", type='X', value='PRESS')
        addon_keymaps.append((km, kmi))

def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_class(PIE_MT_mesh_delete)
    bpy.utils.unregister_class(VIEW3D_OT_call_pie_delete)

if __name__ == "__main__":
    register()

