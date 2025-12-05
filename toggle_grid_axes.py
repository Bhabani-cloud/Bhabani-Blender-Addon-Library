bl_info = {
    "name": "Toggle Grid & Axes Button",
    "author": "Bhabani Tudu",
    "version": (1, 0),
    "blender": (5, 0, 0),
    "category": "3D View",
}

import bpy

class VIEW3D_OT_toggle_grid_and_axes(bpy.types.Operator):
    bl_idname = "view3d.toggle_grid_and_axes"
    bl_label = "Toggle Grid & Axes"
    bl_description = "Toggle Grid Floor, X Axis and Y Axis visibility together"

    def execute(self, context):
        overlay = context.space_data.overlay
        
        any_on = overlay.show_floor or overlay.show_axis_x or overlay.show_axis_y
        
        overlay.show_floor = not any_on
        overlay.show_axis_x = not any_on
        overlay.show_axis_y = not any_on
        
        return {'FINISHED'}


def register():
    bpy.utils.register_class(VIEW3D_OT_toggle_grid_and_axes)


def unregister():
    bpy.utils.unregister_class(VIEW3D_OT_toggle_grid_and_axes)


if __name__ == "__main__":
    register()
