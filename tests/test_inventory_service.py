from ctrlops.services.inventory_service import scan_inventory


def test_inventory_output_shape():
    inventory = scan_inventory()

    assert "hostname" in inventory
    assert "os" in inventory
    assert "kernel" in inventory
    assert isinstance(inventory["network_interfaces"], dict)
    assert isinstance(inventory["open_ports"], list)
