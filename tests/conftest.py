def pytest_configure(config):
    plugin = config.pluginmanager.getplugin("mypy")
    plugin.mypy_argv.append("--exclude")
    plugin.mypy_argv.append("/docs/")
