Source.Python Data/Custom/Entities ReadMe

This directory is used for custom entity data by entitiestools.

To load entity data in a plugin/custom package, use entitiestools.load_entities_data.

.. code:: python

    from entitiestools import load_entities_data

    # This will automatically load the directory with the plugin/custom package name
    # e.g. (../addons/source-python/data/custom/entities/plugin_name)
    # and make them accessible by Entity.
    load_entities_data()
