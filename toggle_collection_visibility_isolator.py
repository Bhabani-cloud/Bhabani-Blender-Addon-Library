bl_info = {
    "name": "Collection Visibility Isolator",
    "blender": (4, 4, 0),
    "category": "3D View",
    "author": "Bhabani Tudu",
    "description": "Shift+1-9: Isolate collections | Shift+Q: Toggle addon"
}

import bpy

# Property group to store our addon state
class VisibilityIsolatorProps(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(
        name="Addon Enabled",
        description="Toggle addon functionality",
        default=True
    )

class VIEW3D_PT_visibility_isolator(bpy.types.Panel):
    bl_label = "Visibility Isolator"
    bl_category = "Collection Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        return context.window_manager.visibility_isolator_props.enabled

    def draw(self, context):
        props = context.window_manager.visibility_isolator_props
        layout = self.layout
        
        # Addon toggle button
        row = layout.row()
        row.prop(props, "enabled", text="Disable Addon" if props.enabled else "Enable Addon", 
                icon='CHECKMARK' if props.enabled else 'CANCEL')
        row.label(text="(Shift+Q)")

        layout.separator()
        layout.label(text="Isolation Hotkeys:")
        layout.label(text="Shift+1 to Shift+9")

class OBJECT_OT_isolate_visibility(bpy.types.Operator):
    bl_idname = "view3d.isolate_visibility"
    bl_label = "Isolate Collection Visibility"
    bl_options = {'REGISTER', 'UNDO'}

    index: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return context.window_manager.visibility_isolator_props.enabled

    def execute(self, context):
        props = context.window_manager.visibility_isolator_props
        if not props.enabled:
            return {'CANCELLED'}

        layer_collections = context.view_layer.layer_collection.children
        if self.index < 0 or self.index >= len(layer_collections):
            self.report({'WARNING'}, "Collection index out of range")
            return {'CANCELLED'}

        target_col = layer_collections[self.index]
        is_already_isolated = (
            not target_col.hide_viewport and 
            all(col.hide_viewport or col == target_col for col in layer_collections)
        )

        if is_already_isolated:
            for col in layer_collections:
                col.hide_viewport = False
            self.report({'INFO'}, "Showing all collections")
        else:
            for col in layer_collections:
                col.hide_viewport = (col != target_col)
            self.report({'INFO'}, f"Isolated: {target_col.name}")

        return {'FINISHED'}

class WM_OT_toggle_visibility_isolator(bpy.types.Operator):
    bl_idname = "wm.toggle_visibility_isolator"
    bl_label = "Toggle Visibility Isolator"
    
    def execute(self, context):
        props = context.window_manager.visibility_isolator_props
        props.enabled = not props.enabled
        
        # Force UI update
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        
        self.report({'INFO'}, f"Addon {'enabled' if props.enabled else 'disabled'}")
        return {'FINISHED'}

addon_keymaps = []

def register_keymaps():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if not kc:
        return

    km = kc.keymaps.new(name='Object Mode', space_type='EMPTY')
    
    # Always register the toggle hotkey
    kmi = km.keymap_items.new(
        WM_OT_toggle_visibility_isolator.bl_idname,
        type='Q',
        value='PRESS',
        shift=True
    )
    addon_keymaps.append((km, kmi))
    
    # Only register isolation hotkeys if enabled
    if wm.visibility_isolator_props.enabled:
        for i, key in enumerate(['ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE']):
            kmi = km.keymap_items.new(
                OBJECT_OT_isolate_visibility.bl_idname,
                type=key,
                value='PRESS',
                shift=True
            )
            kmi.properties.index = i
            addon_keymaps.append((km, kmi))

def unregister_keymaps():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

classes = (
    VisibilityIsolatorProps,
    VIEW3D_PT_visibility_isolator,
    OBJECT_OT_isolate_visibility,
    WM_OT_toggle_visibility_isolator,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Register our property
    bpy.types.WindowManager.visibility_isolator_props = bpy.props.PointerProperty(type=VisibilityIsolatorProps)
    
    register_keymaps()

def unregister():
    unregister_keymaps()
    
    # Unregister our property
    del bpy.types.WindowManager.visibility_isolator_props
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()