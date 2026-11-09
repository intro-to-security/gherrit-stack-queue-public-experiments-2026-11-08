import gzip
import hashlib
import json
from pathlib import Path
import struct
import zlib

OUT = Path(__file__).resolve().parent
PACKAGE = OUT.parent.parent
EVIDENCE = PACKAGE / "actual-results-001"


def serial(name):
    result = {}
    for line in (EVIDENCE/name).read_text().splitlines():
        if line.startswith("PROTOCOL {"):
            item = json.loads(line[len("PROTOCOL "):])
            if item["kind"] in result:
                raise ValueError("duplicate_serial_kind")
            result[item["kind"]] = item["value"]
    return result


def document(snapshot, name):
    item = snapshot["files"][name]
    data = bytes.fromhex(item["hex"])
    assert len(data) == item["bytes"] and hashlib.sha256(data).hexdigest() == item["sha256"]
    return json.loads(data)


def objects(repo):
    result = {}
    for item in repo["objects"]:
        data = bytes.fromhex(item["read"]["stdout_hex"])
        assert item["read"]["exit"] == 0 and len(data) == item["size"]
        encoded = item["type"].encode()+b" "+str(len(data)).encode()+b"\0"+data
        assert hashlib.sha1(encoded).hexdigest() == item["oid"]
        result[item["oid"]] = dict(type=item["type"], body_sha256=hashlib.sha256(data).hexdigest(), encoded=encoded)
    return result


class Ext4:
    def __init__(self, data):
        self.data = data
        sb = data[1024:2048]
        assert struct.unpack_from("<H",sb,56)[0] == 0xEF53
        self.block = 1024 << struct.unpack_from("<I",sb,24)[0]
        self.per_group = struct.unpack_from("<I",sb,40)[0]
        self.inode_size = struct.unpack_from("<H",sb,88)[0]
        self.incompat = struct.unpack_from("<I",sb,96)[0]
        self.desc_size = max(32,struct.unpack_from("<H",sb,254)[0]) if self.incompat & 0x80 else 32
        assert self.block == 4096 and self.inode_size in (128,256) and self.desc_size in (32,64)
        assert len(data) == 33554432

    def inode(self, number):
        group,index = divmod(number-1,self.per_group)
        descriptor = self.block+group*self.desc_size
        table = struct.unpack_from("<I",self.data,descriptor+8)[0]
        if self.desc_size >= 64:
            table += struct.unpack_from("<I",self.data,descriptor+40)[0]<<32
        offset = table*self.block+index*self.inode_size
        raw = self.data[offset:offset+self.inode_size]
        mode = struct.unpack_from("<H",raw,0)[0]
        size = struct.unpack_from("<I",raw,4)[0] + (struct.unpack_from("<I",raw,108)[0]<<32)
        flags = struct.unpack_from("<I",raw,32)[0]
        return dict(number=number,offset=offset,mode=mode,size=size,flags=flags,raw=raw)

    def extents(self, block, expected_depth=None):
        magic,entries,maximum,depth = struct.unpack_from("<HHHH",block,0)
        assert magic == 0xF30A and entries <= maximum and depth <= 2
        if expected_depth is not None:
            assert depth == expected_depth
        found = []
        for i in range(entries):
            offset = 12+i*12
            if depth:
                logical,lo,hi,_ = struct.unpack_from("<IIHH",block,offset)
                physical = lo+(hi<<32)
                found.extend(self.extents(self.data[physical*self.block:(physical+1)*self.block],depth-1))
            else:
                logical,length,hi,lo = struct.unpack_from("<IHHI",block,offset)
                unwritten = length > 32768
                found.append((logical,length-32768 if unwritten else length,lo+(hi<<32),unwritten))
        return found

    def contents(self, inode):
        if not inode["size"]:
            return b""
        assert inode["flags"] & 0x80000 and not inode["flags"] & 0x10000000
        assert inode["size"] <= 1048576
        result = bytearray(inode["size"])
        for logical,length,physical,unwritten in self.extents(inode["raw"][40:100]):
            if unwritten:
                continue
            start = logical*self.block
            end = min(inode["size"],(logical+length)*self.block)
            if start < end:
                result[start:end] = self.data[physical*self.block:physical*self.block+end-start]
        return bytes(result)

    def entries(self, inode):
        assert inode["mode"] & 0xF000 == 0x4000
        data = self.contents(inode)
        result = {}
        for start in range(0,len(data),self.block):
            offset = start
            while offset+8 <= min(start+self.block,len(data)):
                number,length,size,kind = struct.unpack_from("<IHBB",data,offset)
                assert length >= 8 and length % 4 == 0 and offset+length <= start+self.block and size <= length-8
                if number:
                    name = data[offset+8:offset+8+size].decode()
                    if name not in (".",".."):
                        assert name not in result
                        result[name] = number
                offset += length
        return result

    def resolve(self, name):
        inode = self.inode(2)
        for part in name.split("/"):
            inode = self.inode(self.entries(inode)[part])
        return inode

    def file(self,name):
        inode = self.resolve(name)
        assert inode["mode"] & 0xF000 == 0x8000
        data = self.contents(inode)
        info = {key:value for key,value in inode.items() if key != "raw"}
        info.update(sha256=hashlib.sha256(data).hexdigest(),hex=data.hex() if len(data)<=4096 else None)
        return data,info


def main():
    cut = serial("after_return-cut.log")
    recovered = serial("after_return-recover.log")
    base,before,after = cut["baseline"],recovered["before_recovery"],recovered["after_recovery"]
    intent = document(base,"operation.json")["intent"]
    result = intent["result"]
    snapshots = {}
    for label,snapshot in [("baseline",base),("before_recovery",before),("after_recovery",after)]:
        repositories = {}
        for role,repo in snapshot["repos"].items():
            values = objects(repo)
            original = objects(base["repos"][role])
            refs = repo["refs"]
            repositories[role] = dict(object_count=len(values),all_original_objects_exact=values==original,
                  refs_stdout=bytes.fromhex(refs["stdout_hex"]).decode(),refs_stderr=bytes.fromhex(refs["stderr_hex"]).decode(),
                  refs_exit=refs["exit"],fsck_exit=repo["fsck"]["exit"],fsck_stderr=bytes.fromhex(repo["fsck"]["stderr_hex"]).decode())
        snapshots[label] = dict(repositories=repositories,
                               operation=document(snapshot,"operation.json"),
                               checkpoint=document(snapshot,"result-checkpoint.json") if "result-checkpoint.json" in snapshot["files"] else None,
                               provider_store=document(snapshot,"provider/state.json"))
    recorded=json.loads((EVIDENCE/"after_return-result.json").read_text())
    images={}
    root="scope/case-after_return/"
    selected={"local_continuation":root+"repo/.git/"+intent["continuation"],
              "provider_archive":root+"provider/repo/.git/refs/archives/"+intent["id"],
              "provider_head":root+"provider/repo/.git/refs/heads/A",
              "retained_result":root+"repo/.git/refs/retained/result",
              "operation":root+"operation.json","checkpoint":root+"result-checkpoint.json",
              "provider_store":root+"provider/state.json"}
    for label,key in [("pre_recovery_home_without_journal_replay","pre_recovery"),("post_clean_recovery","post_recovery")]:
        metadata=recorded[key]
        compressed=(EVIDENCE/metadata["file"]).read_bytes()
        assert hashlib.sha256(compressed).hexdigest()==metadata["gzip_sha256"]
        data=gzip.decompress(compressed)
        assert len(data)==metadata["raw_bytes"] and hashlib.sha256(data).hexdigest()==metadata["raw_sha256"]
        fs=Ext4(data)
        files={}
        for name,path in selected.items():
            try:
                contents,info=fs.file(path)
                info["path"]=path
                if name in ("provider_head","retained_result"):
                    info["matches_expected_41_bytes"]=contents==(result+"\n").encode()
                elif name in ("operation","checkpoint","provider_store"):
                    serial_name={"operation":"operation.json","checkpoint":"result-checkpoint.json","provider_store":"provider/state.json"}[name]
                    expected=bytes.fromhex(after["files"][serial_name]["hex"])
                    info["equals_after_recovery_serial_bytes"]=contents==expected
                files[name]=info
            except (AssertionError,KeyError,ValueError,struct.error) as error:
                files[name]=dict(path=path,unavailable_from_raw_home_metadata=str(error),journal_replay_performed=False)
        object_checks=[]
        if key=="post_recovery":
            for role in ("local","provider"):
                repository=root+("repo/.git/" if role=="local" else "provider/repo/.git/")
                for oid,item in objects(after["repos"][role]).items():
                    compressed_object,_=fs.file(repository+"objects/"+oid[:2]+"/"+oid[2:])
                    body=zlib.decompress(compressed_object)
                    object_checks.append(dict(role=role,oid=oid,exact=body==item["encoded"],git_sha1=hashlib.sha1(body).hexdigest()))
        images[label]=dict(raw_sha256=metadata["raw_sha256"],files=files,loose_object_checks=object_checks,
                           parser_limit="Bounded extents-only read of this 32MiB ext4 image; no journal replay or filesystem writes")
    logs={}
    for name,item in before["files"].items():
        if name.endswith(".jsonl"):
            data=bytes.fromhex(item["hex"])
            logs[name]=dict(bytes=len(data),nul_bytes=data.count(b"\0"),sha256=hashlib.sha256(data).hexdigest(),
                            semantic_role="Unsynced diagnostic log, not authoritative outcome evidence")
    report=dict(cut_return=cut.get("returned"),recovery_result=recovered["recovery_result"],expected_result=result,
                expected_new_ref_bytes=(result+"\n").encode().hex(),snapshots=snapshots,images=images,diagnostic_logs=logs,
                source_inputs={name:hashlib.sha256((EVIDENCE/name).read_bytes()).hexdigest() for name in
                    ["after_return-cut.log","after_return-recover.log","after_return-result.json","after_return-cut.receipt.json","after_return-recover.receipt.json"]},
                runtime=cut["runtime"],effects="Pure serial/object/image-byte audit only; no Git, VM, container, replay or input mutation")
    (OUT/"FINDINGS.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(dict(cut_return=report["cut_return"],recovery=report["recovery_result"],
                         post_ref_sizes={key:value.get('size') for key,value in images['post_clean_recovery']['files'].items()},
                         object_checks=images['post_clean_recovery']['loose_object_checks'],diagnostic_logs=logs)))


if __name__=="__main__":
    main()
