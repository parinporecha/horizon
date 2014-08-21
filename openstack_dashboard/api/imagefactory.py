from __future__ import absolute_import

import logging
import urlparse
import json
import requests
import xml.etree.ElementTree as ET

from openstack_dashboard.api.base import url_for

LOG = logging.getLogger(__name__)

class FactoryImage:
    def __init__(self, data):
        self.id = data['id']
        self.glance_id = data['identifier_on_provider']
        self.target_image = data['target_image']
        self.status = data['status']
        self.progress = data['percent_complete']

        if data['template']:
            try:
                print data['template']
                template = ET.fromstring(data['template'])
                self.template = template.find("./name").text
                self.name = template.find("./name").text
                self.os_name = template.find("./os/name").text + " v" + template.find("./os/version").text
                self.os_version = template.find("./os/version").text
                self.arch = template.find("./os/arch").text
                self.description = template.find("./description").text
            except:
                LOG.error("Unable to parse Template")

def imagefactory_request(request, path, body=None, method=None):
    LOG.debug('Looking up Imagefactory entrypoint URL')
    #imagefactory_url = urlparse.urlparse(url_for(request, "image-build"))

    IMAGEFACTORY_URL = "https://lxbst0518.cern.ch:8075/imagefactory"
    CERN_CERTIFICATE = '/etc/pki/tls/certs/CERN-bundle.pem'

    #imagefactory_request = urllib2.Request(IMAGEFACTORY_URL + path)
    #imagefactory_request = requests.post(IMAGEFACTORY_URL + path, data = payload, verify=CERN_CERTIFICATE)
    #imagefactory_request.add_header('Content-type', 'application/json')
    #imagefactory_request.add_header('Accept', 'application/json')
    #if body:
      #imagefactory_request.add_data(json.dumps(body))

    if method:
        request.get_method = lambda: method

    #return requests.post(IMAGEFACTORY_URL + path, data = body, verify=CERN_CERTIFICATE)
    return requests.post(IMAGEFACTORY_URL + path, data = body, verify = CERN_CERTIFICATE)

def image_create(request, template, kickstart, properties = ""):
    LOG.debug('Creating Image Create request for Imagefactory')
    glance_url = urlparse.urlparse(url_for(request, "image"))
    print "glance URL = " + str(glance_url.geturl())
    keystone_url = urlparse.urlparse(url_for(request, "identity"))
    print "keystone URL = " + str(keystone_url.geturl())

    TENANT_NAME = "Personal pporecha"
    PASS = "ca74c72d8dea4da0"
    AUTH_URL = "https://openstack.cern.ch:5000/v2.0"
    #AUTH_URL = "http://128.142.243.224:5000/v2.0/"
    GLANCE_HOST = "openstack"
    GLANCE_PORT = "9292"

    parameters_json = json.dumps({"install_script" : kickstart})
    if properties == "":
        properties = json.dumps({})
    provider = """{\"glance-host\":\"""" + GLANCE_HOST + """\",
                             \"glance-port\": """ + GLANCE_PORT + """,
                             \"properties\": """ + properties + """}"""

    body = {"template":template,
                                 "target":"openstack-kvm",
                                 # We must set this as a string rather than a dict
                                 "provider": provider,
                                "parameters": parameters_json,
                                 "credentials":"""<provider_credentials>
                                                      <openstack_credentials>
                                                          <tenant>""" + TENANT_NAME + """</tenant>
                                                          <strategy>keystone</strategy>
                                                          <auth_url>""" + AUTH_URL + """</auth_url>
                                                          <token>""" + str(request.user.token.id) + """</token>
                                                      </openstack_credentials>
                                                  </provider_credentials>"""}
    return imagefactory_request(request, "/provider_images", body)

def image_get(request, image_id):
    response = json.loads(imagefactory_request(request, "/provider_images/" + image_id).read)
    return FactoryImage(response)

def image_delete(request, image_id):
    response = json.loads(imagefactory_request(request, "/provider_images/" + image_id).read)
    return FactoryImage(response)

def image_list(request):
    images = []
    list = json.loads(imagefactory_request(request, "/provider_images").read())
    for i in list["provider_images"]:
        response = imagefactory_request(request, "/provider_images/" + i['provider_image']['id']).read()
        image = FactoryImage(json.loads(response)['provider_image'])
        images.append(image)
    return images
