"""Offline guards before root's first hosted fixture."""
from pathlib import Path
import tempfile
from rootlab import Lab


def main():
    with tempfile.TemporaryDirectory(prefix="rootlab-guards-", dir=Path(__file__).resolve().parent) as tmp:
        lab = Lab(Path(tmp), "exh-1109-check")
        for bad in ["main", "exh-1109-causal-other", "exh-1109-check-x:refs/heads/main"]:
            try:
                lab.refname(bad)
            except ValueError:
                pass
            else:
                raise AssertionError("Out-of-scope ref accepted")
        counter = Path(tmp) / "count"
        args = ["/usr/bin/python3", "-c", "import pathlib,sys;p=pathlib.Path(sys.argv[1]);p.write_text(str(int(p.read_text())+1) if p.exists() else '1')", str(counter)]
        lab.command("one-effect", args, mutation=True)
        try:
            lab.command("one-effect", args, mutation=True)
        except FileExistsError:
            pass
        else:
            raise AssertionError("Duplicate dispatch was not rejected")
        assert counter.read_text() == "1"
        captured = []
        lab.command = lambda label, args, **kw: captured.append((args, kw))
        lab.push("capture-only", {"exh-1109-check-new": (None, "a" * 40)})
        assert "--atomic" in captured[0][0]
        assert "--force-with-lease=refs/heads/exh-1109-check-new:" in captured[0][0]
    print("Offline namespace, duplicate-dispatch and absence-lease controls passed; zero network calls")


if __name__ == "__main__":
    main()
