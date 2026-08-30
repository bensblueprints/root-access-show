# ROOT ACCESS — TV Series Production (Mr. Robot style)

A 12-episode cyberpunk thriller built on the Root Access universe (NU11 vs Terable Corp).
Seasons 2 & 3 planned. Video generated via H3 MiniMax (MCP server TBD) with reference-image continuity.

## The 4 Agents

### 🖊️ WRITER
Writes episode scripts. Input: the series bible. Output: 12 episode scripts with strictly-labeled
dialogue (CHARACTER: line), scene-change markers, and a cliffhanger at the end of every episode.
Main characters (8 core) carry the series; one-off characters (cop, lawyer, etc.) appear once to
advance plot and are never reused.

### 🔍 RESEARCHER
Researches source material (Mr. Robot, cyberpunk, the Root Access lore) and produces the series
bible + episode arcs. First agent in the pipeline.

### 🎬 DIRECTOR
Structures each episode into scenes with blocking. Marks every scene change:
`[SCENE: INT. BASEMENT — NIGHT]`, `[LOCATION CHANGE: basement → street]`, `[ROOM CHANGE: ...]`.
Defines which reference image carries into the next scene for visual continuity.

### ✂️ VIDEO EDITOR
Tracks reference-image continuity across scenes so the H3 MiniMax generator streams consistently:
each new scene is generated from the previous scene's frame + the characters as reference images.
Flags every generation breakpoint and the reference assets used.

## Pipeline
1. RESEARCHER → `bible.md`
2. WRITER → `episodes/ep01..ep12.md` (or `season1.md`)
3. DIRECTOR → scene blocking + change markers
4. VIDEO EDITOR → continuity/reference map (activates when the MCP video server arrives)

## Continuity rules (for the generator)
- Reuse the LAST scene's reference image as the seed for the next scene.
- Characters are re-referenced via their images into every new scene.
- Scene changes (room, location, time) MUST be explicitly marked so generation is deterministic.

## Core cast (8)
- NU11: Zero-Day, Neural Burn, Swarm Tech, Ghost Walker
- Terable Corp: Director Kairos, Arc Sentinel, Nexus Commander, Nexus Trooper
