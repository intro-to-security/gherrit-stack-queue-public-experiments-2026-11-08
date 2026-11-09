"""Read back all owned fixture queues and unchanged repository feature defaults."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from lab import Lane,REPO,save,now
L=Lane('control')
paths=['native/fixtures.json','ci/fixtures.json','locks/fixtures.json','edit/fixtures.json','edit/pending-cancel/fixtures.json']
cases=[]
for relative in paths:
 path=ROOT/relative
 if path.exists():
  for c in json.loads(path.read_text()).values():
   if isinstance(c,dict)and'trunk'in c:cases.append((relative,c))
assert cases
variables={'owner':'intro-to-security','repo':REPO.split('/')[1]};decl=['$owner:String!','$repo:String!'];fields=[]
for i,(path,c)in enumerate(cases):
 key='b'+str(i);variables[key]=c['trunk'];decl.append('$'+key+':String!');fields.append('q'+str(i)+':mergeQueue(branch:$'+key+'){id entries(first:100){nodes{id state pullRequest{number}} pageInfo{hasNextPage}}}')
query='query('+','.join(decl)+'){repository(owner:$owner,name:$repo){'+' '.join(fields)+'}}'
r=L.graphql('final-owned-queues',query,variables,fresh=True);assert r['http']==200 and not r['data'].get('errors'),r
values=r['data']['data']['repository'];results=[]
for i,(path,c)in enumerate(cases):
 q=values['q'+str(i)];entries=(q or{}).get('entries',{});assert not entries.get('pageInfo',{}).get('hasNextPage');nodes=entries.get('nodes',[]);results.append({'source':path,'name':c['name'],'trunk':c['trunk'],'prs':c['prs'],'queue_entries':nodes});assert nodes==[],results[-1]
repo=L.api('final-repository','GET','repos/'+REPO,fresh=True);assert repo['http']==200;rd=repo['data'];assert rd['id']==1450803505 and rd['private']is False and rd['permissions']['admin'];assert rd['allow_auto_merge']==json.loads((ROOT/'repository-created.json').read_text())['allow_auto_merge']
a=L.api('final-actions-permissions','GET',f'repos/{REPO}/actions/permissions',fresh=True);w=L.api('final-workflow-permissions','GET',f'repos/{REPO}/actions/permissions/workflow',fresh=True);assert a['http']==200 and w['http']==200;assert a['data']['enabled'] is True;assert w['data']=={'default_workflow_permissions':'read','can_approve_pull_request_reviews':False}
save(ROOT/'FINAL-VERIFICATION.json',{'at':now(),'repository':REPO,'public':True,'repo_admin':True,'allow_auto_merge':rd['allow_auto_merge'],'actions_permissions':a['data'],'workflow_permissions':w['data'],'fixture_queues':results,'all_observed_fixture_queues_empty':True,'organization_wide_changes':False,'private_material_published':False,'limits':'Current owned-resource observations, not absence of all possible later provider effects.'});print('Verified',len(results),'owned fixture queues empty; public visibility and read-only token defaults unchanged.')
