
## Patching

After checking out optware (rev. 12863), we need to apply some patches.

The main one, to add support for MD-253 (based on WD MyBook v1.02.04) is

    patch -p1 < optware-md253.patch

after that, we correct some of the download URL for some of the packages

    patch -p1 < optware-sites.patch

and finally we set some software versions to match those on device and other build fixes

    patch -p1 < optware-md253_versions.patch
    patch -p1 < optware-md253-base.patch

### makefile changes

There are other small fixes that we might want to perform on makefile. Those are the place where source code is downloaded (DL_DIR) and where the final packages are written (PACKAGE_DIR).


If we pretend to move the toolchain into a globally accessible place, we can also modify TARGET_CROSS_TOP on the platforms/toolchain-md253.mk directory

## Building

Once the optware tree is prepared, we can build the packages as usual, by running

    make md253-target
    
    cd md253
    make directories
    make toolchain ipkg-utils

Before issuing the final `make`, there are some warnings we should account for. First, it is useful to manually build the python2x-stage targets, as they are broken and should be attempted twice to succeed (build for 27 is ok). 
Some other packages (kamailio) do initially fail, but get compiled if retried later (probably some missing requirement)

If the placement for packages (PACKAGE_DIR) is modified, to properly create the repository a few more changes are required on makefiles

    sed -i -e 's|$(BUILD_DIR)/\([^\.]*\.ipk\)|$(PACKAGE_DIR)/\1|' make/*.mk
    sed -i -e 's/$(IPKG_BUILD)\s\+$(.*IPK_DIR)[^ ;]*/& $(PACKAGE_DIR)/' make/*.mk

