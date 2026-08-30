#!/usr/bin/env python3
"""Generate 8 T-pose characters (4 NU11 + 4 Terable) via Meshy text-to-3d.
T-pose + no base for video/rigging. preview -> refine -> download glb.
"""
import json, os, time, urllib.request

API = "https://api.meshy.ai/openapi/v2/text-to-3d"
ENV = os.path.expanduser("~/.hermes/.env")
OUT = os.path.expanduser("~/zda/tpose")
os.makedirs(OUT, exist_ok=True)

def key():
    for line in open(ENV):
        if line.startswith("MESHY_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("no MESHY_API_KEY")

def api(method, url, token, payload=None):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    body = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, method=method, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())

TPOSE = "standing in a strict T-pose, arms straight out horizontally to the sides, legs straight and together, facing forward, upright, no base, no stand, no pedestal, free-standing full body"
PROMPTS = {
 "nu11-zero-day": f"A cyberpunk master hacker, holographic head, coat of living code, dark hooded clothes with acid-green graffiti, holding a glowing green energy staff, three blade drones orbiting him. {TPOSE}. Realistic sci-fi game character, high detail.",
 "nu11-neural-burn": f"A cyberpunk psyker, a wired-up net burn victim, skull studded with data jacks, trailing spinal cables, halo of stolen holographic screens, dark clothes. {TPOSE}. Realistic sci-fi game character, high detail.",
 "nu11-swarm-tech": f"A cyberpunk drone-controller infantry, antenna crown, bracer tablet, one gloved hand raised to conduct a swarm of drones, dark infantry gear with green accents. {TPOSE}. Realistic sci-fi game character, high detail.",
 "nu11-ghost-walker": f"A cyberpunk stealth assassin, glitch-camouflage poncho, blocky rail-pistol, glowing neural spike, grapple line on the hip, dark clothing. {TPOSE}. Realistic sci-fi game character, high detail.",
 "terable-director-kairos": f"A cyberpunk corporate security director, clock-faced helmet, spine of data screens, temporal staff, glowing chrono-blade, clean chrome armor with electric-blue accents. {TPOSE}. Realistic sci-fi game character, high detail.",
 "terable-arc-sentinel": f"A cyberpunk heavy weapons trooper, stabilizer legs, a crackling arc projector fed by twin high-voltage tanks, clean chrome armor with electric-blue accents. {TPOSE}. Realistic sci-fi game character, high detail.",
 "terable-nexus-commander": f"A cyberpunk squad leader, wrapped in tactical holographic light, command baton, two spotter drones, clean chrome armor with electric-blue accents. {TPOSE}. Realistic sci-fi game character, high detail.",
 "terable-nexus-trooper": f"A cyberpunk soldier, white-plated armor, pulse rifle, sensor pods, clean chrome armor with electric-blue accents. {TPOSE}. Realistic sci-fi game character, high detail.",
}

def main():
    tok = key()
    slugs = list(PROMPTS)
    state = {s: {} for s in slugs}
    # 1. previews
    print("=== kicking off 8 previews ===")
    for s in slugs:
        r = api("POST", API, tok, {
            "mode": "preview", "prompt": PROMPTS[s], "art_style": "realistic",
            "texture_richness": "high", "should_remesh": True,
            "target_polycount": 100000, "target_formats": ["glb"],
        })
        state[s]["preview"] = r["result"]
        print(f"  {s}: preview {r['result'][:13]}...")
    # 2. poll previews
    print("=== polling previews ===")
    while any("preview_done" not in state[s] for s in slugs):
        for s in slugs:
            if "preview_done" in state[s]: continue
            st = api("GET", f"{API}/{state[s]['preview']}", tok)
            if st["status"] in ("SUCCEEDED", "FAILED", "CANCELED"):
                state[s]["preview_done"] = st["status"]
                print(f"  {s}: preview {st['status']}" + (f" ({st.get('task_error',{}).get('message','')})" if st["status"]=="FAILED" else ""))
        time.sleep(20)
    # 3. refines
    print("=== kicking off refines ===")
    for s in slugs:
        if state[s].get("preview_done") != "SUCCEEDED":
            print(f"  {s}: SKIP refine (preview failed)"); continue
        r = api("POST", API, tok, {
            "mode": "refine", "preview_task_id": state[s]["preview"],
            "enable_pbr": True, "target_formats": ["glb"],
        })
        state[s]["refine"] = r["result"]
        print(f"  {s}: refine {r['result'][:13]}...")
    # 4. poll refines + download
    print("=== polling refines + downloading ===")
    while any("refine" in state[s] and "refine_done" not in state[s] for s in slugs):
        for s in slugs:
            if "refine" not in state[s] or "refine_done" in state[s]: continue
            st = api("GET", f"{API}/{state[s]['refine']}", tok)
            if st["status"] in ("SUCCEEDED", "FAILED", "CANCELED"):
                state[s]["refine_done"] = st["status"]
                print(f"  {s}: refine {st['status']}")
                if st["status"] == "SUCCEEDED":
                    url = st.get("model_urls", {}).get("glb")
                    if url:
                        urllib.request.urlretrieve(url, os.path.join(OUT, s + "-tpose.glb"))
                        print(f"    downloaded {s}-tpose.glb")
        time.sleep(20)
    json.dump(state, open(os.path.join(OUT, "tpose_tasks.json"), "w"), indent=2)
    ok = sum(1 for s in slugs if state[s].get("refine_done") == "SUCCEEDED")
    print(f"\nDONE: {ok}/8 T-pose glbs generated -> {OUT}")

if __name__ == "__main__":
    main()
