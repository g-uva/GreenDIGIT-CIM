import argparse
import gzip
import hashlib
import io
import json
import sys
import uuid
import time, shlex
from datetime import datetime
from pathlib import Path
from typing import Iterator, Dict, Any

DEFAULT_CHUNK = 10_000

def iter_json_array(file_path: Path) -> Iterator[Dict[str, Any]]:
    """
    Stream a very large JSON array without loading it entirely in memory.
    Supports inputs like: [ {..}, {..}, ... ]
    This is a simple state machine that finds top-level JSON objects in an array.
    """
    with file_path.open("r", encoding="utf-8") as f:
        # Skip whitespace until '['
        ch = f.read(1)
        while ch and ch.isspace():
            ch = f.read(1)
        if ch != '[':
            raise ValueError("Input appears not to be a JSON array (doesn't start with '['). "
                             "If your file is NDJSON, use --input-format ndjson.")
        in_string = False
        escape = False
        depth = 0
        buf = io.StringIO()

        # Consume until first object starts
        while True:
            ch = f.read(1)
            if not ch:
                break
            if ch.isspace():
                continue
            if ch == ']':  # empty array
                return
            if ch == '{':
                depth = 1
                buf.write(ch)
                break
            elif ch == ',':
                continue  # allow trailing commas before first object (tolerant)
            else:
                # Unexpected
                raise ValueError("Malformed array: expected '{' or ']' after '['")
        # Now stream objects
        while True:
            ch = f.read(1)
            if not ch:
                raise ValueError("Unexpected EOF while reading JSON object.")
            buf.write(ch)
            if in_string:
                if escape:
                    escape = False
                elif ch == '\\\\':
                    escape = True
                elif ch == '\"':
                    in_string = False
            else:
                if ch == '\"':
                    in_string = True
                elif ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        # End of object
                        obj_txt = buf.getvalue()
                        buf = io.StringIO()
                        try:
                            yield json.loads(obj_txt)
                        except json.JSONDecodeError as e:
                            raise ValueError(f"Failed to parse object: {e}\\nObject text (truncated): {obj_txt[:200]}...")
                        # Now consume until next '{' or ']' (skipping commas/whitespace)
                        while True:
                            ch = f.read(1)
                            if not ch:
                                raise ValueError("Unexpected EOF after object; expected ',' or ']' ")
                            if ch.isspace():
                                continue
                            if ch == ',':
                                # next must be an object start
                                # skip whitespace
                                ch = f.read(1)
                                while ch and ch.isspace():
                                    ch = f.read(1)
                                if ch != '{':
                                    raise ValueError("Malformed array: expected '{' after comma")
                                depth = 1
                                buf.write(ch)
                                break
                            elif ch == ']':
                                return
                            else:
                                # Could be directly '{' without comma (tolerate), or error
                                if ch == '{':
                                    depth = 1
                                    buf.write(ch)
                                    break
                                raise ValueError("Malformed array: expected ',' or ']' ")
                # else: other characters ignored here

def iter_ndjson(file_path: Path) -> Iterator[Dict[str, Any]]:
    with file_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)

def md5_of_bytes(data: bytes) -> str:
    m = hashlib.md5()
    m.update(data)
    return m.hexdigest()

def write_chunk(records, out_path: Path, gzip_enabled: bool) -> Dict[str, Any]:
    # Build NDJSON bytes
    buf = io.BytesIO()
    for rec in records:
        line = json.dumps(rec, separators=(',', ':'), ensure_ascii=False).encode("utf-8") + b"\n"
        buf.write(line)
    raw = buf.getvalue()
    if gzip_enabled:
        gz_path = out_path.with_suffix(out_path.suffix + ".gz")
        with gzip.open(gz_path, "wb") as gzf:
            gzf.write(raw)
        size = gz_path.stat().st_size
        return {"path": str(gz_path), "count": len(records), "md5": md5_of_bytes(raw), "gzip": True, "size_bytes": size}
    else:
        with out_path.open("wb") as f:
            f.write(raw)
        size = out_path.stat().st_size
        return {"path": str(out_path), "count": len(records), "md5": md5_of_bytes(raw), "gzip": False, "size_bytes": size}

def main():
    p = argparse.ArgumentParser(description="Convert a .json (array) or .ndjson to NDJSON chunks with idempotency manifest.")
    p.add_argument("input", type=str, help="Path to input file (.json array or .ndjson)")
    p.add_argument("out_dir", type=str, help="Output directory for chunks + manifest")
    p.add_argument("--input-format", choices=["auto","array","ndjson"], default="auto", help="Treat input as array or NDJSON")
    p.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK, help="Records per chunk (default: 10k)")
    p.add_argument("--gzip", action="store_true", help="Gzip-compress output chunks")
    p.add_argument("--idem-key", type=str, default=None, help="Optional fixed Idempotency-Key (UUID). If omitted, generated.")
    p.add_argument("--prefix", type=str, default="chunk", help="Output filename prefix")
    p.add_argument("--start-seq", type=int, default=0, help="Starting X-Batch-Seq (default 0)")
    p.add_argument("--emit-curl", action="store_true", help="Print curl commands for upload")
    p.add_argument("--exec-curl", action="store_true", help="Execute curl for upload (requires curl installed)")
    p.add_argument("--endpoint", type=str, default=None, help="Upload endpoint, e.g. https://api.example/submit/ndjson")
    p.add_argument("--bearer", type=str, default=None, help="Bearer token for Authorization header")
    p.add_argument("--auto-resume", action="store_true", help="Query server for next expected seq and resume from there")
    p.add_argument("--status-endpoint", type=str, default=None, help="Ingest status endpoint, e.g. https://host/gd-cim-api/ingest/status")
    p.add_argument("--resume-from", type=int, default=None, help="Manually resume from this sequence number")
    p.add_argument("--verbose", action="store_true", help="Print detailed progress/logs")
    p.add_argument("--log-file", type=str, default=None, help="Append curl outputs to this file")
    p.add_argument("--resume-local", action="store_true", help="Use local progress file to resume (default: on)")
    args = p.parse_args()
    
    logfh = open(args.log_file, "a") if args.log_file else None
    in_path = Path(args.input).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    progress_path = out_dir / "progress.jsonl"

    if args.idem_key:
        idem = args.idem_key
    else:
        idem = str(uuid.uuid4())

    # Decide input format
    input_fmt = args.input_format
    if input_fmt == "auto":
        # Peek first non-space char
        with in_path.open("r", encoding="utf-8") as f:
            first = f.read(1024)
        first = first.lstrip()
        if first.startswith("["):
            input_fmt = "array"
        else:
            input_fmt = "ndjson"

    if input_fmt == "array":
        iterator = iter_json_array(in_path)
    else:
        iterator = iter_ndjson(in_path)

    manifest = {
        "created_at": datetime.utcnow().isoformat() + "Z",
        "input": str(in_path),
        "idempotency_key": idem,
        "chunk_size": args.chunk_size,
        "gzip": args.gzip,
        "prefix": args.prefix,
        "start_seq": args.start_seq,
        "chunks": []
    }

    seq = args.start_seq
    batch = []
    total = 0
    for rec in iterator:
        batch.append(rec)
        if len(batch) >= args.chunk_size:
            out_path = out_dir / f"{args.prefix}_{seq:06d}.ndjson"
            meta = write_chunk(batch, out_path, args.gzip)
            if args.verbose:
                print(f"[write] seq={seq} path={meta['path']} count={meta['count']} size={meta['size_bytes']}B", flush=True)
            meta.update({"seq": seq})
            manifest["chunks"].append(meta)
            total += len(batch)
            batch = []
            seq += 1
    # flush tail
    if batch:
        out_path = out_dir / f"{args.prefix}_{seq:06d}.ndjson"
        meta = write_chunk(batch, out_path, args.gzip)
        if args.verbose:
            print(f"[write] seq={seq} path={meta['path']} count={meta['count']} size={meta['size_bytes']}B", flush=True)
        meta.update({"seq": seq})
        manifest["chunks"].append(meta)
        total += len(batch)
        seq += 1

    if args.verbose:
        print(f"[write] seq={seq} path={meta['path']} count={meta['count']} size={meta['size_bytes']}B")

    manifest["total_records"] = total
    manifest["total_chunks"] = len(manifest["chunks"])

    # Save manifest.json
    manifest_path = out_dir / "manifest.json"
    with manifest_path.open("w", encoding="utf-8") as mf:
        json.dump(manifest, mf, indent=2)

    resume_from = args.resume_from
    if args.resume_local and progress_path.exists():
        try:
            last = -1
            with progress_path.open("r", encoding="utf-8") as pf:
                for line in pf:
                    if not line.strip(): continue
                    rec = json.loads(line)
                    last = max(last, int(rec.get("seq", -1)))
            if last >= 0:
                resume_from = max(resume_from or 0, last + 1)
                print(f"[resume-local] last_ok_seq={last} -> resume_from={resume_from}", flush=True)
        except Exception as e:
            print(f"[resume-local] ignored ({e})", file=sys.stderr)

    if args.auto_resume:
        if not args.status_endpoint:
            raise SystemExit("--status-endpoint is required when --auto-resume is set")
        if not args.bearer:
            raise SystemExit("--bearer is required when --auto-resume is set")
        # call status endpoint to get next_expected_seq
        import subprocess, json as _json
        status_cmd = [
            "curl", "-sS",
            "-H", f"Authorization: Bearer {args.bearer}",
            f"{args.status_endpoint}?idempotency_key={idem}"
        ]
        out = subprocess.check_output(status_cmd, text=True)
        st = _json.loads(out)
        resume_from = st.get("next_expected_seq", 0)
        print(f"[auto-resume] next_expected_seq={resume_from} (processed={len(st.get('processed', []))}, missing={st.get('missing', [])})")
        srv_next = st.get("next_expected_seq", 0)
        # take the higher of local vs server
        resume_from = max(resume_from or 0, int(srv_next))
        print(f"[auto-resume] server_next={srv_next} -> resume_from={resume_from}", flush=True)

    upload_chunks = manifest["chunks"]
    print(f"[plan] total_chunks={len(manifest['chunks'])} uploading={len(upload_chunks)} "
        f"(resume_from={resume_from})", flush=True)
    if resume_from is not None:
        upload_chunks = [c for c in upload_chunks if c["seq"] >= int(resume_from)]

    print(f"[plan] total={len(manifest['chunks'])} uploading={len(upload_chunks)} "
        f"(resume_from={resume_from}; first_seq={upload_chunks[0]['seq'] if upload_chunks else 'N/A'})", flush=True)

    # Optionally print or execute curl commands
    if args.emit_curl or args.exec_curl:
        if not args.endpoint:
            print("--endpoint is required for curl generation", file=sys.stderr)
        elif not args.bearer:
            print("--bearer is required for curl generation", file=sys.stderr)
        else:
            for c in upload_chunks:
                path = c["path"]
                headers = [
                    "-H", f"Authorization: Bearer {args.bearer}",
                    "-H", "Content-Type: application/x-ndjson",
                    "-H", f"Idempotency-Key: {manifest['idempotency_key']}",
                    "-H", f"X-Batch-Seq: {c['seq']}",
                ]
                if c.get("gzip"):
                    headers += ["-H", "Content-Encoding: gzip"]
                # cmd = ["curl", "-sS", "-X", "POST", *headers, "--data-binary", f"@{path}", args.endpoint]
                cmd = [
                    "curl", "--fail", "-sS", "-v", "-X", "POST", *headers,
                    "--data-binary", f"@{path}",
                    "-w", "\nHTTP_STATUS=%{http_code}\n",
                    args.endpoint,
                ]

                # stream output live (no buffering)
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
                ok = False
                for line in p.stdout:
                    print(line.rstrip(), flush=True)
                    if line.startswith("HTTP_STATUS=2"):
                        ok = True
                ret = p.wait()
                if not ok or ret != 0:
                    raise SystemExit(f"[ERROR] seq={c['seq']} upload failed (rc={ret})")
                
                with progress_path.open("a", encoding="utf-8") as pf:
                    pf.write(json.dumps({"seq": c["seq"], "path": path, "ts": time.time()}) + "\n")

                proc = subprocess.run(cmd, capture_output=True, text=True)
                print((proc.stdout or "") + (proc.stderr or ""), flush=True)
                if proc.returncode != 0 or "HTTP_STATUS=2" not in proc.stdout + proc.stderr:
                    raise SystemExit(f"[ERROR] seq={c['seq']} upload failed")

                if args.emit_curl:
                    printable = " ".join(shlex.quote(x) for x in cmd)
                    print(f"[emit] {printable}")

                if args.exec_curl:
                    if args.verbose:
                        print(f"[upload] seq={c['seq']} -> {args.endpoint}")
                    start = time.time()
                    proc = subprocess.run(cmd, capture_output=True, text=True)
                    out = (proc.stdout or "") + (proc.stderr or "")
                    if args.verbose:
                        print(out.strip())
                    if logfh:
                        logfh.write(f"\n=== seq {c['seq']} ===\n{out}\n")
                        logfh.flush()

                    # Fail if curl errored or HTTP not 2xx
                    if proc.returncode != 0 or "HTTP_STATUS=2" not in out:
                        if logfh: logfh.flush()
                        raise SystemExit(f"[ERROR] seq={c['seq']} upload failed (rc={proc.returncode}). See --verbose/--log-file.")
                    if args.verbose:
                        dur = time.time() - start
                        print(f"[ok] seq={c['seq']} uploaded in {dur:.2f}s")
            if logfh:
                logfh.close()

    print(f"Done. Wrote {manifest['total_chunks']} chunk(s) with {manifest['total_records']} record(s).")
    print(f"Idempotency-Key: {manifest['idempotency_key']}")
    print(f"Manifest: {manifest_path}")

def shlex_quote(s: str) -> str:
    # Minimal shell quoting for curl previews
    if not s or any(ch in s for ch in " \t\n\"'\\$`!()[]{}&|;<>?*"):
        return "'" + s.replace("'", "'\"'\"'") + "'"
    return s

if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        # allow piping to tools like 'head' without tracebacks
        try:
            sys.stdout.close()
        except Exception:
            pass
        sys.exit(0)