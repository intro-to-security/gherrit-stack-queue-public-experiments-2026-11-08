#!/usr/bin/env python3
"""Prepare reserved UI fixtures only after root enables the bot permission."""
import json,sys
import lab
KEYS=['ui-stale','ui-lastpush','ui-codeowner','ui-signed']
if __name__=='__main__':
    command=sys.argv[1]
    if command=='dispatch':
        flag=lab.api('ui-bot-flag-preflight',lab.R+'/actions/permissions/workflow')
        if not flag['can_approve_pull_request_reviews']:raise SystemExit('Root bot permission has not been enabled; no dispatch sent.')
        for key in KEYS:
            s=lab.load();c=s[key]
            for pos,base in [('lower','trunk'),('upper','lower')]:
                dispatches=c.setdefault('bot_dispatches',{})
                if pos in dispatches:raise SystemExit('Recorded dispatch exists; reconcile '+key+' '+pos)
                body={'ref':'exp/fu2/ci/control/workflow','inputs':{'operation':'create-pr','head':c[pos],'base':c[base],'title':'Follow-up review '+key+': '+pos,'body':'Reserved synthetic distinct-author website-rebase fixture.\n\n'+lab.NOTICE}}
                dispatches[pos]={'at':lab.now(),'phase':'intent','request':body};lab.save(s)
                lab.api(key+'-'+pos+'-bot-create-dispatch',lab.R+'/actions/workflows/automation.yml/dispatches','POST',body)
                dispatches[pos]['phase']='acknowledged';lab.save(s)
                print(key,pos,'acknowledged',flush=True)
    elif command=='prepare':
        for key in KEYS:
            c=lab.discover(key)
            if c.get('ui_prepared'):raise SystemExit('Reserved UI fixture already prepared: '+key)
            lab.register(key)
            if key!='ui-signed':lab.approve(key)
            lab.snapshot(key,'approved')
            lab.advance(key)
            # The unrelated trunk commit is explicitly made before admin enforcement.
            ep=lab.R+'/branches/'+lab.urllib.parse.quote(c['trunk'],safe='')+'/protection/enforce_admins'
            lab.api(key+'-enforce-admins',ep,'POST');lab.api(key+'-enforce-admins-readback',ep)
            print(key,json.dumps(lab.snapshot(key,'ready-ui')),flush=True)
            s=lab.load();s[key]['ui_prepared']=True;lab.save(s)
    elif command=='after':
        import compare
        for key in KEYS:
            print(key,json.dumps(lab.snapshot(key,'after-ui')),flush=True)
            compare.compare(key,'approved','after-ui')
    else:raise SystemExit('Unknown phase')
