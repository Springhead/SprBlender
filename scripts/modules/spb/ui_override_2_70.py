# -*- coding: utf-8 -*-

import bpy
import spb

from   Spr              import *
from   spb.synchronizer import *
from   spb.utils        import *


# --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
# AddメニューをオーバーライドしてSpringhead ObjectをAddできるようにする

import bl_ui.space_view3d
from bpy.types import Menu
info_mt_add_draw = bl_ui.space_view3d.INFO_MT_add.draw
class INFO_MT_add(Menu):
	bl_label = "Add"

	def draw(self, context):
		info_mt_add_draw(self, context)
		layout = self.layout
		layout.separator()

		layout.menu("INFO_MT_spr_add_solid", icon='OUTLINER_OB_MESH')
		layout.menu("INFO_MT_spr_add_joint", icon='CONSTRAINT')

# -- -- -- -- --
class INFO_MT_spr_add_solid(Menu):
	bl_idname = "INFO_MT_spr_add_solid"
	bl_label = "Spr Solid"

	def draw(self, context):
		layout = self.layout

		layout.operator_context = 'EXEC_REGION_WIN'
		layout.operator("spr.add_solid_box",    icon='MESH_CUBE',     text="Box")
		layout.operator("spr.add_solid_sphere", icon='MESH_UVSPHERE', text="Sphere")

class INFO_MT_SprAddSolidBox(bpy.types.Operator):
	bl_idname = "spr.add_solid_box"
	bl_label = "[spr]Box"
	bl_description = "[Spr]Box"
	
	def execute(self,context):
		bpy.ops.mesh.primitive_cube_add()
		obj = bpy.context.object
		obj.spr_object_type = "Solid"
		obj.spr_shape_type	= "Box"
		
		return{'FINISHED'}

class INFO_MT_SprAddSolidSphere(bpy.types.Operator):
	bl_idname = "spr.add_solid_sphere"
	bl_label = "[spr]Sphere Solid"
	bl_description = "[Spr]Sphere Solid"
	
	def execute(self,context):
		bpy.ops.mesh.primitive_uv_sphere_add()
		obj = bpy.context.object
		obj.spr_object_type = "Solid"
		obj.spr_shape_type	= "Sphere"
		
		return{'FINISHED'}

# -- -- -- -- --
class INFO_MT_spr_add_joint(Menu):
	bl_idname = "INFO_MT_spr_add_joint"
	bl_label = "Spr Joint"

	def draw(self, context):
		layout = self.layout

		layout.operator_context = 'EXEC_REGION_WIN'
		layout.operator("spr.add_joint_hinge",  text="Hinge")
		layout.operator("spr.add_joint_slider", text="Slider")
		layout.operator("spr.add_joint_ball",   text="Ball")
		layout.operator("spr.add_joint_spring", text="Spring")

class INFO_MT_SprAddJointHinge(bpy.types.Operator):
	bl_idname = "spr.add_joint_hinge"
	bl_label = "[spr]Hinge Joint"
	bl_description = "[Spr]Hinge Joint"
	
	def execute(self,context):
		bpy.ops.object.empty_add(type='SINGLE_ARROW')
		obj = bpy.context.object
		obj.show_x_ray = True
		obj.spr_object_type = "Joint"
		obj.spr_joint_mode  = "Hinge"
		
		return{'FINISHED'}

class INFO_MT_SprAddJointSlider(bpy.types.Operator):
	bl_idname = "spr.add_joint_slider"
	bl_label = "[spr]Slider Joint"
	bl_description = "[Spr]Slider Joint"
	
	def execute(self,context):
		bpy.ops.object.empty_add(type='SINGLE_ARROW')
		obj = bpy.context.object
		obj.show_x_ray = True
		obj.spr_object_type = "Joint"
		obj.spr_joint_mode  = "Slider"
		
		return{'FINISHED'}

class INFO_MT_SprAddJointBall(bpy.types.Operator):
	bl_idname = "spr.add_joint_ball"
	bl_label = "[spr]Ball Joint"
	bl_description = "[Spr]Ball Joint"
	
	def execute(self,context):
		bpy.ops.object.empty_add(type='SINGLE_ARROW')
		obj = bpy.context.object
		obj.show_x_ray = True
		obj.spr_object_type = "Joint"
		obj.spr_joint_mode  = "Ball"
		
		return{'FINISHED'}

class INFO_MT_SprAddJointSpring(bpy.types.Operator):
	bl_idname = "spr.add_joint_spring"
	bl_label = "[spr]Spring Joint"
	bl_description = "[Spr]Spring Joint"
	
	def execute(self,context):
		bpy.ops.object.empty_add(type='ARROWS')
		obj = bpy.context.object
		obj.show_x_ray = True
		obj.spr_object_type = "Joint"
		obj.spr_joint_mode  = "Spring"
		
		return{'FINISHED'}


# --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
# File -> Exportメニューをオーバーライドして.sprファイルを出力できるようにする

import bl_ui.space_info
info_mt_file_export_draw = bl_ui.space_info.INFO_MT_file_export.draw
class INFO_MT_file_export(Menu):
	bl_idname = "INFO_MT_file_export"
	bl_label = "Export"

	def draw(self, context):
		info_mt_file_export_draw(self, context)
		self.layout.operator("spr.export_spr_file", text="Springhead (.spr)")

class INFO_MT_SprExportSprFile(bpy.types.Operator):
	bl_idname = "spr.export_spr_file"
	bl_label = "[spr]Export Springhead File"
	bl_description = "[Spr]Export Springhead File"
	
	def execute(self,context):
		spb.spbapi.SaveSpr(bpy.data.filepath+".spr")
		return{'FINISHED'}

