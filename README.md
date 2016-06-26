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

#####How to install Pillow to Blender?
If your system's python version matches with blender's python version,

(To find blender's python version, switch to python console in blender and type these commands.)

    >>> import sys
    >>> sys.version
    '3.5.1 (default, Jun  7 2016, 02:56:20) \n[GCC 5.3.0]'
    
(means, version = 3.5.1)

If pillow is not installed, first install it with;

```pip install -U pillow```

to your system's python.

And then, you can just copy the "PIL" directory form your system's python's site-packages directory
to blender's python's site-packages directory. :) 

#####Alternative pillow installation ways:
InshaAllah, soon ...



