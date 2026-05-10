# Biosphere Zero

A first-person 3D Mars terraforming map built in Blender — original design, inspired by Among Us-style multi-room maps but not a copy of any existing map.

## Concept

A cluster of 12 abandoned glass biospheres on Mars, each with a different ecosystem theme, connected by lit glass tunnels. Outside: rusty Mars terrain, two moons, distant mountain silhouettes, faint dust haze.

## Map (12 domes)

| Dome | Theme |
|---|---|
| Heart Hall | Central hub with table, stools, emergency button, holo-plant |
| Jungle Prime | Rainforest with ferns, vines, mossy rocks, holo butterflies |
| Tundra-7 | Frozen biome with ice pond, stalagmites, snow piles |
| Coral Tank | Underwater garden with coral, fish, sand floor |
| Desert Bloom | Cacti, dunes, fossils, holo lizard |
| Myco Grove | Bio-luminescent mushrooms (purple/cyan/green glow) |
| Crystal Vault | Geode cavern with violet & sapphire crystals |
| Solar Farm | Tilted solar panel grid, inverter, warning beacon |
| Wind Vane | Three turbines, weather balloons, anemometer, prisms |
| Water Purity | Spiraling stairs into water well, coiled pipes, valves |
| Reactor Heart | Radiant lava pool, cooling pipes, yellow warning lamps |
| Comms Dish | Tilted parabolic dish, beacon lights, console |

## Files

- `blend/biosphere_zero.blend` — full scene
- `renders/` — 6 PNG renders
  - `fps_heart_hall.png`
  - `fps_coral_tunnel.png`
  - `fps_reactor.png`
  - `fps_myco.png`
  - `fps_crystal.png`
  - `iso_overview.png`
- `scripts/` — build scripts (one per phase)

## Tech

- Blender 5.1
- EEVEE renderer with raytracing
- 1920x1080, 64 samples
- Volume scatter for atmospheric haze
- Compositor: glare (fog glow) + lens distortion (chromatic aberration)
- Filmic color management with Medium High Contrast look

## Cameras

- `FPS_Cam` — 75° FOV, 1.7m eye height, 36mm sensor
- `ISO_Cam` — orthographic top-down for the overview render
