import af


def submit():    
    
    input_rops = [i[0] for i in hou.pwd().inputDependencies()]
    rop_list=[]
    job_ids=[]
    cmd = af.Cmd()
    
    for rop in input_rops:

        rop.parm('af_offline_job').set(1)
        rop.parm('af_ubmit').pressButton()
        rop.parm('af_job_info_pretty').eval()
        rop_list.append(rop.evalParm('af_job_info_pretty'))
        rop.parm('af_offline_job').set(0)

    for i in range(len(rop_list)):

        cmd.data['mask'] = rop_list[i]
        job = cmd.getJobList()
        id = job[0]['id']
        job_ids.append(id)

        if i >0:
            cmd.action = 'action'
            cmd.data['type'] = 'jobs'
            cmd.data['mask'] = rop_list[i]
            cmd.data['params'] = {'depend_mask': rop_list[i-1]}
            cmd._sendRequest()
            
    job_ids.reverse()
    for id in job_ids:
        cmd.setJobState(id, 'start')
        
        
    
