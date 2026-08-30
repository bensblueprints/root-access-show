import json, urllib.request, time
COMFY = "http://127.0.0.1:8188"
def wf(pos, neg, prefix, seed, w=1024, h=1024):
    return {
      "1": {"class_type":"UNETLoader","inputs":{"unet_name":"flux1-dev-fp8-e4m3fn.safetensors","weight_dtype":"fp8_e4m3fn"}},
      "2": {"class_type":"DualCLIPLoader","inputs":{"clip_name1":"clip_l.safetensors","clip_name2":"t5xxl_fp16.safetensors","type":"flux"}},
      "3": {"class_type":"VAELoader","inputs":{"vae_name":"ae.safetensors"}},
      "4": {"class_type":"CLIPTextEncode","inputs":{"text":pos,"clip":["2",0]}},
      "5": {"class_type":"CLIPTextEncode","inputs":{"text":neg,"clip":["2",0]}},
      "6": {"class_type":"EmptySD3LatentImage","inputs":{"width":w,"height":h,"batch_size":1}},
      "7": {"class_type":"KSampler","inputs":{"model":["1",0],"positive":["4",0],"negative":["5",0],"latent_image":["6",0],"seed":seed,"steps":28,"cfg":3.5,"sampler_name":"euler","scheduler":"simple","denoise":1.0}},
      "8": {"class_type":"VAEDecode","inputs":{"samples":["7",0],"vae":["3",0]}},
      "9": {"class_type":"SaveImage","inputs":{"filename_prefix":prefix,"images":["8",0]}},
    }
SHEET = "full body character sheet, front view, standing in a strict T-pose with arms straight out horizontally to the sides, legs straight and together, feet flat, no base, no stand, no pedestal, plain light grey background, centered, entire figure fully visible, character reference for 3D modeling"
NEG = "text, words, letters, logo, watermark, signature, lowres, blurry, deformed, bad anatomy, extra limbs, cropped, cut off, side view, back view, action pose, base, stand, pedestal"
prompts = [
  (f"A cyberpunk master hacker, holographic head, dark hooded coat with acid-green graffiti, glowing green energy staff, three small blade drones. {SHEET}", "tp_zero_day", 6001),
  (f"A cyberpunk psyker, skull studded with data jacks, trailing spinal cables, wired-up dark clothing, faint halo of holographic screens. {SHEET}", "tp_neural_burn", 6002),
  (f"A cyberpunk drone-controller soldier, antenna crown, bracer tablet on one arm, dark infantry gear with green accents. {SHEET}", "tp_swarm_tech", 6003),
  (f"A cyberpunk stealth assassin, glitch-camouflage poncho, blocky rail-pistol, glowing neural spike, grapple line on hip, dark clothing. {SHEET}", "tp_ghost_walker", 6004),
  (f"A cyberpunk corporate security director, clock-faced helmet, spine of data screens on back, temporal staff, glowing chrono-blade, clean chrome armor with electric-blue accents. {SHEET}", "tp_kairos", 6005),
  (f"A cyberpunk heavy weapons trooper, stabilizer legs, crackling arc projector fed by twin high-voltage tanks, chrome armor with electric-blue accents. {SHEET}", "tp_arc_sentinel", 6006),
  (f"A cyberpunk squad leader, tactical holographic light, command baton, two spotter drones, chrome armor with electric-blue accents. {SHEET}", "tp_nexus_commander", 6007),
  (f"A cyberpunk soldier, white-plated armor, pulse rifle, sensor pods, chrome armor with electric-blue accents. {SHEET}", "tp_nexus_trooper", 6008),
]
for pos, prefix, seed in prompts:
    r = urllib.request.urlopen(urllib.request.Request(COMFY+"/prompt", data=json.dumps({"prompt":wf(pos,NEG,prefix,seed)}).encode(), headers={"Content-Type":"application/json"}))
    d = json.loads(r.read())
    print(prefix, "queued" if d.get("prompt_id") else "ERR "+str(d.get("node_errors"))[:200])
time.sleep(3)
while True:
    q = json.loads(urllib.request.urlopen(COMFY+"/queue").read())
    if not q["queue_running"] and not q["queue_pending"]: break
    time.sleep(5)
print("DONE")
