#!/usr/bin/env python

from django.utils.translation import ugettext_lazy as _

from horizon import tables

class InstancesTable(tables.DataTable):
    name = tables.Column("name", verbose_name=_("Name"))
    status = tables.Column("status", verbose_name=_("Status"))
    zone = tables.Column("availability zone", verbose_name=_("Availability zone"))
    image_name = tables.Column("image_name", verbose_name=_("Image name"))

    class Meta:
        name = "instances"
        verbose_name = _("Instances")
