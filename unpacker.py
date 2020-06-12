#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from PIL import Image
from xml.etree import ElementTree
import json
import plistlib


def tree_to_dict(tree):
    d = {}
    for index, item in enumerate(tree):
        if item.tag == 'key':
            if tree[index + 1].tag == 'string':
                d[item.text] = tree[index + 1].text
            elif tree[index + 1].tag == 'true':
                d[item.text] = True
            elif tree[index + 1].tag == 'false':
                d[item.text] = False
            elif tree[index + 1].tag == 'integer':
                d[item.text] = int(tree[index + 1].text)
            elif tree[index + 1].tag == 'dict':
                d[item.text] = tree_to_dict(tree[index + 1])
    return d


def frames_from_data(filename, format):
    if format == 'plist':
        data_filename = filename + '.plist'
        root = ElementTree.fromstring(open(data_filename, 'r').read())
        plist_dict = tree_to_dict(root[0])
        to_list = lambda x: x.replace('{', '').replace('}', '').split(',')
        frames = plist_dict['frames'].items()
        for k, v in frames:
            frame = v
            rectlist = to_list(frame['frame'])
            width = int(rectlist[3] if frame['rotated'] else rectlist[2])
            height = int(rectlist[2] if frame['rotated'] else rectlist[3])
            frame['box'] = (
                int(rectlist[0]),
                int(rectlist[1]),
                int(rectlist[0]) + width,
                int(rectlist[1]) + height
            )
            real_rectlist = to_list(frame['sourceSize'])
            real_width = int(real_rectlist[1] if frame['rotated'] else real_rectlist[0])
            real_height = int(real_rectlist[0] if frame['rotated'] else real_rectlist[1])
            real_sizelist = [real_width, real_height]
            frame['real_sizelist'] = real_sizelist
            offsetlist = to_list(frame['offset'])
            offset_x = int(offsetlist[1] if frame['rotated'] else offsetlist[0])
            offset_y = int(offsetlist[0] if frame['rotated'] else offsetlist[1])
            frame['result_box'] = (
                int((real_sizelist[0] - width) / 2 + offset_x),
                int((real_sizelist[1] - height) / 2 + offset_y),
                int((real_sizelist[0] + width) / 2 + offset_x),
                int((real_sizelist[1] + height) / 2 + offset_y)
            )
        return frames

    elif format == 'json':
        data_filename = filename + '.json'
        json_data = open(data_filename)
        data = json.load(json_data)
        frames = {}
        for f in data['frames']:
            x = int(f["frame"]["x"])
            y = int(f["frame"]["y"])
            w = int(f["frame"]["h"] if f['rotated'] else f["frame"]["w"])
            h = int(f["frame"]["w"] if f['rotated'] else f["frame"]["h"])
            real_w = int(f["sourceSize"]["h"] if f['rotated'] else f["sourceSize"]["w"])
            real_h = int(f["sourceSize"]["w"] if f['rotated'] else f["sourceSize"]["h"])
            d = {
                'box': (
                    x,
                    y,
                    x + w,
                    y + h
                ),
                'real_sizelist': [
                    real_w,
                    real_h
                ],
                'result_box': (
                    int((real_w - w) / 2),
                    int((real_h - h) / 2),
                    int((real_w + w) / 2),
                    int((real_h + h) / 2)
                ),
                'rotated': f['rotated']
            }
            frames[f["filename"]] = d
        json_data.close()
        return frames.items()
    elif format == 'cocos':
        data_filename = filename + ".plist"
        pl = plistlib.readPlist(data_filename)
        data = pl['frames'].items()
        frames = {}
        for k, f in data:
            x = int(f["x"])
            y = int(f["y"])
            w = int(f["width"])
            h = int(f["height"])
            real_w = int(f["originalWidth"])
            real_h = int(f["originalHeight"])
            d = {
                'box': (
                    x,
                    y,
                    x + w,
                    y + h
                ),
                'real_sizelist': [
                    real_w,
                    real_h
                ],
                'result_box': (
                    int((real_w - w) / 2),
                    int((real_h - h) / 2),
                    int((real_w + w) / 2),
                    int((real_h + h) / 2)
                ),
                'rotated': False
            }
            frames[k] = d
        return frames.items()
    elif format == 'plist1':
        data_filename = filename + '.plist'
        root = ElementTree.fromstring(open(data_filename, 'r').read())
        plist_dict = tree_to_dict(root[0])
        to_list = lambda x: x.replace('{', '').replace('}', '').split(',')
        frames = plist_dict['frames'].items()
        for k, v in frames:
            frame = v
            frame['rotated'] = frame['textureRotated']
            rectlist = to_list(frame['textureRect'])
            width = int(rectlist[3] if frame['textureRotated'] else rectlist[2])
            height = int(rectlist[2] if frame['textureRotated'] else rectlist[3])
            frame['box'] = (
                int(rectlist[0]),
                int(rectlist[1]),
                int(rectlist[0]) + width,
                int(rectlist[1]) + height
            )
            real_rectlist = to_list(frame['spriteSourceSize'])
            real_width = int(real_rectlist[1] if frame['textureRotated'] else real_rectlist[0])
            real_height = int(real_rectlist[0] if frame['textureRotated'] else real_rectlist[1])
            real_sizelist = [real_width, real_height]
            frame['real_sizelist'] = real_sizelist
            offsetlist = to_list(frame['spriteOffset'])
            offset_x = int(offsetlist[1] if frame['textureRotated'] else offsetlist[0])
            offset_y = int(offsetlist[0] if frame['textureRotated'] else offsetlist[1])
            frame['result_box'] = (
                int((real_sizelist[0] - width) / 2 + offset_x),
                int((real_sizelist[1] - height) / 2 + offset_y),
                int((real_sizelist[0] + width) / 2 + offset_x),
                int((real_sizelist[1] + height) / 2 + offset_y)
            )
        return frames
    elif format == 'plist2':
        data_filename = filename + '.plist'
        root = ElementTree.fromstring(open(data_filename, 'r').read())
        plist_dict = tree_to_dict(root[0])
        to_list = lambda x: x.replace('{', '').replace('}', '').split(',')
        frames = plist_dict['frames'].items()
        for k, v in frames:
            frame = v
            rectlist = to_list(frame['frame'])
            # print(k)
            if not frame['rotated']:

                width = int(rectlist[2])
                height = int(rectlist[3])
                frame['box'] = (
                    int(rectlist[0]),
                    int(rectlist[1]),
                    int(rectlist[0]) + width,
                    int(rectlist[1]) + height
                )
                real_rectlist = to_list(frame['sourceSize'])
                real_width = int(real_rectlist[0])
                real_height = int(real_rectlist[1])
                real_sizelist = [real_width, real_height]
                frame['real_sizelist'] = real_sizelist
                offsetlist = to_list(frame['offset'])
                offset_x = int(offsetlist[0])
                offset_y = int(offsetlist[1])
                frame['result_box'] = (
                    int((real_sizelist[0] - width) / 2 + offset_x),
                    int((real_sizelist[1] - height) / 2 + offset_y),
                    int((real_sizelist[0] + width) / 2 + offset_x),
                    int((real_sizelist[1] + height) / 2 + offset_y)
                )

            else:

                width = int(rectlist[2])
                height = int(rectlist[3])
                frame['box'] = (
                    int(rectlist[0]),
                    int(rectlist[1]),
                    int(rectlist[0]) + height,
                    int(rectlist[1]) + width
                )
                real_rectlist = to_list(frame['sourceSize'])
                real_width = int(real_rectlist[0])
                real_height = int(real_rectlist[1])
                real_sizelist = [real_width, real_height]
                frame['real_sizelist'] = real_sizelist
                offsetlist = to_list(frame['offset'])
                offset_x = int(offsetlist[0])
                offset_y = int(offsetlist[1])
                frame['result_box'] = (
                    int((real_sizelist[0] - width) / 2 + offset_x),
                    int((real_sizelist[1] - height) / 2 - offset_y),
                    int((real_sizelist[0] + width) / 2 + offset_x),
                    int((real_sizelist[1] + height) / 2 - offset_y)
                )
                # print(frame)

        return frames
    
    elif format == 'plist3':
        data_filename = filename + '.plist'
        root = ElementTree.fromstring(open(data_filename, 'r').read())
        plist_dict = tree_to_dict(root[0])
        to_list = lambda x: x.replace('{', '').replace('}', '').split(',')
        frames = plist_dict['frames'].items()
        for k, v in frames:
            frame = v
            rectlist = to_list(frame['textureRect'])
            frame['rotated'] = frame['textureRotated']
            # print(k)
            if not frame['textureRotated']:

                width = int(rectlist[2])
                height = int(rectlist[3])
                frame['box'] = (
                    int(rectlist[0]),
                    int(rectlist[1]),
                    int(rectlist[0]) + width,
                    int(rectlist[1]) + height
                )
                real_rectlist = to_list(frame['spriteSourceSize'])
                real_width = int(real_rectlist[0])
                real_height = int(real_rectlist[1])
                real_sizelist = [real_width, real_height]
                frame['real_sizelist'] = real_sizelist
                offsetlist = to_list(frame['spriteOffset'])
                offset_x = int(offsetlist[0])
                offset_y = int(offsetlist[1])
                frame['result_box'] = (
                    int((real_sizelist[0] - width) / 2 + offset_x),
                    int((real_sizelist[1] - height) / 2 + offset_y),
                    int((real_sizelist[0] + width) / 2 + offset_x),
                    int((real_sizelist[1] + height) / 2 + offset_y)
                )

            else:

                width = int(rectlist[2])
                height = int(rectlist[3])
                frame['box'] = (
                    int(rectlist[0]),
                    int(rectlist[1]),
                    int(rectlist[0]) + height,
                    int(rectlist[1]) + width
                )
                real_rectlist = to_list(frame['spriteSourceSize'])
                real_width = int(real_rectlist[0])
                real_height = int(real_rectlist[1])
                real_sizelist = [real_width, real_height]
                frame['real_sizelist'] = real_sizelist
                offsetlist = to_list(frame['spriteOffset'])
                offset_x = int(offsetlist[0])
                offset_y = int(offsetlist[1])
                frame['result_box'] = (
                    int((real_sizelist[0] - width) / 2 + offset_x),
                    int((real_sizelist[1] - height) / 2 - offset_y),
                    int((real_sizelist[0] + width) / 2 + offset_x),
                    int((real_sizelist[1] + height) / 2 - offset_y)
                )
                print(frame)

        return frames
    else:
        print("Wrong data format on parsing: '" + format + "'!")
        exit(1)


def gen_png_from_data(filename, format):
    big_image = Image.open(filename + ".png")
    frames = frames_from_data(filename, format)
    for k, v in frames:
        if not (format == 'plist2' or format == 'plist3'):
            try:
                frame = v
                box = frame['box']
                rect_on_big = big_image.crop(box)
                real_sizelist = frame['real_sizelist']
                result_image = Image.new('RGBA', real_sizelist, (0, 0, 0, 0))
                result_box = frame['result_box']
                result_image.paste(rect_on_big, result_box, mask=0)
                if frame['rotated']:
                    result_image = result_image.rotate(90)
                outfile = (filename + '/' + k).replace('gift_', '')
                dirname = os.path.dirname(outfile)
                if not os.path.isdir(dirname):
                    os.makedirs(dirname)
                print(outfile, "generated")
                result_image.save(outfile)
            except Exception as e:
                print(k)
                print(e)
        else:
            try:
                frame = v
                box = frame['box']
                rect_on_big = big_image.crop(box)

                # res_file = (filename + '/' + k).replace('.png', '_r.png')
                # rect_on_big.save(res_file)

                real_sizelist = frame['real_sizelist']
                result_image = Image.new('RGBA', real_sizelist, (0, 0, 0, 0))
                result_box = frame['result_box']
                if frame['rotated']:
                    rect_on_big = rect_on_big.rotate(90, expand = True)
                    result_image.paste(rect_on_big, result_box, mask = 0)
                else:
                    result_image.paste(rect_on_big, result_box, mask = 0)

                # if frame['rotated']:
                #     result_image = result_image.rotate(90)
                outfile = (filename + '/' + k).replace('gift_', '')
                dirname = os.path.dirname(outfile)
                if not os.path.isdir(dirname):
                    os.makedirs(dirname)
                print(outfile, "generated")
                
                result_image.save(outfile)
            except Exception as e:
                print(k)
                print(e)



def endWith(s,*endstring):
    array = map(s.endswith,endstring)
    if True in array:
        return True
    else:
        return False

# Get the all files & directories in the specified directory (path).
def get_recursive_file_list(path):
    current_files = os.listdir(path)
    all_files = []
    for file_name in current_files:
        full_file_name = os.path.join(path, file_name)
        all_files.append(full_file_name)
        
        if os.path.isdir(full_file_name):
            next_level_files = get_recursive_file_list(full_file_name)
            all_files.extend(next_level_files)
            
    return all_files

# Get the all files & directories in the specified directory (path).   
def get_file_list(path):
    current_files = os.listdir(path)
    all_files = []  
    for file_name in current_files:
        full_file_name = os.path.join(path, file_name)
        if endWith(full_file_name,'.plist'):
            full_file_name = full_file_name.replace('.plist','')
            all_files.append(full_file_name)
        if endWith(full_file_name,'.json'):
            full_file_name = full_file_name.replace('.json','')
            all_files.append(full_file_name)
        if os.path.isdir(full_file_name):
            next_level_files =  get_recursive_file_list(full_file_name)
            all_files.extend(next_level_files)
    return all_files


def get_sources_file(filename, format, ext):
    data_filename = filename + ext
    png_filename = filename + '.png'
    if os.path.exists(data_filename) and os.path.exists(png_filename):
        gen_png_from_data(filename, format)
    else:
        print("Make sure you have both " + data_filename + " and " + png_filename + " files in the same directory")


def main():
    if len(sys.argv) <= 1:
        print("You must pass filename [plist or cocos or plist1 or plist2] as parameter!")
        exit(1)
    
    print(sys.argv)
    path_or_name = sys.argv[1]
    ext = '.plist'
    if len(sys.argv) < 3:
        print("No data format passed, assuming .plist")
    elif sys.argv[2] == 'plist' or sys.argv[2] == 'cocos' or sys.argv[2] == 'plist1' or sys.argv[2] == 'plist2' or sys.argv[2] == 'plist3':
        print(str(sys.argv[2]) + " data format passed")
    elif sys.argv[2] == 'json':
        ext = '.json'
        print(".json data format passed")
    else:
        print("Wrong data format passed '" + sys.argv[2] + "'!")
        exit(1)
        
    # supports multiple file conversions
    if os.path.isdir(path_or_name):
        files = get_file_list(path_or_name)
        for file0 in files:
            get_sources_file(file0, sys.argv[2], ext)
    else:
        get_sources_file(path_or_name, sys.argv[2], ext)


# Use like this: python unpacker.py [Image Path or Image Name(but no suffix)] [Type:plist or json]
if __name__ == '__main__':
    main()