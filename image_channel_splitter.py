# -*- coding: utf-8 -*-

# BismillahirRahmanirRahim

# project_name: 'blender_image_channel_splitter'
# project_web: 'https://github.com/erdinc-me/blender_image_channel_splitter'
# file_web: 'https://github.com/erdinc-me/blender_image_channel_splitter/blob/master/image_channel_splitter.py'
# date: '06/22/16'
# author, maintainer : 'Erdinç Yılmaz'
# author_web: 'http://erdinc.me'
# author_github: 'https://github.com/erdinc-me/'
# email: '@'
# license: 'GPLv3, see LICENSE for more details'
# LICENSE: 'https://github.com/erdinc-me/blender_image_channel_splitter/blob/master/LICENSE'
# copyright: '(C) 2016 Erdinç Yılmaz.'
# version: '1.0 RC'
# status: 'Release Candidate'

bl_info = {
    "name": "Image Channel Splitter",
    "description": "Splits image channels to individual single channel grayscale images. ",
    "author": "Erdinc Yilmaz",
    "version": (0, 0, 1),
    "blender": (2, 70, 0),
    "location": "Node Editor > Tool Shelf (T)",
    "warning": "If pillow or pil is not installed, blender api will be used and it can be"
               " a memory monster for a few seconds.",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Node"
}

import os.path
import bpy


from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       PropertyGroup,
                       EnumProperty,
                       )

try:
    from PIL import Image
    is_pil_imported = True

    # ---------------------------------------------------------------------
    def load_image_created_with_pil(bw_img_path, is_create_texture_node):
        # img.file_format = img_format

        # img = bpy.data.images.load(bw_img_path, check_existing=True)
        # check_existing=True implemented in 2, 76, 1 version of blender. To support older versions we will not use it.
        # instead;
        img = None
        for i in bpy.data.images:
            if i.filepath_raw == bw_img_path:
                i.reload()
                img = i
                # return
                break
        if not img:
            img = bpy.data.images.load(bw_img_path)

        if is_create_texture_node:
            # active_node = bpy.context.active_node
            mat = bpy.context.object.active_material
            # get the nodes
            nodes = mat.node_tree.nodes

            for n in nodes:
                if n.label == img.name:
                    return

            node_texture = nodes.new(type='ShaderNodeTexImage')
            node_texture.image = img
            node_texture.name = "Image Texture"
            node_texture.label = img.name
            node_texture.color_space = "NONE"
            # node_texture.location = active_node.location[0], active_node.location[1] - active_node.bl_height_min
            node_texture.hide = True
            node_texture.select = False
            node_texture.location = bpy.context.scene.ImageChannelSplitter.locationX, \
                                    bpy.context.scene.ImageChannelSplitter.locationY

            bpy.context.scene.ImageChannelSplitter.locationY -= 40
            node_texture.width_hidden = bpy.context.active_node.width
            # node_texture.select = True
            # nodes.active = node_texture

    # ---------------------------------------------------------------------
    def create_and_save_single_channel_images_with_pil(context, img_path):

        ics = context.scene.ImageChannelSplitter

        r = ics.is_red_channel
        g = ics.is_green_channel
        b = ics.is_blue_channel
        a = ics.is_alpha_channel
        average = ics.is_average
        weighted_average = ics.is_weighted_average

        # for remaining percentage display
        selected_channels = [r, g, b, a, average, weighted_average]
        remained = sum(1 for x in selected_channels if x)
        del selected_channels
        wm = bpy.context.window_manager
        wm.progress_begin(0, remained)
        wm.progress_update(remained)
        # ics.progress = "Please wait !"

        if ics.is_custom_save_path:
            save_dir = ics.custom_save_path
        else:
            save_dir = os.path.dirname(img_path)

        img_format = ics.image_format_menu
        if img_format in ["PNG", "TIFF"]:
            depth = ics.depth_menu
        else:
            depth = "8"

        is_create_texture_node = ics.is_create_texture_node
        is_unlink = ics.is_unlink

        basename_without_extension = os.path.splitext(os.path.basename(img_path))[0]
        # src_pixels = list(src_image.pixels)
        # print(sys.getsizeof(gl))

        active_node = bpy.context.active_node
        height = active_node.dimensions[1]

        bpy.context.scene.ImageChannelSplitter.locationX = active_node.location[0]
        bpy.context.scene.ImageChannelSplitter.locationY = active_node.location[1] - height - 15

        # im = Image.open('image.gif')
        # rgb_im = im.convert('RGB')
        # r, g, b = rgb_im.getpixel((1, 1))

        img = Image.open(img_path, 'r')
        mode = img.mode
        aa = None
        if mode == "RGB":
            rr, gg, bb = img.split()
        elif mode == "RGBA":
            rr, gg, bb, aa = img.split()
        else:
            return

        if average:
            bwfilename = "{}_average.{}".format(basename_without_extension, img_format.lower())
            bwfilepath = os.path.join(save_dir, bwfilename)

            # bwimg = convert_to_gs(img)
            rgb2xyz = (
                0.33333, 0.33333, 0.33333, 0)
            bwimg = img.convert("L", rgb2xyz)
            bwimg.save(bwfilepath, img_format.lower())
            load_image_created_with_pil(bwfilepath, is_create_texture_node)
            del bwimg
            remained -= 1
            wm.progress_update(remained)
            # ics.progress = "{} / {} done".format(total-remained, total)

        if weighted_average:
            bwfilename = "{}_weighted_average.{}".format(basename_without_extension, img_format.lower())
            bwfilepath = os.path.join(save_dir, bwfilename)
            bwimg = img.convert('L')
            bwimg.save(bwfilepath, img_format.lower())
            load_image_created_with_pil(bwfilepath, is_create_texture_node)
            del bwimg
            remained -= 1
            wm.progress_update(remained)

        if r:
            bwfilename = "{}_red.{}".format(basename_without_extension, img_format.lower())
            bwfilepath = os.path.join(save_dir, bwfilename)
            rr.save(bwfilepath, img_format.lower())
            load_image_created_with_pil(bwfilepath, is_create_texture_node)
            del rr
            remained -= 1
            wm.progress_update(remained)

        if g:
            bwfilename = "{}_green.{}".format(basename_without_extension, img_format.lower())
            bwfilepath = os.path.join(save_dir, bwfilename)
            gg.save(bwfilepath, img_format.lower())
            load_image_created_with_pil(bwfilepath, is_create_texture_node)
            del gg
            remained -= 1
            wm.progress_update(remained)

        if b:
            bwfilename = "{}_blue.{}".format(basename_without_extension, img_format.lower())
            bwfilepath = os.path.join(save_dir, bwfilename)
            bb.save(bwfilepath, img_format.lower())
            load_image_created_with_pil(bwfilepath, is_create_texture_node)
            del bb
            remained -= 1
            wm.progress_update(remained)

        # TODO: need to implement a checking mechanism for detecting alpha channel
        # with pil after changing node selection.
        # there was one but it was in the draw method of the panel class,
        # and it was constantly loading image from hd. so not very usable.
        # for now this will bypass alpha channel if there is not one. and wont update the add-on ui.
        if a:
            if aa:
                bwfilename = "{}_alpha.{}".format(basename_without_extension, img_format.lower())
                bwfilepath = os.path.join(save_dir, bwfilename)
                aa.save(bwfilepath, img_format.lower())
                load_image_created_with_pil(bwfilepath, is_create_texture_node)
                del aa
                remained -= 1
                wm.progress_update(remained)
            else:
                pass

        del img
        wm.progress_end()
        # context.scene.ImageChannelSplitter.progress = "All Done!"


except ImportError:
    is_pil_imported = False


# ---------------------------------------------------------------------
def save_bw_image_with_blender(img, filepath, img_format, depth):
    settings = bpy.context.scene.render.image_settings

    # save current render settings of the scene
    current_format = settings.file_format
    current_mode = settings.color_mode
    current_depth = settings.color_depth

    # temporary altering render settings of the scene
    settings.file_format = img_format
    settings.color_mode = "BW"
    settings.color_depth = depth

    img.save_render(filepath)

    # reset to original render settings of the scene
    settings.file_format = current_format
    settings.color_mode = current_mode
    settings.color_depth = current_depth


# ---------------------------------------------------------------------
def save_created_images_with_blender(img, img_format, depth, newfilename, save_dir, is_create_texture_node):
    # img.file_format = img_format

    img.filepath_raw = os.path.join(save_dir, newfilename)
    # img.save()
    save_bw_image_with_blender(img, img.filepath_raw, img_format, depth)
    # if is_unlink:
    #     nimg.user_clear()
    #     bpy.data.images.remove(nimg)

    bw_img_path = img.filepath_raw
    img.user_clear()
    bpy.data.images.remove(img)
    del img

    # img = bpy.data.images.load(bw_img_path, check_existing=True)
    # check_existing=True implemented in 2, 76, 1 version of blender. To support older versions we will not use it.
    # instead;
    img = None
    for i in bpy.data.images:
        if i.filepath_raw == bw_img_path:
            i.reload()
            img = i
            # return
            break
    if not img:
        img = bpy.data.images.load(bw_img_path)

    if is_create_texture_node:
        # active_node = bpy.context.active_node
        mat = bpy.context.object.active_material
        # get the nodes
        nodes = mat.node_tree.nodes

        for n in nodes:
            if n.label == img.name:
                return

        node_texture = nodes.new(type='ShaderNodeTexImage')
        node_texture.image = img
        node_texture.name = "Image Texture"
        node_texture.label = img.name
        node_texture.color_space = "NONE"
        # node_texture.location = active_node.location[0], active_node.location[1] - active_node.bl_height_min
        node_texture.hide = True
        node_texture.select = False
        node_texture.location = bpy.context.scene.ImageChannelSplitter.locationX, \
                                bpy.context.scene.ImageChannelSplitter.locationY

        bpy.context.scene.ImageChannelSplitter.locationY -= 40
        node_texture.width_hidden = bpy.context.active_node.width
        # node_texture.select = True
        # nodes.active = node_texture

# # ---------------------------------------------------------------------
# def get_chunks(l, n):
#     """yields n-sized chunks from l."""
#     for i in range(0, len(l), n):
#         yield l[i:i + n]


# ---------------------------------------------------------------------
def create_single_channel_images_with_blender(context):
    ics = context.scene.ImageChannelSplitter
    src_image = context.active_node.image

    r = ics.is_red_channel
    g = ics.is_green_channel
    b = ics.is_blue_channel
    a = ics.is_alpha_channel
    average = ics.is_average
    weighted_average = ics.is_weighted_average

    # for remaining percentage display
    selected_channels = [r, g, b, a, average, weighted_average]
    remained = sum(1 for x in selected_channels if x)
    wm = bpy.context.window_manager
    wm.progress_begin(0, remained)
    wm.progress_update(remained)
    # ics.progress = "Please wait !"

    if ics.is_custom_save_path:
        save_dir = ics.custom_save_path
    else:
        save_dir = os.path.dirname(src_image.filepath)

    img_format = ics.image_format_menu
    if img_format in ["PNG", "TIFF"]:
        depth = ics.depth_menu
    else:
        depth = "8"

    is_create_texture_node = ics.is_create_texture_node,
    is_unlink = ics.is_unlink

    # save_dir = os.path.dirname(src_image.filepath)
    basename_without_extension = os.path.splitext(os.path.basename(src_image.filepath))[0]
    # src_pixels = list(src_image.pixels)
    src_pixels = src_image.pixels[:]  # tuple
    total_pixels = len(src_pixels)
    w = src_image.size[0]
    h = src_image.size[1]

    # gl = list(get_chunks(src_pixels, 4))
    # gl = grouped_list = [src_pixels[i:i+4] for i in range(total_pixels)[::4]]
    gl = [src_pixels[i:i + 4] for i in range(0, total_pixels, 4)]
    # gl = get_chunks(src_pixels, 4)

    # print(sys.getsizeof(gl))

    active_node = bpy.context.active_node
    height = active_node.dimensions[1]

    bpy.context.scene.ImageChannelSplitter.locationX = active_node.location[0]
    bpy.context.scene.ImageChannelSplitter.locationY = active_node.location[1] - height - 15

    if average:
        newfilename = "{}_average.{}".format(basename_without_extension, img_format.lower())
        nimg = bpy.data.images.new(newfilename, w, h, alpha=False)

        singlechannelpixellist = []
        for px in gl:
            p = (px[0] + px[1] + px[2]) / 3
            singlechannelpixellist.extend([p, p, p, px[3]])

        nimg.pixels = singlechannelpixellist
        # nimg.pixels[:] = singlechannelpixellist

        del singlechannelpixellist
        save_created_images_with_blender(nimg, img_format, depth, newfilename, save_dir, is_create_texture_node)
        remained -= 1
        wm.progress_update(remained)
        # ics.progress = "{} / {} done".format(total-remained, total)

    if weighted_average:
        newfilename = "{}_weighted_average.{}".format(basename_without_extension, img_format.lower())
        nimg = bpy.data.images.new(newfilename, w, h, alpha=False)

        singlechannelpixellist = []
        for px in gl:
            p = 0.299 * px[0] + 0.587 * px[1] + 0.114 * px[2]
            singlechannelpixellist.extend([p, p, p, px[3]])

        nimg.pixels = singlechannelpixellist
        del singlechannelpixellist
        save_created_images_with_blender(nimg, img_format, depth, newfilename, save_dir, is_create_texture_node)
        remained -= 1
        wm.progress_update(remained)

    if r:
        newfilename = "{}_red.{}".format(basename_without_extension, img_format.lower())
        nimg = bpy.data.images.new(newfilename, w, h, alpha=False)

        singlechannelpixellist = []
        for px in gl:
            singlechannelpixellist.extend([px[0], px[0], px[0], px[3]])

        nimg.pixels = singlechannelpixellist
        del singlechannelpixellist
        save_created_images_with_blender(nimg, img_format, depth, newfilename, save_dir, is_create_texture_node)
        remained -= 1
        wm.progress_update(remained)

    if g:
        newfilename = "{}_green.{}".format(basename_without_extension, img_format.lower())
        nimg = bpy.data.images.new(newfilename, w, h, alpha=False)

        singlechannelpixellist = []
        for px in gl:
            singlechannelpixellist.extend([px[1], px[1], px[1], px[3]])

        nimg.pixels = singlechannelpixellist
        del singlechannelpixellist
        save_created_images_with_blender(nimg, img_format, depth, newfilename, save_dir, is_create_texture_node)
        remained -= 1
        wm.progress_update(remained)

    if b:
        newfilename = "{}_blue.{}".format(basename_without_extension, img_format.lower())
        nimg = bpy.data.images.new(newfilename, w, h, alpha=False)

        singlechannelpixellist = []
        for px in gl:
            singlechannelpixellist.extend([px[2], px[2], px[2], px[3]])

        nimg.pixels = singlechannelpixellist
        del singlechannelpixellist
        save_created_images_with_blender(nimg, img_format, depth, newfilename, save_dir, is_create_texture_node)
        remained -= 1
        wm.progress_update(remained)

    if a:
        newfilename = "{}_alpha.{}".format(basename_without_extension, img_format.lower())
        nimg = bpy.data.images.new(newfilename, w, h, alpha=False)

        singlechannelpixellist = []
        for px in gl:
            singlechannelpixellist.extend([px[3], px[3], px[3], px[3]])

        nimg.pixels = singlechannelpixellist
        del singlechannelpixellist
        save_created_images_with_blender(nimg, img_format, depth, newfilename, save_dir, is_create_texture_node)
        remained -= 1
        wm.progress_update(remained)

    del src_pixels
    del gl
    wm.progress_end()


# ------------------------------------------------------------------------
#    storing properties in the active scene
# ------------------------------------------------------------------------

class ICSPanelSettings(PropertyGroup):

    locationX = IntProperty(
        name="locationX",
        default=0
    )

    locationY = IntProperty(
        name="locationY",
        default=0
    )

    is_red_channel = BoolProperty(
        name="Red Channel",
        description="Check this to create a new image from red channel.",
        default=True
    )

    is_green_channel = BoolProperty(
        name="Blue Channel",
        description="Check this to create a new image from green channel.",
        default=True
    )

    is_blue_channel = BoolProperty(
        name="Green Channel",
        description="Check this to create a new image from blue channel.",
        default=True
    )

    is_alpha_channel = BoolProperty(
        name="Alpha Channel",
        description="Check this to create a new image from alpha channel.",
        default=False
    )

    is_average = BoolProperty(
        name="Average",
        description="r=g=b=(r+g+b)/3",
        default=False
    )

    is_weighted_average = BoolProperty(
        name="Weighted Average",
        description="r=g=b=0.299*r + 0.587*g + 0.114*b",
        default=False
    )

    is_create_texture_node = BoolProperty(
        name="Create Texture Node",
        description="Check this to create texture nodes loaded with newly created images.",
        default=True
    )

    is_unlink = BoolProperty(
        name="Unlink",
        description="Check this to unlink separated channel images from blender after creating and saving them.",
        default=False
    )

    image_formats = [('TIFF', 'tif', '', 1),
                     ('TGA', 'tga', '', 2),
                     ('PNG', 'png', '', 3),
                     ('JPEG', 'jpg', '', 4),
                     ]

    image_format_menu = bpy.props.EnumProperty(
        items=image_formats,
        name="Format",
        description="image format to save: ",
        default="JPEG",
        # update=update_func
    )

    depth_menu = bpy.props.EnumProperty(
        items=[('8', '8', '', 1), ('16', '16', '', 2)],
        name="Depth",
        description="Channel depth: ",
        default="8",
        # update=update_func
    )

    is_custom_save_path = BoolProperty(
        name="",
        description="Check this to set custom save path",
        default=False
    )

    custom_save_path = StringProperty(
        name="",
        description="Choose a directory:",
        default=os.path.expanduser("~"),
        maxlen=1024,
        subtype='DIR_PATH')

    # progress = StringProperty(
    #     name="",
    #     description="progress",
    #     default="",
    #     maxlen=1024,
    # )


########################################################################
class SplitChannelsButton(bpy.types.Operator):
    bl_idname = "ics.split_button"
    bl_label = "Split and Save"

    @classmethod
    def poll(cls, context):

        # space = context.space_data
        # return space.type == 'NODE_EDITOR'
        if hasattr(context.active_node.image, "filepath_raw"):
            # if not "Render Result" is selected
            if context.active_node.image.filepath:
                return True

    def execute(self, context):
        if is_pil_imported:

            src_image = context.active_node.image
            img_path = src_image.filepath_raw
            if img_path.startswith("//"):
                if not bpy.data.is_saved:
                    # if not context.scene.ImageChannelSplitter.is_custom_save_path:
                    msg = 'To process an image with relative path, ' \
                          'you should save the blend file first.'
                    self.report({'WARNING'}, msg)
                    return {'FINISHED'}

                img_path = bpy.path.abspath(img_path)

                # blend_file_path = bpy.data.filepath
                # directory = os.path.dirname(blend_file_path)
                # img_path = os.path.normpath(os.path.join(directory, img_path))

            if not os.path.exists(img_path):
                msg = 'Could not find file: {}'.format(img_path)
                self.report({'WARNING'}, msg)
                return {'FINISHED'}

            create_and_save_single_channel_images_with_pil(context, img_path)
        else:
            create_single_channel_images_with_blender(context)
        # create_single_channel_images_with_blender(context)

        # return {'RUNNING_MODAL'}
        return {'FINISHED'}

        # ------------------------------------------------------------------------


# PANEL
########################################################################
class ImageChannelSplitterPanel(Panel):
    # bl_idname = "ImageChannelSplitterPanel"
    # bl_idname = "NODE_PT_image_channel_splitter_panel"
    bl_label = "Channel Splitter"
    bl_category = "Channel Splitter"
    # bl_category = "ICS"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'TOOLS'
    # bl_context = "scene"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        icsplitter = scene.ImageChannelSplitter

        # draw_alpha = False

        box = layout.box()
        row = box.row()

        # if context.active_node and context.active_node.bl_idname in ["ShaderNodeTexEnvironment", "ShaderNodeTexImage"]:
        if context.active_node \
                and hasattr(context.active_node, 'image') \
                and hasattr(context.active_node.image, "filepath_raw"):
            # if is_pil_imported:
            #     img = Image.open(context.active_node.image.filepath_raw, 'r')
            #     if img.mode == "RGBA":
            #         draw_alpha = True
            #     img.close()


            row.label(text='Select Channels', icon='IMAGE_RGB')

            # col = layout.column()
            # col.label(text="test")
            # col.prop(icsplitter, "primitive")

            row = box.row()
            row.prop(icsplitter, "is_red_channel", text="Red Channel", icon="COLOR_RED")
            row = box.row()
            row.prop(icsplitter, "is_green_channel", text="Green Channel", icon="COLOR_GREEN")
            row = box.row()
            row.prop(icsplitter, "is_blue_channel", text="Blue Channel", icon="COLOR_BLUE")

            # if draw_alpha:
            row = box.row()
            row.prop(icsplitter, "is_alpha_channel", text="Alpha Channel", icon="IMAGE_ALPHA")

            row = box.row()
            row.prop(icsplitter, "is_average", text="Average", icon="SEQ_SPLITVIEW")
            row = box.row()
            row.prop(icsplitter, "is_weighted_average", text="Weighted Average", icon="SEQ_LUMA_WAVEFORM")
            # layout.separator()
            box = layout.box()
            row = box.row()
            row.label(text='Options', icon='SCRIPTWIN')
            row = box.row()
            row.prop(icsplitter, "is_create_texture_node", text="Create Texture Node")

            row = box.row()
            row.prop(icsplitter, "is_unlink", text="Unlink After Save")
            row = box.row()
            # rowCustomPath.prop(icsplitter, "is_custom_save_path", text="")
            # icsplitter.custom_save_path = context.active_node.image.filepath
            row.prop(icsplitter, "is_custom_save_path", text="Custom Save Directory")
            if icsplitter.is_custom_save_path:
                row = box.row()
                row.prop(icsplitter, "custom_save_path")
            row = box.row()
            row.prop(icsplitter, "image_format_menu")
            row = box.row()

            # TODO: pil png p mode, 16 bit support says experimental. tiff has problems
            # https://stackoverflow.com/questions/7247371/python-and-16-bit-tiff
            if not is_pil_imported and icsplitter.image_format_menu in ["PNG", "TIFF"]:
                row.prop(icsplitter, "depth_menu", expand=True)

            row = box.row()
            row.operator("ics.split_button", text="Split And Save", icon="RENDER_STILL")
            # row = box.row()
            # row.prop(icsplitter, "progress")

        else:
            row.label(text='Please select an image node with a loaded image', icon='IMAGE_RGB')


# ------------------------------------------------------------------------
# register and unregister functions
# ------------------------------------------------------------------------

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.ImageChannelSplitter = PointerProperty(type=ICSPanelSettings)


def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.ImageChannelSplitter


if __name__ == "__main__":
    register()
