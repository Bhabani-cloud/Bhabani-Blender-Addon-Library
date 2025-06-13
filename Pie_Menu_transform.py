bl_info = {
    "name": "Gizmo Transform Pie Menu",
    "author": "ChatGPT",
    "version": (1, 2),
    "blender": (4, 4, 0),
    "location": "Shift + Alt + D",
    "description": "Pie menu for activating Move, Rotate, Scale, Transform gizmos",
    "category": "3D View",
}

import bpy
from bpy.types import Menu

# Matcap Operator
class UNIVERSAL_OT_set_matcap_light(bpy.types.Operator):
    bl_idname = "view3d.set_matcap_light"
    bl_label = "Use MatCap Lighting"

    def execute(self, context):
        area = next((area for area in context.screen.areas if area.type == 'VIEW_3D'), None)
        if area:
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.light = 'MATCAP'
        return {'FINISHED'}
    
# Pie Menu with Gizmo Tool Activation
class UNIVERSAL_MT_gizmo_pie(Menu):
    bl_label = "Gizmo Transform Pie Menu"
    bl_idname = "UNIVERSAL_MT_gizmo_pie"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("wm.tool_set_by_id", text="Move").name = "builtin.move"
        pie.operator("wm.tool_set_by_id", text="Rotate").name = "builtin.rotate"
        pie.operator("wm.tool_set_by_id", text="Scale").name = "builtin.scale"
        # pie.operator("wm.tool_set_by_id", text="Transform").name = "builtin.transform"
        # pie.operator("wm.tool_set_by_id", text="Measure").name = "builtin.measure"
        pie.operator("object.origin_set", text="Origin to Cursor").type = "ORIGIN_CURSOR"
        pie.operator("object.scale_to_dimension_interactive", text="Dimension")
        pie.operator("view3d.set_matcap_light", text="Set MatCap Light")
        

# Operator to show the pie menu
class UNIVERSAL_OT_show_gizmo_pie(bpy.types.Operator):
    bl_idname = "wm.show_gizmo_pie"
    bl_label = "Show Gizmo Transform Pie"

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name=UNIVERSAL_MT_gizmo_pie.bl_idname)
        return {'FINISHED'}


# Keymap Registration
addon_keymaps = []

def register():
    bpy.utils.register_class(UNIVERSAL_MT_gizmo_pie)
    bpy.utils.register_class(UNIVERSAL_OT_show_gizmo_pie)
    bpy.utils.register_class(UNIVERSAL_OT_set_matcap_light)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    if kc:
        km = kc.keymaps.new(name="3D View", space_type='VIEW_3D')
        kmi = km.keymap_items.new("wm.show_gizmo_pie", 'D', 'PRESS', shift=True, alt=True)
        addon_keymaps.append((km, kmi))


def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_class(UNIVERSAL_MT_gizmo_pie)
    bpy.utils.unregister_class(UNIVERSAL_OT_show_gizmo_pie)
    bpy.utils.unregister_class(UNIVERSAL_OT_set_matcap_light)

if __name__ == "__main__":
    register()
