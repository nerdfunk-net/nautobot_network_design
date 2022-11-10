from pynautobot import api
import jinja2
import yaml
import os
import json


PYTHONWARNINGS="ignore:Unverified HTTPS request"
data_file = "../inventory/sites.yaml"
templateLoader = jinja2.FileSystemLoader(searchpath="/Users/marc/Programming/nerdfunk/nautobot_jinja_templates/")
templateEnv = jinja2.Environment(loader=templateLoader, trim_blocks=True)
TEMPLATE_FILE = "cisco_ios.j2"
template = templateEnv.get_template(TEMPLATE_FILE)

query = """
query ($device_id: ID!) {
  device(id: $device_id) {
    config_context
    hostname: name
    position
    serial
    primary_ip4 {
      id
      primary_ip4_for {
        id
        name
      }
    }
    tenant {
      name
    }
    tags {
      name
      slug
    }
    device_role {
      name
    }
    platform {
      name
      slug
      manufacturer {
        name
      }
      napalm_driver
    }
    site {
      name
      slug
      vlans {
        name
        vid
      }
      vlan_groups {
        id
      }
    }
    interfaces {
      name
      description
      enabled
      mac_address
      type
      mode
      ip_addresses {
        address
        role
        tags {
          slug
        }
      }
      connected_circuit_termination {
        circuit {
          cid
          commit_rate
          provider {
            name
          }
        }
      }
      tagged_vlans {
        name
      }
      untagged_vlan {
        name
        vid
      }
      cable {
        termination_a_type
        status {
          name
        }
        color
      }
      tags {
        id
        slug
      }
      lag {
        name
        enabled
      }
      member_interfaces {
        name
      }
    }
  }
}
"""

with open(data_file) as f: 
    data = yaml.safe_load(f.read())

nb = api(url="http://127.0.0.1:8000", token="18acb72f4f8df7d5b939492edaebc88a0992640d")
nb.http_session.verify = False

variables = {"device_id": "3f6ceddb-7596-4835-a54e-6b3a864be86a"}
data = nb.graphql.query(query=query, variables=variables).json
#print(json.dumps(data, indent=4))
print(template.render(data["data"]["device"]))