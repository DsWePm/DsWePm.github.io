---
title: "Falling into the canyon: how this homepage was made"
date: 2026-10-30
kind: note
category: cg
dossier: FILE-03
tags: blender, cycles, three.js, glsl
summary: A procedurally generated Kowloon Walled City, a free-fall camera driven by physics, 254 frames of Cycles pre-renders, and the details of bringing them back to the web.
---

The homepage opens on a rain-wet white slab with a crack in it. Below the crack is a canyon of buildings crowded with security cages, air-conditioner units and hanging laundry. Scroll down and the camera falls in.

This is how it was put together.

## The city: generated entirely by script

Not a single object in the city was placed by hand. `build_city.py` takes a random seed and lays out units floor by floor along both sides of the crack: windows, security cages, air conditioners, drainpipes, laundry poles. Each unit claims its space first, and whatever is placed later reads the claimed ranges, so an air conditioner never ends up inside a cage and the pipes route around them.

```python
def free_u(fr, L):
    """a spot along the facade that nothing else has claimed yet"""
    for _ in range(12):
        u = rng.uniform(0.15, L - 0.15)
        if not any(a - 0.1 < u < b + 0.1 for a, b in fr.busy):
            return u
    return None
```

The wall colours follow old photographs of the Walled City: faded blue, pink, beige and green plaster over dirty concrete. The light in the windows mixes tungsten yellow, cold white tubes, greenish tubes, and light through red and rose curtains.

> The cluttered colour doesn't come from saturation, but from **many low-saturation colours packed together**.

## The laundry: simulate once, reuse everywhere

The hanging clothes are real cloth simulations. Simulating every pole would be far too slow, so only 8 variants are simulated: 3 T-shirts on hangers (different wind), 2 sheets thrown over a pole, 2 pegged sheets and 1 towel. Each result is frozen into a mesh, and every instance shares that mesh, changing only its material and scale.

| Variant | Count | Simulation time |
| --- | --- | --- |
| T-shirt | 3 | about 40 s each |
| Sheet | 4 | 4–5 s each |
| Towel | 1 | 1 s |

## The camera: riding a falling body

The first camera was keyframed and eased, and it felt like an elevator. It now follows an integrated falling body: gravity, quadratic air drag (terminal speed 55 m/s), a horizontal pull towards the landing spot, and an aerodynamic righting torque that grows with the square of the speed. The camera simply rides along.

![A frame from the fall](hero/fall/f_0100.webp)

It hits the ground at about 34.9 m/s. In the last few frames the floor fills the whole picture, so at the moment the screen is fully black the page cuts to the archive through a waterfall of characters.

## Back on the web

- 254 WebP frames at 1920×1080, 60 fps, 21 MB in total; the scroll position maps straight to a frame number
- The still before the fall is interactive: depth parallax, rain ripples, and the gyroscope on phones
- The rain is a separately rendered loop, composited as refraction instead of being added as white

![The separately rendered rain loop: 4 s, 60 fps, on black, with the slab and buildings as holdouts](hero/rain.mp4)

The next post might be about the character-waterfall cut.
