from pynautobot import api
import yaml 
import os


PYTHONWARNINGS="ignore:Unverified HTTPS request"

data_file = "../inventory/devices.yaml"

with open(data_file) as f: 
    data = yaml.safe_load(f.read())

nb = api(url="http://127.0.0.1:8000", token="18acb72f4f8df7d5b939492edaebc88a0992640d")
nb.http_session.verify = False

# devices
for device in data["devices"]:
    print(f"Creating or Updating device {device['name']}")
    nb_device = nb.dcim.devices.get(name=device["name"])
    if not nb_device:
        nb_device = nb.dcim.devices.create(
            name=device["name"],
            manufacturer=nb.dcim.manufacturers.get(slug=device["manufacturer"]).id,
            site=nb.dcim.sites.get(slug=device["site"]).id,
            device_role=nb.dcim.device_roles.get(slug=device["device_role"]).id,
            device_type=nb.dcim.device_types.get(slug=device["device_type"]).id,
            status=device["status"],
        )
    if nb_device.local_context_data is None:
        print(f"Adding local configuration context to {device['name']}")
        if "local_context" in device.keys():
            nb_device.local_context_data = device["local_context"]

    if "tags" in device.keys():
        print(f"Setting tags on {device['name']}")
        tags = [nb.extras.tags.get(name=tag).id for tag in device["tags"]]
        nb_device.tags = tags

    for interface in device["interfaces"]:
        print(f"Creating or updating interface {interface['name']} on device {device['name']}")
        nb_interface = nb.dcim.interfaces.get(
            device_id=nb_device.id,
            name=interface["name"]
        )
        if not nb_interface:
            nb_interface = nb.dcim.interfaces.create(
                device=nb_device.id,
                name=interface["name"],
                type=interface["type"]
            )
        if "description" in interface.keys():
            nb_interface.description = interface["description"]
        if "label" in interface.keys():
            nb_interface.label = interface["label"]
        if "mtu" in interface.keys():
            nb_interface.mtu = interface["mtu"]
        if "mgmt_only" in interface.keys():
            nb_interface.mgmt_only = interface["mgmt_only"]
        if "enabled" in interface.keys():
            nb_interface.enabled = interface["enabled"]
        if "mode" in interface.keys():
            nb_interface.mode = interface["mode"]
        if "dhcp_helper" in interface.keys():
            nb_interface.custom_fields["dhcp_helper"] = interface["dhcp_helper"]
        if "vrrp_group" in interface.keys():
            nb_interface.custom_fields["vrrp_group"] = interface["vrrp_group"]
        if "vrrp_description" in interface.keys():
            nb_interface.custom_fields["vrrp_description"] = interface["vrrp_description"]
        if "vrrp_priority" in interface.keys():
            nb_interface.custom_fields["vrrp_priority"] = interface["vrrp_priority"]
        if "vrrp_primary_ip" in interface.keys():
            nb_interface.custom_fields["vrrp_primary_ip"] = interface["vrrp_primary_ip"]
        if "untagged_vlan" in interface.keys():
            nb_interface.untagged_vlan = nb.ipam.vlans.get(site=device["site_slug"],
                                                           name=interface["untagged_vlan"]
                                                           ).id
        if "tagged_vlans" in interface.keys():
            vl = [nb.ipam.vlans.get(site=device["site_slug"], name=vlan_name).id for vlan_name in
                  interface["tagged_vlans"]]
            # print("VLAN LIST")
            # print(vl)
            nb_interface.tagged_vlans = vl
        if "ip_addresses" in interface.keys():
            for ip in interface["ip_addresses"]:
                print(f"  Adding IP {ip['address']}")
                nb_ipadd = nb.ipam.ip_addresses.get(
                    address=ip["address"]
                )
                if not nb_ipadd:
                    nb_ipadd = nb.ipam.ip_addresses.create(
                        address=ip["address"],
                        status=ip["status"],
                        assigned_object_type="dcim.interface",
                        assigned_object_id=nb.dcim.interfaces.get(
                            device=device["name"],
                            name=interface["name"]).id
                    )
                if "vrf" in ip.keys():
                    nb_ipadd.vrf = nb.ipam.vrfs.get(name=ip["vrf"]).id
                if "tags" in ip.keys():
                    tgs = [nb.extras.tags.get(name=tag).id for tag in ip["tags"]]
                    nb_ipadd.tags = tgs
                nb_ipadd.interface = nb_interface.id
                nb_ipadd.save()
                if "primary" in ip.keys():
                    nb_device.primary_ip4 = nb_ipadd.id
                    nb_device.save()
        nb_interface.save()

# adding interface connections after they have all been created
for device in data["devices"]:
    nb_device = nb.dcim.devices.get(name=device["name"])
    for interface in device["interfaces"]:
        nb_interface = nb.dcim.interfaces.get(device_id=nb_device.id, name=interface["name"])
        if nb_interface["cable"] is None:
            if "bside_device" in interface.keys():
                print(
                    f"  Creating or updating interface connections between {device['name']}-{interface['name']} and {interface['bside_device']}-{interface['bside_interface']}")
                int_a = nb.dcim.interfaces.get(name=interface["name"], device=device["name"]).id
                int_b = nb.dcim.interfaces.get(name=interface["bside_interface"], device=interface["bside_device"]).id
                nb.dcim.cables.create(
                    termination_a_type="dcim.interface",
                    termination_a_id=int_a,
                    termination_b_type="dcim.interface",
                    termination_b_id=int_b,
                    type="cat5e",
                    status="connected"
                )