# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.LIMS
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE and CONTRIBUTING.

import unittest2 as unittest

from plone.testing import z2

from plone.app.testing import setRoles
from plone.app.testing import applyProfile
from plone.app.testing import TEST_USER_ID
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import FunctionalTesting
from plone.app.testing import login
from plone.app.testing import logout

from bika.lims.testing import BASE_TESTING


class SimpleTestLayer(PloneSandboxLayer):
    """Setup Plone with installed AddOn only
    """
    defaultBases = (BASE_TESTING, PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        super(SimpleTestLayer, self).setUpZope(app, configurationContext)

        # Load ZCML
        import bika.lims
        import senaite.lims
        import senaite.impress
        import senaite.core.listing

        self.loadZCML(package=bika.lims)
        self.loadZCML(package=senaite.lims)
        self.loadZCML(package=senaite.impress)
        self.loadZCML(package=senaite.core.listing)

        # Install product and call its initialize() function
        z2.installProduct(app, "senaite.lims")

    def setUpPloneSite(self, portal):
        super(SimpleTestLayer, self).setUpPloneSite(portal)

        # Apply Setup Profile (portal_quickinstaller)
        applyProfile(portal, "senaite.lims:default")

        login(portal.aq_parent, SITE_OWNER_NAME)

        # Add some test users
        ROLES = ["LabManager", "LabClerk", "Analyst"]
        for role in ROLES:

            for user_nr in range(2):
                username = "test_%s_%s" % (role.lower(), user_nr)
                try:
                    member = portal.portal_registration.addMember(
                        username,
                        username,
                        properties={
                            "username": username,
                            "email": username + "@example.com",
                            "fullname": username})
                    # Add user to all specified groups
                    group_id = role + "s"
                    group = portal.portal_groups.getGroupById(group_id)
                    if group:
                        group.addMember(username)
                    # Add user to all specified roles
                    member._addRole(role)
                except ValueError:
                    pass  # user exists

        logout()

    def tearDownZope(self, app):
        # Uninstall product
        z2.uninstallProduct(app, "senaite.lims")


###
# Use for simple tests (w/o contents)
###
SIMPLE_FIXTURE = SimpleTestLayer()
SIMPLE_TESTING = FunctionalTesting(
    bases=(SIMPLE_FIXTURE, ),
    name="senaite.lims:SimpleTesting"
)


class SimpleTestCase(unittest.TestCase):
    layer = SIMPLE_TESTING

    def setUp(self):
        super(SimpleTestCase, self).setUp()

        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.request["ACTUAL_URL"] = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["LabManager", "Manager"])
