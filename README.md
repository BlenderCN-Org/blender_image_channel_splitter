###Blender Image Channel Splitter

######Splits and saves image channels to individual single channel grayscale images.

If the addon finds the [Pillow(PIL)](https://pypi.python.org/pypi/Pillow) python module it will use it, if not it will use blender api.
[Pillow](https://pypi.python.org/pypi/Pillow) version is much faster and uses a lot less RAM.

[![Blender Image Channel Splitter Youtube Video](http://img.youtube.com/vi/6NnkoAUqKus/0.jpg)](http://www.youtube.com/watch?v=6NnkoAUqKus)

#####A warning!!
if you do not have enough RAM, Blender api version may be not usable for textures bigger than 3K.

It takes 10-50 seconds to process images and it may use a lot of RAM for the time period.
(After that it frees the RAM.)

**2K** textures uses **~1GB RAM**
**3K** textures uses **~2.5GB RAM**

and grows exponantial-ish-ly.

