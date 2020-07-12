from checkerapp.models import AlertPlugin
from checkerapp.models import PluginList


def run():
    existing_plugins = list(PluginList.objects.values_list("name", flat=True))
    all_plugins = [cls.__name__ for cls in AlertPlugin.__subclasses__()]

    for plugin in existing_plugins:
        if plugin not in all_plugins:
            PluginList.objects.filter(name=plugin).delete()
            print(f"Removed {plugin} !")
