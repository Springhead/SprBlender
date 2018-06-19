# -*- coding: utf-8 -*-

import bpy
import spb
import bgl
import threading
import traceback
import time
import string
import random

from   mathutils    import Vector,Quaternion, Matrix
from   collections  import defaultdict, OrderedDict
from   threading    import Lock

from   Spr          import *
from   math         import *


# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# Extra Functions
# 

def rename_objects(group, suffix=None):
	spb.handlers.operation = False
	spb.handlers.clear()
	names = []
	if suffix is None:
		suffix = time.strftime("_%Y%m%d_%H%M%S")

	for obj in group.objects:
		names.append(obj.name)
		obj.name = (obj.name + suffix)

	for obj in group.objects:
		if obj.spr_roundcone_target_name in names:
			obj.spr_roundcone_target_name = obj.spr_roundcone_target_name + suffix
		if obj.spr_joint_socket_target_name in names:
			obj.spr_joint_socket_target_name = obj.spr_joint_socket_target_name + suffix
		if obj.spr_joint_plug_target_name in names:
			obj.spr_joint_plug_target_name = obj.spr_joint_plug_target_name + suffix
		if obj.spr_ik_tip_object_name in names:
			obj.spr_ik_tip_object_name = obj.spr_ik_tip_object_name + suffix
		if obj.spr_ik_target_object_name in names:
			obj.spr_ik_target_object_name = obj.spr_ik_target_object_name + suffix
	for ctl in group.spr_controllers:
		if ctl.target in names:
			ctl.target = ctl.target + suffix
	for viz in group.spr_visualizers:
		if viz.target in names:
			viz.target = viz.target + suffix

	spb.handlers.operation = True


def create_solid_joint(armature, bone, level=0):
	bpy.ops.object.empty_add(type='SPHERE')
	so0 = bpy.context.object
	so0.name = "so_"+bone.name
	so0.location = armature.location + bone.head_local
	so0.scale = Vector((1, 1, 1)) * 0.3
	so0.show_x_ray = True
	so0.spr_object_type = "Solid"
	so0.spr_shape_type  = "RoundCone"
	so0.game.mass       = 0.1
	so0.spr_autoset_inertia = False


	bpy.ops.object.select_all(action='DESELECT')
	bpy.ops.group.create(name=armature.name)
	bpy.context.scene.objects[so0.name].select = True
	bpy.ops.object.group_link(group=armature.name)
	bpy.context.scene.objects[so0.name].select = False

	bpy.data.groups[armature.name].spr_creature_group = True

	# ---

	jo0 = None
	if level > 0:
		bpy.ops.object.empty_add(type='ARROWS')
		jo0 = bpy.context.object
		jo0.name = "jo_"+bone.name

		jo0.location = Vector((0,0,0))
		jo0.scale = Vector((1, 1, 1)) * 1.5
		jo0.show_x_ray = True

		jo0.spr_object_type     = "Joint"
		jo0.spr_joint_type      = "Ball"
		jo0.spr_joint_collision = False
		jo0.spr_spring          = 1000.0/(level+1)
		jo0.spr_damper          = jo0.spr_spring * 0.01
		jo0.spr_ik_enabled      = True
		jo0.spr_ik_bias         = (level * 5) + 1

		jo0.parent = so0
		
		bpy.context.scene.objects[jo0.name].select = True
		bpy.ops.object.group_link(group=armature.name)
		bpy.context.scene.objects[jo0.name].select = False

	for child in bone.children:
		so1, jo1 = create_solid_joint(armature, child, level+1)
		so0.spr_roundcone_target_name    = so1.name
		jo1.spr_joint_socket_target_name = so0.name

	if len(bone.children)==0:
		bpy.ops.object.empty_add(type='SPHERE')
		cd = bpy.context.object
		cd.name = "cd_"+bone.name
		cd.scale = Vector((1, 1, 1))
		cd.location = (bone.tail_local - bone.head_local) * (1/0.3)
		cd.show_x_ray = True
		cd.parent = so0

		so0.spr_ik_enabled = True
		so0.spr_ik_tip_use_obj = True
		so0.spr_ik_tip_object_name = cd.name
		so0.spr_ik_pos_control_enabled = False

		bpy.context.scene.objects[cd.name].select = True
		bpy.ops.object.group_link(group=armature.name)
		bpy.context.scene.objects[cd.name].select = False

	# ---

	return (so0, jo0)


def link_solid_and_bone(armature_obj):
	bpy.ops.object.mode_set(mode='POSE')

	armature = bpy.data.armatures[armature_obj.data.name]
	print(type(armature_obj))
	for bone in armature.bones:
		armature.bones.active = bone

		bpy.ops.pose.constraint_add(type='COPY_ROTATION')
		armature_obj.pose.bones[bone.name].constraints["Copy Rotation"].target = bpy.data.objects["so_"+bone.name]
		armature_obj.pose.bones[bone.name].constraints["Copy Rotation"].owner_space = "LOCAL_WITH_PARENT"

		bpy.ops.pose.constraint_add(type='COPY_LOCATION')
		armature_obj.pose.bones[bone.name].constraints["Copy Location"].target = bpy.data.objects["so_"+bone.name]


# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# Utility Functions
# 

def copy(v):
	'''どんなベクトル等であってもコピーする関数'''
	if type(v) is Vec2d:
		return Vec2d(v.x, v.y)

	if type(v) is Vec2f:
		return Vec2f(v.x, v.y)

	if type(v) is Vec3d:
		return Vec3d(v.x, v.y, v.z)

	if type(v) is Vec3f:
		return Vec3f(v.x, v.y, v.z)

	if type(v) is Quaterniond:
		return Quaterniond(v.w, v.x, v.y, v.z)

	if type(v) is Quaternionf:
		return Quaternionf(v.w, v.x, v.y, v.z)

	if type(v) is Posed:
		return Posed(copy(v.getPos()), copy(v.getOri()))

	if type(v) is Posef:
		return Posed(copy(v.getPos()), copy(v.getOri()))

	if type(v) is Vector:
		return v.copy()

	if type(v) is Quaternion:
		return v.copy()

	if type(v) is Matrix:
		return v.copy()

	if type(v) is list:
		r = []
		for i in v:
			r.append(copy(i))
		return r

	return v


def to_f(v):
	'''XXXd を XXXf にする'''
	if type(v) is Vec2d:
		return Vec2f(v.x, v.y)

	if type(v) is Vec3d:
		return Vec3f(v.x, v.y, v.z)

	if type(v) is Quaterniond:
		return Quaternionf(v.w, v.x, v.y, v.z)

	if type(v) is Posed:
		return Posef(to_f(v.getPos()), to_f(v.getOri()))

	if type(v) is list:
		r = []
		for i in v:
			r.append(to_f(i))
		return r

	return v


def to_d(v):
	'''XXXf を XXXd にする'''
	if type(v) is Vec2f:
		return Vec2d(v.x, v.y)

	if type(v) is Vec3f:
		return Vec3d(v.x, v.y, v.z)

	if type(v) is Quaternionf:
		return Quaterniond(v.w, v.x, v.y, v.z)

	if type(v) is Posef:
		return Posed(to_d(v.getPos()), to_d(v.getOri()))

	if type(v) is list:
		r = []
		for i in v:
			r.append(to_d(i))
		return r

	return v


def to_2d(v):
	'''3次元ベクトルのx, yから2次元ベクトルを作る'''
	if type(v) is Vector:
		return Vector((v.x, v.y))
	if type(v) is Vec3d:
		return Vec2d(v.x, v.y)
	return v


def to_spr(v):
	'''bpyのベクトルやクォータニオンをsprに変換する関数'''
	if type(v) is Vector:
		if len(v)==2:
			return Vec2d(v.x, v.y)
		if len(v)==3:
			return Vec3d(v.x, v.y, v.z)

	if type(v) is Quaternion:
		return Quaterniond(v.w, v.x, v.y, v.z)

	if type(v) is Matrix:
		p = v.to_translation()
		q = v.to_quaternion()
		pose = Posed(Vec3d(p.x,p.y,p.z), Quaterniond(q.w,q.x,q.y,q.z))
		return pose

	if type(v) is list:
		r = []
		for i in v:
			r.append(to_spr(i))
		return r

	return v


def to_bpy(v):
	'''sprのベクトルやクォータニオンをbpyに変換する関数'''
	if type(v) is Vec2d or type(v) is Vec2f:
		return Vector((v.x, v.y))

	if type(v) is Vec3d or type(v) is Vec3f:
		return Vector((v.x, v.y, v.z))

	if type(v) is Quaterniond or type(v) is Quaternionf:
		return Quaternion((v.w, v.x, v.y, v.z))

	if type(v) is Posed or type(v) is Posef:
		a = Affined()
		m = Matrix()
		v.ToAffine(a)
		for i in range(4):
			m[i][0] = a.row(i).x
			m[i][1] = a.row(i).y
			m[i][2] = a.row(i).z
			m[i][3] = a.row(i).w
		return m

	if type(v) is list:
		r = []
		for i in v:
			r.append(to_bpy(i))
		return r

	return v


def scale_matrix(s):
	'''ベクトル表現のscaleをAffine行列に変換する'''
	return Matrix(((s.x,0,0,0), (0,s.y,0,0), (0,0,s.z,0), (0,0,0,1)))


def bpy_object_pose(obj):
	'''matrix_worldに相当するものを（matrix_worldを使わずに）得る関数'''
	obj.rotation_mode = 'QUATERNION'

	rot = obj.rotation_quaternion.to_matrix()
	loc = obj.location
	mat  = Matrix()
	for i in range(0,3):
		for j in range(0,3):
			mat[i][j] = rot[i][j]
		mat[i][3] = loc[i]

	if not obj.parent is None:
		pp  = bpy_object_pose(obj.parent)
		pi  = obj.matrix_parent_inverse
		sc  = scale_matrix(obj.parent.scale)
		mat = pp * sc * pi * mat

	return mat


def rad(deg):
	'''度をラジアンへ変換'''
	if deg is None:
		return rad
	return deg / 180.0 * 3.1415926


def deg(rad):
	'''ラジアンを度へ変換'''
	if rad is None:
		return 0
	return rad * 180.0 / 3.1415926


def angle_normalize(rad_angle):
	return cyclic_normalize(rad_angle, (rad(-180),rad(180)), rad(360))

def cyclic_normalize(value, rng, period):
	while value > rng[1]:
		value -= period
	while value < rng[0]:
		value += period
	return value


def angle_diff(rad1, rad2):
	rad1 = angle_normalize(rad1)
	rad2 = angle_normalize(rad2)
	if rad2 > rad1:
		diff1 = rad2 - rad1
		diff2 = rad1 - rad2 + rad(360)
	else:
		diff1 = rad1 - rad2
		diff2 = rad2 - rad1 + rad(360)
	return min(diff1, diff2)


def angle_close(current, target, limit):
	current = angle_normalize(current)
	target  = angle_normalize(target)
	if angle_diff(current, target) < limit:
		return target
	if (target < current):
		if ((current-target) < (target-current+rad(360))):
			direction = -1
		else:
			direction = +1
	else:
		if ((target-current) < (current-target+rad(360))):
			direction = +1
		else:
			direction = -1
	return current + (direction * limit)


def show_icons(layout):
	'''layoutにアイコン一覧を表示するテスト用関数'''
	icons = ['NONE', 'QUESTION', 'ERROR', 'CANCEL', 'TRIA_RIGHT', 'TRIA_DOWN', 'TRIA_LEFT', 'TRIA_UP', 'ARROW_LEFTRIGHT', 'PLUS', 'DISCLOSURE_TRI_DOWN', 'DISCLOSURE_TRI_RIGHT', 'RADIOBUT_OFF', 'RADIOBUT_ON', 'MENU_PANEL', 'BLENDER', 'DOT', 'X', 'GO_LEFT', 'PLUG', 'UI', 'NODE', 'NODE_SEL', 'FULLSCREEN', 'SPLITSCREEN', 'RIGHTARROW_THIN', 'BORDERMOVE', 'VIEWZOOM', 'ZOOMIN', 'ZOOMOUT', 'PANEL_CLOSE', 'COPY_ID', 'EYEDROPPER', 'LINK_AREA', 'AUTO', 'CHECKBOX_DEHLT', 'CHECKBOX_HLT', 'UNLOCKED', 'LOCKED', 'UNPINNED', 'PINNED', 'SCREEN_BACK', 'RIGHTARROW', 'DOWNARROW_HLT', 'DOTSUP', 'DOTSDOWN', 'LINK', 'INLINK', 'PLUGIN', 'HELP', 'GHOST_ENABLED', 'COLOR', 'LINKED', 'UNLINKED', 'HAND', 'ZOOM_ALL', 'ZOOM_SELECTED', 'ZOOM_PREVIOUS', 'ZOOM_IN', 'ZOOM_OUT', 'RENDER_REGION', 'BORDER_RECT', 'BORDER_LASSO', 'FREEZE', 'STYLUS_PRESSURE', 'GHOST_DISABLED', 'NEW', 'FILE_TICK', 'QUIT', 'URL', 'RECOVER_LAST', 'FULLSCREEN_ENTER', 'FULLSCREEN_EXIT', 'BLANK1', 'LAMP', 'MATERIAL', 'TEXTURE', 'ANIM', 'WORLD', 'SCENE', 'EDIT', 'GAME', 'RADIO', 'SCRIPT', 'PARTICLES', 'PHYSICS', 'SPEAKER', 'TEXTURE_SHADED', 'VIEW3D', 'IPO', 'OOPS', 'BUTS', 'FILESEL', 'IMAGE_COL', 'INFO', 'SEQUENCE', 'TEXT', 'IMASEL', 'SOUND', 'ACTION', 'NLA', 'SCRIPTWIN', 'TIME', 'NODETREE', 'LOGIC', 'CONSOLE', 'PREFERENCES', 'CLIP', 'ASSET_MANAGER', 'OBJECT_DATAMODE', 'EDITMODE_HLT', 'FACESEL_HLT', 'VPAINT_HLT', 'TPAINT_HLT', 'WPAINT_HLT', 'SCULPTMODE_HLT', 'POSE_HLT', 'PARTICLEMODE', 'LIGHTPAINT', 'SCENE_DATA', 'RENDERLAYERS', 'WORLD_DATA', 'OBJECT_DATA', 'MESH_DATA', 'CURVE_DATA', 'META_DATA', 'LATTICE_DATA', 'LAMP_DATA', 'MATERIAL_DATA', 'TEXTURE_DATA', 'ANIM_DATA', 'CAMERA_DATA', 'PARTICLE_DATA', 'LIBRARY_DATA_DIRECT', 'GROUP', 'ARMATURE_DATA', 'POSE_DATA', 'BONE_DATA', 'CONSTRAINT', 'SHAPEKEY_DATA', 'CONSTRAINT_BONE', 'PACKAGE', 'UGLYPACKAGE', 'BRUSH_DATA', 'IMAGE_DATA', 'FILE', 'FCURVE', 'FONT_DATA', 'RENDER_RESULT', 'SURFACE_DATA', 'EMPTY_DATA', 'SETTINGS', 'RENDER_ANIMATION', 'RENDER_STILL', 'BOIDS', 'STRANDS', 'LIBRARY_DATA_INDIRECT', 'GREASEPENCIL', 'GROUP_BONE', 'GROUP_VERTEX', 'GROUP_VCOL', 'GROUP_UVS', 'RNA', 'RNA_ADD', 'OUTLINER_OB_EMPTY', 'OUTLINER_OB_MESH', 'OUTLINER_OB_CURVE', 'OUTLINER_OB_LATTICE', 'OUTLINER_OB_META', 'OUTLINER_OB_LAMP', 'OUTLINER_OB_CAMERA', 'OUTLINER_OB_ARMATURE', 'OUTLINER_OB_FONT', 'OUTLINER_OB_SURFACE', 'OUTLINER_OB_SPEAKER', 'RESTRICT_VIEW_OFF', 'RESTRICT_VIEW_ON', 'RESTRICT_SELECT_OFF', 'RESTRICT_SELECT_ON', 'RESTRICT_RENDER_OFF', 'RESTRICT_RENDER_ON', 'OUTLINER_DATA_EMPTY', 'OUTLINER_DATA_MESH', 'OUTLINER_DATA_CURVE', 'OUTLINER_DATA_LATTICE', 'OUTLINER_DATA_META', 'OUTLINER_DATA_LAMP', 'OUTLINER_DATA_CAMERA', 'OUTLINER_DATA_ARMATURE', 'OUTLINER_DATA_FONT', 'OUTLINER_DATA_SURFACE', 'OUTLINER_DATA_SPEAKER', 'OUTLINER_DATA_POSE', 'MESH_PLANE', 'MESH_CUBE', 'MESH_CIRCLE', 'MESH_UVSPHERE', 'MESH_ICOSPHERE', 'MESH_GRID', 'MESH_MONKEY', 'MESH_CYLINDER', 'MESH_TORUS', 'MESH_CONE', 'LAMP_POINT', 'LAMP_SUN', 'LAMP_SPOT', 'LAMP_HEMI', 'LAMP_AREA', 'META_EMPTY', 'META_PLANE', 'META_CUBE', 'META_BALL', 'META_ELLIPSOID', 'META_CAPSULE', 'SURFACE_NCURVE', 'SURFACE_NCIRCLE', 'SURFACE_NSURFACE', 'SURFACE_NCYLINDER', 'SURFACE_NSPHERE', 'SURFACE_NTORUS', 'CURVE_BEZCURVE', 'CURVE_BEZCIRCLE', 'CURVE_NCURVE', 'CURVE_NCIRCLE', 'CURVE_PATH', 'FORCE_FORCE', 'FORCE_WIND', 'FORCE_VORTEX', 'FORCE_MAGNETIC', 'FORCE_HARMONIC', 'FORCE_CHARGE', 'FORCE_LENNARDJONES', 'FORCE_TEXTURE', 'FORCE_CURVE', 'FORCE_BOID', 'FORCE_TURBULENCE', 'FORCE_DRAG', 'MODIFIER', 'MOD_WAVE', 'MOD_BUILD', 'MOD_DECIM', 'MOD_MIRROR', 'MOD_SOFT', 'MOD_SUBSURF', 'HOOK', 'MOD_PHYSICS', 'MOD_PARTICLES', 'MOD_BOOLEAN', 'MOD_EDGESPLIT', 'MOD_ARRAY', 'MOD_UVPROJECT', 'MOD_DISPLACE', 'MOD_CURVE', 'MOD_LATTICE', 'CONSTRAINT_DATA', 'MOD_ARMATURE', 'MOD_SHRINKWRAP', 'MOD_CAST', 'MOD_MESHDEFORM', 'MOD_BEVEL', 'MOD_SMOOTH', 'MOD_SIMPLEDEFORM', 'MOD_MASK', 'MOD_CLOTH', 'MOD_EXPLODE', 'MOD_FLUIDSIM', 'MOD_MULTIRES', 'MOD_SMOKE', 'MOD_SOLIDIFY', 'MOD_SCREW', 'MOD_VERTEX_WEIGHT', 'MOD_DYNAMICPAINT', 'MOD_REMESH', 'REC', 'PLAY', 'FF', 'REW', 'PAUSE', 'PREV_KEYFRAME', 'NEXT_KEYFRAME', 'PLAY_AUDIO', 'PLAY_REVERSE', 'PREVIEW_RANGE', 'PMARKER_ACT', 'PMARKER_SEL', 'PMARKER', 'MARKER_HLT', 'MARKER', 'SPACE2', 'SPACE3', 'KEYINGSET', 'KEY_DEHLT', 'KEY_HLT', 'MUTE_IPO_OFF', 'MUTE_IPO_ON', 'VISIBLE_IPO_OFF', 'VISIBLE_IPO_ON', 'DRIVER', 'SOLO_OFF', 'SOLO_ON', 'FRAME_PREV', 'FRAME_NEXT', 'VERTEXSEL', 'EDGESEL', 'FACESEL', 'ROTATE', 'CURSOR', 'ROTATECOLLECTION', 'ROTATECENTER', 'ROTACTIVE', 'ALIGN', 'SMOOTHCURVE', 'SPHERECURVE', 'ROOTCURVE', 'SHARPCURVE', 'LINCURVE', 'NOCURVE', 'RNDCURVE', 'PROP_OFF', 'PROP_ON', 'PROP_CON', 'PARTICLE_POINT', 'PARTICLE_TIP', 'PARTICLE_PATH', 'MAN_TRANS', 'MAN_ROT', 'MAN_SCALE', 'MANIPUL', 'SNAP_OFF', 'SNAP_ON', 'SNAP_NORMAL', 'SNAP_INCREMENT', 'SNAP_VERTEX', 'SNAP_EDGE', 'SNAP_FACE', 'SNAP_VOLUME', 'STICKY_UVS_LOC', 'STICKY_UVS_DISABLE', 'STICKY_UVS_VERT', 'CLIPUV_DEHLT', 'CLIPUV_HLT', 'SNAP_PEEL_OBJECT', 'GRID', 'PASTEDOWN', 'COPYDOWN', 'PASTEFLIPUP', 'PASTEFLIPDOWN', 'SNAP_SURFACE', 'RETOPO', 'UV_VERTEXSEL', 'UV_EDGESEL', 'UV_FACESEL', 'UV_ISLANDSEL', 'UV_SYNC_SELECT', 'BBOX', 'WIRE', 'SOLID', 'SMOOTH', 'POTATO', 'ORTHO', 'LOCKVIEW_OFF', 'LOCKVIEW_ON', 'AXIS_SIDE', 'AXIS_FRONT', 'AXIS_TOP', 'NDOF_DOM', 'NDOF_TURN', 'NDOF_FLY', 'NDOF_TRANS', 'LAYER_USED', 'LAYER_ACTIVE', 'SORTALPHA', 'SORTBYEXT', 'SORTTIME', 'SORTSIZE', 'LONGDISPLAY', 'SHORTDISPLAY', 'GHOST', 'IMGDISPLAY', 'BOOKMARKS', 'FONTPREVIEW', 'FILTER', 'NEWFOLDER', 'FILE_PARENT', 'FILE_REFRESH', 'FILE_FOLDER', 'FILE_BLANK', 'FILE_BLEND', 'FILE_IMAGE', 'FILE_MOVIE', 'FILE_SCRIPT', 'FILE_SOUND', 'FILE_FONT', 'BACK', 'FORWARD', 'DISK_DRIVE', 'MATPLANE', 'MATSPHERE', 'MATCUBE', 'MONKEY', 'HAIR', 'ALIASED', 'ANTIALIASED', 'MAT_SPHERE_SKY', 'WORDWRAP_OFF', 'WORDWRAP_ON', 'SYNTAX_OFF', 'SYNTAX_ON', 'LINENUMBERS_OFF', 'LINENUMBERS_ON', 'SCRIPTPLUGINS', 'SEQ_SEQUENCER', 'SEQ_PREVIEW', 'SEQ_LUMA_WAVEFORM', 'SEQ_CHROMA_SCOPE', 'SEQ_HISTOGRAM', 'SEQ_SPLITVIEW', 'IMAGE_RGB', 'IMAGE_RGB_ALPHA', 'IMAGE_ALPHA', 'IMAGE_ZDEPTH', 'IMAGEFILE', 'BRUSH_ADD', 'BRUSH_BLOB', 'BRUSH_BLUR', 'BRUSH_CLAY', 'BRUSH_CLONE', 'BRUSH_CREASE', 'BRUSH_DARKEN', 'BRUSH_FILL', 'BRUSH_FLATTEN', 'BRUSH_GRAB', 'BRUSH_INFLATE', 'BRUSH_LAYER', 'BRUSH_LIGHTEN', 'BRUSH_MIX', 'BRUSH_MULTIPLY', 'BRUSH_NUDGE', 'BRUSH_PINCH', 'BRUSH_SCRAPE', 'BRUSH_SCULPT_DRAW', 'BRUSH_SMEAR', 'BRUSH_SMOOTH', 'BRUSH_SNAKE_HOOK', 'BRUSH_SOFTEN', 'BRUSH_SUBTRACT', 'BRUSH_TEXDRAW', 'BRUSH_THUMB', 'BRUSH_ROTATE', 'BRUSH_VERTEXDRAW', 'VIEW3D_VEC', 'EDIT_VEC', 'EDITMODE_DEHLT', 'EDITMODE_HLT', 'DISCLOSURE_TRI_RIGHT_VEC', 'DISCLOSURE_TRI_DOWN_VEC', 'MOVE_UP_VEC', 'MOVE_DOWN_VEC', 'X_VEC', 'SMALL_TRI_RIGHT_VEC']
	for icon_ in icons:
	 	layout.label(text=icon_, icon = icon_)



def synchronized(lock_get_func):
	'''関数呼び出しのSynchronizeを実現するデコレータ'''
	'''@synchronize(lambda self: self.lock) のように使う。'''
	def wrap(f):
		def wrapped_func(*args, **kw):
			self = args[0]
			lock = lock_get_func(self)
			lock.acquire()
			try:
				return f(*args, **kw)
			finally:
				lock.release()
		return wrapped_func
	return wrap



def make_material(name, diffuse, specular, alpha):
	'''マテリアルを作成する'''
	mat = bpy.data.materials.new(name)
	mat.diffuse_color = diffuse
	mat.diffuse_shader = 'LAMBERT' 
	mat.diffuse_intensity = 1.0 
	mat.specular_color = specular
	mat.specular_shader = 'COOKTORR'
	mat.specular_intensity = 0.5
	mat.alpha = alpha
	mat.ambient = 1
	return mat


def prepare_material(mat_name, diffuse, specular, alpha):
	'''マテリアルを作成または取得（既存の場合）する'''
	try:
		mat = bpy.data.materials[mat_name]
	except:
		mat = make_material(mat_name, diffuse, specular, alpha)
		mat.use_transparency		= 1
		mat.use_shadeless			= True
		mat.use_cast_buffer_shadows = False

	return mat


def set_material(ob, mat):
	'''マテリアルをセットする'''
	me = ob.data
	me.materials.append(mat)


def create_mesh(name, origin, verts, edges, faces):
	'''メッシュを作成する'''
	# Create mesh and object
	me = bpy.data.meshes.new(name+'Mesh')
	ob = bpy.data.objects.new(name, me)
	ob.location = origin
	ob.show_name = True
	# Link object to scene
	scn = bpy.context.scene
	scn.objects.link(ob)
	scn.objects.active = ob
	scn.update()

	# Create mesh from given verts, edges, faces. 
	# Either edges or faces should be [], or you ask for problems
	me.from_pydata(verts, edges, faces)

	# Update mesh with new data
	me.update(calc_edges=True)

	return ob
	

def glDrawSphere(radius, slices, stacks):
	'''球を描画する関数'''
	for s in range(0,stacks):
		z0 = ((s+0)*(2*radius)/stacks) - radius
		z1 = ((s+1)*(2*radius)/stacks) - radius
		r0 = sqrt(radius*radius - z0*z0)
		r1 = sqrt(radius*radius - z1*z1)
		
		bgl.glBegin(bgl.GL_QUAD_STRIP);
		for i in range(0,slices+1):
			x = sin(((2.0 * 3.14159) / slices) * i);
			y = cos(((2.0 * 3.14159) / slices) * i);
			bgl.glVertex3f(r0 * x, r0 * y, z0);
			bgl.glVertex3f(r1 * x, r1 * y, z1);
		bgl.glEnd();


# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# Utility Class
# 

class Var():
	'''変数の変化率・ローパスフィルタ等を自動で計算するしくみ'''
	def __init__(self, default, alpha=1.0, diff_alpha=1.0, predict=False, clear_input=True, keep_value=False):
		self.default      = default

		self.curr_var     = self.default()
		self.last_var     = self.default()
		self.diff_var     = self.default()

		self.v_input      = self.default()
		self.n_input      = 0
		self.b_input      = False
		self.last_b_input = False

		self.alpha        = alpha
		self.diff_alpha   = diff_alpha

		self.predict      = predict
		self.clear_input  = clear_input
		self.keep_value   = keep_value

	def clear(self):
		if self.clear_input:
			self.v_input  = self.default()
		self.n_input  = 0
		self.b_input  = False

	def input(self, value):
		if self.clear_input:
			self.v_input += value
		else:
			self.v_input  = value
		self.n_input += 1
		self.b_input  = True

	def update(self, dt=1):
		diff = self.default()
		if self.b_input:
			# 入力値の平均をとる
			value = self.v_input * (1 / self.n_input)

			# ローパスを適用
			self.curr_var = (self.curr_var*(1-self.alpha)) + (value*self.alpha)

			if self.last_b_input:
				# 入力にもとづき変化率を算出
				diff = (self.curr_var - self.last_var) * (1 / dt)

		else:
			if self.predict:
				# 予測する場合：変化率にもとづき値を予測
				self.curr_var = self.curr_var + (self.diff_var * dt)
				diff = self.diff_var

			else:
				if not self.keep_value:
					# 予測しない場合：clear後の値（たいていデフォルト値）に近づける
					self.curr_var = (self.curr_var*(1-self.alpha)) + (self.v_input*self.alpha)


		self.last_b_input = self.b_input
		self.last_var     = self.curr_var

		# 変化率にローパスを適用
		self.diff_var = (self.diff_var*(1-self.diff_alpha)) + (diff*(self.diff_alpha))


class GainAdjuster():
	'''過去の最大値に基づいて自動で数値を0.0～1.0に正規化する。
	変数ごとに一意なKeyを割り当てること。
	使用例： GainAdjuster(0)[ ～～～～～ ] '''
	max_values = defaultdict(lambda: 1)

	def __init__(self, key):
		self.key      = key

	def __getitem__(self, v):
		if self.max_values[self.key] < v:
			self.max_values[self.key] = v
		m  = self.max_values[self.key]
		rv = (v / m) if (m > 1e-3) else 0
		return rv

	@classmethod
	def update(cls):
		'''GainAdjuster.update() を 1stepに1回だけ呼ぶこと。'''
		for k,v in cls.max_values.items():
			cls.max_values[k] = max(cls.max_values[k] - 0.0002, 0)


class KeepMaxLevelMeter():
	'''最大値を指定秒数保持するレベルメータ'''
	def __init__(self, keep_time):
		self.keep_time    = keep_time
		self.max          = 0
		self.max_up_time  = time.time()

	def input(self, value):
		if self.max < value:
			self.max = value
			self.max_up_time = time.time()

		if time.time() - self.max_up_time > self.keep_time:
			self.max = max(self.max - 0.2, 0)



# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----

class NoneCheckDict(OrderedDict):
	'''要素が存在しない場合はNoneを返すdict．ついでに要素の順番も保持する。
	defaultdictと違い，存在しない要素にアクセスしても要素として追加はしない．'''

	def __getitem__(self, key):
		if key in self.keys():
			return dict.__getitem__(self, key)
		else:
			return None



class Profilers:
	'''実行時間計測クラス'''

	def __init__(self):
		self.curr_id   = 0
		self.profilers = defaultdict(lambda: Profiler())

	def start(self, id=0):
		'''ループ内の時間計測開始地点に置く．'''
		self.curr_id = id
		self.profilers[id].start(id)

	def lap(self, id=None):
		'''各計測ポイントに置く．start->lap間, およびlap->lap間の時間が測定される．'''
		id = id or self.curr_id
		self.profilers[id].lap()



class Profiler:
	'''Profilersが内部的に使う実働クラス'''
	def __init__(self):
		self.count     = 0
		self.id        = 0
		self.time_sum  = defaultdict(lambda: 0)
		self.starttime = time.time()

	def start(self, prof_id=0):
		self.id     = 0
		self.count += 1
		self.last   = time.time()

		now = time.time()
		if now - self.starttime > 5:
			print(" -- ", prof_id, " -- ")
			for i in range(0, len(self.time_sum)):
				print(i, " : ", ((self.time_sum[i]/self.count)*1000000).__int__()/1000.0, "[ms]")
				self.time_sum[i] = 0
			self.starttime = now
			self.count = 0

	def lap(self):
		now = time.time()
		self.time_sum[self.id] += (now - self.last)
		self.last  = now
		self.id   += 1

profiler = Profilers()
profiler.start()



class DebugLog:
	'''デバッグ用タイムスタンプ付きログ'''

	def __init__(self):
		self.count  = 0
		self.logs   = []

		'''ログターゲット'''
		self.log_print = False
		self.log_file  = False

		'''
		ログレベル
		'''
		self.levels = {
			"NONE"         :  0,  # 何も出力しない
			"ERROR"        :  1,  # エラー
			"WARNING"      :  5,  # 警告
			"EVENT"        : 10,  # 変化があった、それを受けて動作した
			"MINOR_EVENT"  : 15,  # 些細な変化があった、それを受けて些細な動作を行った
			"END"          : 20,  # 何らかの定期的な処理を完了した（特別な処理はACTIONに）
			"BEGIN"        : 25,  # 何らかの定期的な処理を開始した
			"PASS"         : 30,  # 何らかのチェックポイントを通過した
			"ALL"          : 99,  # すべて
		}
		self.level  = "NONE"

		'''バッファカウント：ファイル出力時にこの数に達したら出力する'''
		self.buffer_cnt = 1

	def log(self, level, *args):
		if not level in self.levels:
			return
		if not self.level in self.levels:
			return

		if self.levels[level] <= self.levels[self.level]:
			if self.log_print:
				print("[spb]", '<'+level+'>', int(time.time()), ' '.join(map(str,args)))

			if self.log_file:
				self.logs.append( (time.time(), '<'+level+'>'+(' '.join(map(str,args))) ) )
				self.count += 1
				if self.count >= self.buffer_cnt:
					ofp = open("C:/Users/mitake/Projects/Trunk/SprBlender/spbapi_cpp/log/log.txt", "a")
					for item in self.logs:
						ofp.write(item[0].__str__() + "\t" + item[1] + "\n")
					# ofp.write("<<<End Of Block>>>\n")
					ofp.close
					self.count = 0
					self.logs  = []

debuglog = DebugLog()

def logged(func):
	'''関数呼び出しの際にdebuglogに出力するデコレータ'''
	def wrap(*args, **kwargs):
		debuglog.log("BEGIN", args[0].__class__.__name__ + "::" + func.__name__ + str(args[1:]))
		func(*args, **kwargs)
		debuglog.log("END",   args[0].__class__.__name__ + "::" + func.__name__ + str(args[1:]))
	return wrap




class PetariLeap():
	def __init__(self):
		self.springs  = defaultdict(lambda: defaultdict(lambda: None))
		self.lastVels = defaultdict(lambda: Vec3d())
		self.grabness = defaultdict(lambda: 0.0)

		self.lastStepCnt = 0

	def step(self):
		phScene = spb.handlers.scene_handler.spr()

		dt = (phScene.GetCount() - self.lastStepCnt) * phScene.GetTimeStep()
		self.lastStepCnt = phScene.GetCount()

		fwLeap = spb.spbapi_cpp.CreateLeap()
		for i in range(fwLeap.NSkeleton()):
			gs = fwLeap.GetSkeleton(i).GetGrabStrength()
			#print("                    Grab : ", i, gs)
			for j in range(fwLeap.GetSkeleton(i).NBones()):
				self.grabness[fwLeap.GetSkeleton(i).GetBone(j).GetSolid()] = gs

		for so in phScene.GetSolids():
			if "Leap" in so.GetName():
				currVel = so.GetVelocity()
				lastVel = self.lastVels[so]
				self.lastVels[so] = currVel
				accel = ((currVel - lastVel) * (1/dt)).norm()
				for so2,spring in self.springs[so].items():
					thresh = (self.grabness[so] - 0.5) * 400.0
					#if thresh < accel:
					#print("				grabness : " , so.GetName(), self.grabness[so])
					if self.grabness[so] <= 0.7 and spring.IsEnabled():
						spring.Enable(False)
						print("Disable", so.GetName(), so2.GetName())
					if (so.GetPose().getPos() - so2.GetPose().getPos()).norm() > 500 and spring.IsEnabled():
						so2.SetVelocity(Vec3d())
						so2.SetAngularVelocity(Vec3d())
						spring.Enable(False)


		for so1 in phScene.GetSolids():
			for so2 in phScene.GetSolids():
				if "Leap" in so1.GetName() and "Apple" in so2.GetName():
					force  = phScene.GetConstraintEngine().GetContactPoints().GetTotalForce(so1, so2).norm()
					force += phScene.GetConstraintEngine().GetContactPoints().GetTotalForce(so2, so1).norm()
					if force > 1e-3:
						if self.springs[so1][so2] is not None:
							self.springs[so1][so2].Enable(True)
						else:
							desc = PHSpringDesc()
							desc.spring = Vec3d(1,1,1) * 500.0
							desc.damper = Vec3d(1,1,1) *  50.0
							desc.springOri = 100.0
							desc.damperOri =  10.0
							spring = phScene.CreateJoint(so1,so2,PHSpring.GetIfInfoStatic(),desc)
							self.springs[so1][so2] = spring

