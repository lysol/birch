DESIGN

Games can be created and placed in examples/. The design of the engine expects a procedural approach,
with chunks being seeded as needed when the view is scrolled. Implementing a `seed_handler` method and registering
it with the engine is the way forward here.

Game loop logic is placed in a "tick handler", which is not a zookeeper who deals with arachnids.

Package builds should be ok now. Run `python3 setup.py install`, then any of the examples, such as `python3 -m birch.examples.scamcity`.

NOTES

See the Leaburg example for an approach using [Tiled](https://www.mapeditor.org/) maps. You still must edit a spritesheet, and include a `json` file to mark
where tiles are sliced. I'll update this later to instead draw from the tileset itself.