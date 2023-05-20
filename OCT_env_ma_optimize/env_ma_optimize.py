import os
import subprocess


mayabatch = r'"C:\Program Files\Autodesk\Maya2018\bin\mayabatch.exe" -noAutoloadPlugins -file '
envMa = r'D:\\BarHeadedGooseHimalayas.BDL.ma'
loctrl = 'BarHeadedGooseHimalayas:loc_ctrl'
seqpath = r'J:\OCT\show\OCT_0815'
dir_list = os.listdir(seqpath)


def check_xform_expcam(ANIma, camabc, loctrl):
    envRN = 'BarHeadedGooseHimalayas'
    expcam = (
        r'$s = `playbackOptions -q -ast`;$e = `playbackOptions -q -aet`;print StartFrame_;'
        r'print $s;print _EndFrame_;print $e;print \"\n\";'
        r'$cmd = \"-fr \"+$s+\" \"+$e+\" -ws -ef -df ogawa -rt ^|cgCamera^|globalCtrl^|globalAimPosCtrl^|globalAimPos_bake^|offset^|camAim^|camRenderConst^|camShake^|camRender -file {}\";'
        r'loadPlugin AbcExport;AbcExport -j $cmd;'
    ).format(
        camabc)
    checkxform = r'file -lr \"{}\" \"{}\";print 487;getAttr {}.translate;'.format(
        envRN, envMa, loctrl)
    prepcmd = mayabatch+ANIma+' -command "{}{}"'.format(expcam, checkxform)
    coord = []
    output = subprocess.Popen(
        prepcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
    for line in iter(output.stdout.readline, ""):
        print(line)
        if line.startswith('StartFrame_'):
            startF = line.split('_')[1]
            endF = line.split('_')[3][:-2]
        if line.startswith('487'):
            coord = line.split(': ')[1].split(' ')
            coord[2] = coord[2][:-1]
    return coord, startF, endF


def camfrustrum(envMa, camabc, fixedEnvMa, coord, startF, endF, loctrl):
    loctrl = loctrl.split(':')[1]
    xlate = r'setAttr \"{loctrl}.translate\" {x} {y} {z};setKeyframe \"{loctrl}\";'.format(
        loctrl=loctrl, x=coord[0], y=coord[1], z=coord[2])
    setfr = r'playbackOptions -ast {sf} -aet {ef} -min {sf} -max {ef};'.format(
        sf=startF, ef=endF)
    camclip = r'loadPlugin AbcImport;AbcImport -m import \"{}\";python(\"execfile(r\'D:\\\\camfrustum.py\')\");'.format(
        camabc)
    save = r'cleanUpScene(3);file -rn \"{f}\";file -s;'.format(f=fixedEnvMa)
    batchcmd = mayabatch + \
        r'{} -command "{}{}{}{}'.format(envMa, xlate, setfr, camclip, save)
    output = subprocess.Popen(
        batchcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)


def main():
    for shot in dir_list:
        ignore = os.path.join(seqpath, shot, 'ignoreme.txt')
        if os.path.exists(ignore):
            print (shot+' ignore')
            continue
        LGTpath = os.path.join(seqpath, shot, 'lighting')
        ANIma = os.path.join(LGTpath, 'ready', shot+'_ANI_OK.ma')
        envfname = os.path.basename(envMa)
        fixedEnvMa = os.path.join(
            LGTpath, 'ready', envfname).replace('\\', '/')
        if os.path.exists(fixedEnvMa):
            print (shot + ' env already fixed')
            continue
        if not os.path.exists(ANIma):
            print (shot+' missing ani')
            continue
        ready = os.path.dirname(ANIma)
        camabc = os.path.join(ready, 'cam.abc').replace('\\', '/')
        coord, startF, endF = check_xform_expcam(ANIma, camabc, loctrl)
        camfrustrum(envMa, camabc, fixedEnvMa, coord, startF, endF, loctrl)
        print (shot + ' fixing success')


main()
