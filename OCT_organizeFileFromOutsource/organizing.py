import os
import glob
import shutil
import os.path as op


layPath = r'J:\2203_OCT\2_Production\1_Lay\EP810'
# 'J:\2203_OCT\2_Production\1_Lay\EP810\*v02.ma'
maPath = op.join(layPath, 'OCT_0810*LAY_v*.ma')
lgtRoot = r'J:\OCT\show\OCT_0810\wx'  # target folder


def version_check(newFolder_path):
    current_ver_file = glob.glob(op.join(newFolder_path, 'currentVer_*.txt'))
    if len(current_ver_file) == 1:
        current_ver_path = current_ver_file[0]
        current_ver_file = op.basename(current_ver_path)
        current_ver_dir = op.dirname(current_ver_path)
        current_ver = current_ver_file.split('_')[1].split('.')[0]
        if int(shot_full_ver) > int(current_ver):
            new_ver_file = current_ver_file.replace(current_ver, shot_full_ver)
            new_ver_path = op.join(current_ver_dir, new_ver_file)
            os.rename(current_ver_path, new_ver_path)
            return True
        else:
            return False
    else:
        shot_ver_path = op.join(
            newFolder_path, 'currentVer_' + shot_full_ver + '.txt')
        with open(shot_ver_path, 'w') as f:
            pass
        return True


def move():
    for shot_path in glob.glob(maPath):
        shot_fname = op.basename(shot_path)  # OCT_0810_s010_020_LAY_v02.ma
        shot_dir = op.dirname(shot_path)
        shot_fname_split_list = shot_fname.split(
            '_LAY')  # 'OCT_0810_s010_010' '_v01.ma'
        shot_code = shot_fname_split_list[0]
        newFolder_path = op.join(lgtRoot, shot_code)
        if op.exists(newFolder_path) == False:
            os.mkdir(newFolder_path)
        shot_ver = shot_fname_split_list[1]
        shot_ver_2nd_digit = int(shot_ver[2])
        shot_ver_1st_digit = int(shot_ver[3])
        shot_full_ver = shot_ver[2] + shot_ver[3]
        OK_path = op.join(newFolder_path, 'ready', shot_code+'_LAY_OK.ma')
        if version_check(newFolder_path) == True:
            shutil.copy(shot_path, OK_path)
