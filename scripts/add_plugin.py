from checkerapp.models import AlertPlugin
from checkerapp.models import PluginList


def run():
    existing_plugins = list(PluginList.objects.values_list("name", flat=True))
    all_plugins = [cls.__name__ for cls in AlertPlugin.__subclasses__()]

    for plugin in all_plugins:
        if plugin not in existing_plugins:
            PluginList.objects.create(name=plugin)
            print(f"Created {plugin} !")
        else:
            print(f"{plugin} already exists !")
