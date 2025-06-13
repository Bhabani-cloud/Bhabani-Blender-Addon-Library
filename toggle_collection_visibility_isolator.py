bl_info = {
    "name": "Collection Visibility Isolator",
    "blender": (4, 4, 0),
    "category": "3D View",
    "author": "ChatGPT",
    "description": "Shift+1-9: Isolate collections | Shift+Q: Toggle addon | Pinned collections stay visible"
}

import bpy

class PinnedCollection(bpy.types.PropertyGroup):
    """Property group to store pinned collection indices"""
    index: bpy.props.IntProperty()

class VisibilityIsolatorProps(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(
        name="Addon Enabled",
        description="Toggle addon functionality",
        default=True
    )
    
    pinned_collections: bpy.props.CollectionProperty(
        type=PinnedCollection
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
        
        # Addon toggle
        row = layout.row()
        row.prop(props, "enabled", text="Disable Addon" if props.enabled else "Enable Addon", 
                icon='CHECKMARK' if props.enabled else 'CANCEL')
        row.label(text="(Shift+Q)")

        layout.separator()
        
        # Collections list with pin toggle
        layout.label(text="Collections:")
        for i, col in enumerate(context.view_layer.layer_collection.children):
            if i >= 9:  # Only show first 9 to match hotkeys
                break
                
            row = layout.row(align=True)
            
            # Check if collection is pinned
            is_pinned = any(p.index == i for p in props.pinned_collections)
            
            # Pin toggle
            pin_icon = 'PINNED' if is_pinned else 'UNPINNED'
            pin_op = row.operator("wm.toggle_pin_collection", text="", icon=pin_icon, emboss=False)
            pin_op.collection_index = i
            
            # Collection name
            row.label(text=f"{i+1}. {col.name}")

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
        
        # Get list of pinned indices
        pinned_indices = [p.index for p in props.pinned_collections]
        
        is_already_isolated = (
            not target_col.hide_viewport and 
            all(col.hide_viewport or col == target_col or i in pinned_indices
                for i, col in enumerate(layer_collections))
        )

        if is_already_isolated:
            # Show all non-pinned collections
            for i, col in enumerate(layer_collections):
                if i not in pinned_indices:
                    col.hide_viewport = False
            self.report({'INFO'}, "Showing all collections")
        else:
            # Isolate target collection (keep pinned collections visible)
            for i, col in enumerate(layer_collections):
                if i not in pinned_indices:
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

class WM_OT_toggle_pin_collection(bpy.types.Operator):
    bl_idname = "wm.toggle_pin_collection"
    bl_label = "Toggle Pin Collection"
    
    collection_index: bpy.props.IntProperty()
    
    def execute(self, context):
        props = context.window_manager.visibility_isolator_props
        pinned_indices = [p.index for p in props.pinned_collections]
        
        if self.collection_index in pinned_indices:
            # Find and remove the pinned collection
            for i, p in enumerate(props.pinned_collections):
                if p.index == self.collection_index:
                    props.pinned_collections.remove(i)
                    break
        else:
            # Add new pinned collection
            new_pin = props.pinned_collections.add()
            new_pin.index = self.collection_index
        
        # Force UI update
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        
        return {'FINISHED'}

addon_keymaps = []

def register_keymaps():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if not kc:
        return

    km = kc.keymaps.new(name='Object Mode', space_type='EMPTY')
    
    # Toggle hotkey
    kmi = km.keymap_items.new(
        WM_OT_toggle_visibility_isolator.bl_idname,
        type='Q',
        value='PRESS',
        shift=True
    )
    addon_keymaps.append((km, kmi))
    
    # Isolation hotkeys
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
    PinnedCollection,
    VisibilityIsolatorProps,
    VIEW3D_PT_visibility_isolator,
    OBJECT_OT_isolate_visibility,
    WM_OT_toggle_visibility_isolator,
    WM_OT_toggle_pin_collection,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.WindowManager.visibility_isolator_props = bpy.props.PointerProperty(type=VisibilityIsolatorProps)
    register_keymaps()

def unregister():
    unregister_keymaps()
    del bpy.types.WindowManager.visibility_isolator_props
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
