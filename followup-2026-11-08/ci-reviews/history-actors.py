#!/usr/bin/env python3
"""Dispatch and reconcile fixed actor-comment effects without blind write retries."""
import datetime,json,pathlib,time
import lab
STATE=lab.HERE/'history-state.json';BRANCH='exp/fu2/ci/history-control/workflow'
MARKER='<!-- gherrit-history:v1 artifact=fu2-history-actors-2026-11-08 -->'
def load():return json.loads(STATE.read_text()) if STATE.exists() else {'pr':lab.load()['history-actors']['lower_pr'],'marker':MARKER,'jobs':{}}
def save(s):lab.write(STATE,s)
def dispatch(key,operation,body,comment_id=None,mode='write',start_at=None):
 s=load();assert key not in s['jobs'],'Reconcile the recorded job, do not repeat its dispatch'
 inputs={'operation':operation,'permission_mode':mode,'number':str(s['pr']),'body':body}
 if comment_id:inputs['comment_id']=str(comment_id)
 if start_at:inputs['start_at']=str(start_at)
 request={'ref':BRANCH,'inputs':inputs};s['jobs'][key]={'intent_at':lab.now(),'request':request,'phase':'intent'};save(s)
 lab.api('history-'+key+'-dispatch',lab.R+'/actions/workflows/automation.yml/dispatches','POST',request);s['jobs'][key]['phase']='acknowledged';save(s)
 return s['jobs'][key]
def collect():
 import urllib.parse
 runs=lab.api('history-actor-runs',lab.R+'/actions/runs?branch='+urllib.parse.quote(BRANCH,safe='')+'&per_page=100')['workflow_runs'];out=[]
 for r in runs:
  if r['name']!='history-actors':continue
  lab.api('history-run-'+str(r['id']),lab.R+'/actions/runs/'+str(r['id']))
  out.append({k:r[k] for k in ['id','status','conclusion','created_at','head_sha','head_branch']})
  if r['status']=='completed':
   dest=lab.EV/'history-actions'/str(r['id'])
   if not dest.exists():lab.run('history-download-'+str(r['id']),['gh','run','download',str(r['id']),'--repo',lab.REPO,'--dir',str(dest)],ok=(0,1))
 lab.write(lab.EV/'history-actor-runs.json',out);return out
if __name__=='__main__':
 import sys
 if sys.argv[1]=='create':dispatch('create','create',MARKER+'\nGenerated synthetic history owned by this bot identity.\n\n'+lab.NOTICE)
 elif sys.argv[1]=='collect':print(json.dumps(collect(),indent=2))
