import ip_config
def configure_ip():
    configurator = ip_config.IPConfigurator()
    while configurator.clientAddress != valid_ip:
        configurator.selectIP(invalid_ip=configurator.clientAddress)
        if configurator.closed: break
    print(configurator.clientAddress)

# Printer den valgte IP-adressen
valid_ip = "192.168.10.234"
configure_ip()