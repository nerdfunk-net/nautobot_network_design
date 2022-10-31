from pynautobot import api
import yaml 
import os


PYTHONWARNINGS="ignore:Unverified HTTPS request"

data_file = "../inventory/sites.yaml"

with open(data_file) as f: 
    data = yaml.safe_load(f.read())

nb = api(url="http://127.0.0.1:8000", token="18acb72f4f8df7d5b939492edaebc88a0992640d")
nb.http_session.verify = False

# sites: 
for site in data["sites"]: 
    print(f"Creating or Updating Site {site['name']}")
    nb_data = nb.dcim.sites.get(slug=site["slug"])
    if not nb_data: 
        nb_data = nb.dcim.sites.create(
            name=site["name"],
            slug=site["slug"],
            status=site["status"],
        )
    nb_site = nb.dcim.sites.get(slug=site["slug"])
    if "asn" in site.keys():        
        nb_site.asn = site["asn"]
    if "time_zone" in site.keys():    
        nb_site.time_zone = site["time_zone"]
    if "description" in site.keys():    
        nb_site.description = site["description"]
    if "physical_address" in site.keys():
        nb_site.physical_address = site["physical_address"]
    if "shipping_address" in site.keys():
        nb_site.shipping_address = site["shipping_address"]
    if "latitude" in site.keys():
        nb_site.latitude = site["latitude"]
    if "longitude" in site.keys():
        nb_site.longitude = site["longitude"]
    if "contact_name" in site.keys():
        nb_site.contact_name = site["contact_name"]
    if "contact_phone" in site.keys():
        nb_site.contact_phone = site["contact_phone"]
    if "contact_email" in site.keys():
        nb_site.contact_email = site["contact_email"]
    if "comments" in site.keys():
        nb_site.comments = site["comments"]
    nb_site.save()
