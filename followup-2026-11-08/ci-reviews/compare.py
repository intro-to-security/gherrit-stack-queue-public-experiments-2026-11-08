#!/usr/bin/env python3
import hashlib,json,sys
import lab

def compare(key,before='before-merge',after='after-merge'):
    a=json.loads((lab.EV/('snapshot-'+key+'-'+before+'.json')).read_text());b=json.loads((lab.EV/('snapshot-'+key+'-'+after+'.json')).read_text())
    c=lab.load()[key];lab.git(key+'-compare-fetch','fetch','origin',c['trunk'],c['lower'],c['upper'])
    out={'at':lab.now(),'before':before,'after':after,'layers':{}}
    for pos in ['lower','upper']:
        old,new=a[pos]['head']['sha'],b[pos]['head']['sha'];ob,nb=a[pos]['base']['sha'],b[pos]['base']['sha']
        oldcommits=a[pos+'_commits'];newcommits=b[pos+'_commits'];comparisons=[]
        for i,(x,y) in enumerate(zip(oldcommits,newcommits)):
            xc=lab.api(key+'-old-'+pos+'-'+str(i),lab.R+'/git/commits/'+x['sha']);yc=lab.api(key+'-new-'+pos+'-'+str(i),lab.R+'/git/commits/'+y['sha'])
            xp=lab.git(key+'-old-patch-'+pos+'-'+str(i),'diff','--binary',xc['parents'][0]['sha'],x['sha']);yp=lab.git(key+'-new-patch-'+pos+'-'+str(i),'diff','--binary',yc['parents'][0]['sha'],y['sha'])
            comparisons.append({'old':x['sha'],'new':y['sha'],'old_verified':xc['verification']['verified'],'new_verified':yc['verification']['verified'],'old_reason':xc['verification']['reason'],'new_reason':yc['verification']['reason'],'author_equal':xc['author']==yc['author'],'message_equal':xc['message']==yc['message'],'tree_equal':xc['tree']['sha']==yc['tree']['sha'],'patch_equal':xp==yp,'old_committer':xc['committer'],'new_committer':yc['committer'],'signature_bytes_equal':xc['verification'].get('signature')==yc['verification'].get('signature')})
        xp=lab.git(key+'-old-group-'+pos,'diff','--binary',ob,old);yp=lab.git(key+'-new-group-'+pos,'diff','--binary',nb,new)
        out['layers'][pos]={'old':old,'new':new,'old_base':ob,'new_base':nb,'old_count':len(oldcommits),'new_count':len(newcommits),'group_patch_equal':xp==yp,'old_patch_sha256':hashlib.sha256(xp.encode()).hexdigest(),'new_patch_sha256':hashlib.sha256(yp.encode()).hexdigest(),'commits':comparisons}
    lab.write(lab.EV/(key+'-comparison.json'),out);return out
if __name__=='__main__':print(json.dumps(compare(*sys.argv[1:]),indent=2))
