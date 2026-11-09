import os
from pathlib import Path
import re
import stat


class DurableRefError(RuntimeError):
    pass


def scoped_plans(directory, intent):
    case = Path(directory)
    prefix = case.name.removeprefix("case-")
    allowed = ("validated", "marked", "request_logged", "provider_head", "provider_archive",
               "provider_receipt", "acknowledged", "result_ref", "result_checkpoint", "complete", "after_return")
    if prefix not in allowed or case != Path("/state/scope") / ("case-" + prefix):
        raise DurableRefError("outside_owned_case")
    identity = "op-case-" + prefix
    continuation = "refs/retained/completed-case-" + prefix
    if intent["id"] != identity or intent["continuation"] != continuation or intent["provider"] != str(case / "provider"):
        raise DurableRefError("frozen_scope_mismatch")
    if any(not re.fullmatch(r"[0-9a-f]{40}", intent[key]) or intent[key] == "0"*40 for key in ("input", "result", "expected")) or intent["input"] != intent["expected"]:
        raise DurableRefError("unsupported_object_identity")
    return {(str(case / "provider/repo"), "refs/heads/A"):(intent["result"],intent["expected"],"provider_head"),
            (str(case / "provider/repo"), "refs/archives/" + identity):(intent["result"],"0"*40,"provider_archive"),
            (str(case / "repo"), continuation):(intent["result"],"0"*40,"local_continuation")}


class LooseFiles:
    def __init__(self, ops=os):
        self.ops = ops

    def visit(self, case, repo, ref, expected, role, synchronize=False):
        target = Path(repo) / ".git" / ref
        components = target.parent.parts[1:]
        handles = []
        anchor_device = None
        trace = []
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        try:
            descriptor = self.ops.open("/",flags)
            handles.append((Path("/"),descriptor,True))
            current = Path("/")
            for index,name in enumerate(components):
                current = current / name
                try:
                    descriptor = self.ops.open(name,flags,dir_fd=descriptor)
                except FileNotFoundError:
                    if not synchronize and expected == "0"*40 and role == "provider_archive" and index == len(components)-1 and name == "archives":
                        return []
                    raise
                handles.append((current,descriptor,True))
                info = self.ops.fstat(descriptor)
                if not stat.S_ISDIR(info.st_mode):
                    raise DurableRefError("not_normal_directory:" + str(current))
                if current == case:
                    anchor_device = info.st_dev
                if current == case or case in current.parents:
                    if info.st_uid != self.ops.geteuid() or info.st_dev != anchor_device:
                        raise DurableRefError("directory_not_owned_on_case_filesystem:" + str(current))
                if name == ".git":
                    for unsupported in ("commondir","packed-refs"):
                        try:
                            self.ops.stat(unsupported,dir_fd=descriptor,follow_symlinks=False)
                        except FileNotFoundError:
                            pass
                        else:
                            raise DurableRefError("unsupported_git_layout:" + unsupported)
            parent = descriptor
            try:
                before = self.ops.stat(target.name,dir_fd=parent,follow_symlinks=False)
            except FileNotFoundError:
                if not synchronize and expected == "0"*40:
                    return []
                raise
            if expected == "0"*40:
                raise DurableRefError("absence_expectation_not_met")
            if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_uid != self.ops.geteuid() or before.st_dev != anchor_device:
                raise DurableRefError("not_owned_normal_loose_ref")
            descriptor = self.ops.open(target.name,os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,dir_fd=parent)
            handles.append((target,descriptor,False))
            opened = self.ops.fstat(descriptor)
            if (opened.st_dev,opened.st_ino) != (before.st_dev,before.st_ino):
                raise DurableRefError("ref_changed_during_open")
            data = b""
            while len(data) <= 41:
                chunk = self.ops.read(descriptor,42-len(data))
                if not chunk:
                    break
                data += chunk
            if data != (expected+"\n").encode() or self.ops.fstat(descriptor).st_size != 41:
                raise DurableRefError("loose_ref_bytes_mismatch")
            if synchronize:
                self.ops.fsync(descriptor)
                trace.append(str(target))
                after = self.ops.stat(target.name,dir_fd=parent,follow_symlinks=False)
                if (after.st_dev,after.st_ino) != (opened.st_dev,opened.st_ino):
                    raise DurableRefError("ref_name_changed_during_barrier")
                for path,fd,is_directory in reversed(handles):
                    if is_directory and (path == case or case in path.parents):
                        self.ops.fsync(fd)
                        trace.append(str(path))
            return trace
        except OSError as error:
            raise DurableRefError("ref_barrier_io_error:" + str(error)) from error
        finally:
            for _,descriptor,_ in reversed(handles):
                self.ops.close(descriptor)


def install(protocol, directory, intent, files=None, report=None):
    case = Path(directory)
    plans = scoped_plans(case,intent)
    original = protocol.Git.run
    if getattr(original,"durable_ref_variant",False):
        raise DurableRefError("wrapper_already_installed")
    if any(key in protocol.ENV for key in ("GIT_DIR","GIT_COMMON_DIR","GIT_NAMESPACE","GIT_WORK_TREE","GIT_CONFIG_COUNT","GIT_CONFIG_PARAMETERS")):
        raise DurableRefError("unsupported_git_environment_redirect")
    files = files or LooseFiles()
    def run(self,*args,stdin=None,allowed=(0,),env=None):
        if not args or args[0] != "update-ref":
            return original(self,*args,stdin=stdin,allowed=allowed,env=env)
        if len(args) != 4 or stdin is not None or env is not None or allowed != (0,):
            raise DurableRefError("unsupported_update_ref_form")
        selected = plans.get((str(self.root),args[1]))
        if selected is None or (args[2],args[3]) != selected[:2]:
            raise DurableRefError("outside_frozen_update_ref_scope")
        new,old,role = selected
        files.visit(case,self.root,args[1],old,role)
        result = original(self,*args,stdin=stdin,allowed=allowed,env=env)
        if result.returncode != 0:
            raise DurableRefError("unsuccessful_update_ref_cannot_acknowledge_barrier")
        synchronized = files.visit(case,self.root,args[1],new,role,synchronize=True)
        if report is not None:
            report(dict(role=role,repository=str(self.root),ref=args[1],new=new,old=old,synchronized=synchronized))
        return result
    run.durable_ref_variant = True
    run.__wrapped__ = original
    protocol.Git.run = run
    return original
