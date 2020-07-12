class Service:
    EMAIL, SMS = list(range(2))
    PLUGIN_CHOICES = ((EMAIL, "EMAIL"), (SMS, "SMS"))

    def get_plugin_choices(self):
        plugins = ["TgPlugin", "Generic"]

        for plugin_number, plugin in zip(range(2, len(plugins) + 2), plugins):
            self.temp = (plugin_number, plugin)
            self.PLUGIN_CHOICES += tuple((self.temp,))
        return self.PLUGIN_CHOICES


s = Service()
print(s.get_plugin_choices())
