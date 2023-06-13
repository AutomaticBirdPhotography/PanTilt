import ip_config
ip_configurator = ip_config.IPConfigurator()
def configure_ip():
    ip_configurator.selectIP(invalid_ip=ip_configurator.clientAddress)
    print(ip_configurator.clientAddress)
    
configure_ip()