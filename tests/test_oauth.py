"""
This module tests oauth
"""
from unittest.mock import MagicMock

from superset_patchup.oauth import CustomSecurityManager


class TestOauth:
    """
    Class to test the oauth module
    """

    def test_get_oauth_redirect_url_when_not_set(self):
        """
        Test that when custom_redirect_url key is not set in the provider
        None is returned
        """
        appbuilder = MagicMock()
        csm = CustomSecurityManager(appbuilder=appbuilder)
        redirect_url = csm.get_oauth_redirect_url(provider="onadata")
        assert redirect_url is None

    def test_get_oauth_redirect_url_when_set(self):
        """
        Test that when custom_redirect_url key is set in the provider
        it returns the right value
        """
        appbuilder = MagicMock()
        CustomSecurityManager.oauth_providers = [{
            "name":
            "onadata",
            "custom_redirect_url":
            "http://google.com"
        }]
        csm = CustomSecurityManager(appbuilder=appbuilder)
        redirect_url = csm.get_oauth_redirect_url(provider="onadata")
        assert redirect_url == "http://google.com"

    def test_oauth_user_info_onadata_provider(self):
        """
        Test that we get the right user information
        with the onadata provider
        """
        # Sample data returned from endpoints
        user_endpoint = {"username": "testauth", "name": "test"}
        profiles_endpoint = {
            "id": 58863,
            "is_org": False,
            "first_name": "test",
            "name": "test auth",
            "last_name": "auth",
            "email": "testauth@ona.io",
        }

        # Expected result
        result_info = {
            "name": "test auth",
            "email": "testauth@ona.io",
            "id": 58863,
            "username": "testauth",
            "first_name": "test",
            "last_name": "auth",
        }

        appbuilder = MagicMock()
        user_mock = MagicMock()
        user_mock.data = user_endpoint
        profile_mock = MagicMock()
        profile_mock.data = profiles_endpoint
        appbuilder.sm.oauth_remotes["onadata"].get = MagicMock(
            side_effect=[user_mock, profile_mock])
        csm = CustomSecurityManager(appbuilder=appbuilder)
        user_info = csm.oauth_user_info(provider="onadata")
        assert user_info == result_info

    def test_oauth_user_info_openlmis_provider(self):
        """
        Test that we get the right user information
        with the openlmis provider
        """
        # Data returned from userContactDetails endpoint
        contacts_endpoint = {
            "emailDetails": {
                "email": "testauth@openlmis.org"
            }
        }

        # Data returned from users endpoint in openlmis
        users_endpoint = {
            "username": "testauth",
            "firstName": "test",
            "lastName": "auth",
            "active": True,
            "id": "a337ec45-31a0-4f2b-9b2e-a105c4b669bb",
        }

        # Result expected
        result_info = {
            "name": "testauth",
            "email": "testauth@openlmis.org",
            "id": "a337ec45-31a0-4f2b-9b2e-a105c4b669bb",
            "username": "testauth",
            "first_name": "test",
            "last_name": "auth",
        }

        appbuilder = MagicMock()
        reference_user = MagicMock()
        reference_user.data = {
            "referenceDataUserId": "a337ec45-31a0-4f2b-9b2e-a105c4b669bb"
        }

        user_data = MagicMock()
        user_data.data = users_endpoint

        user_email = MagicMock()
        user_email.data = contacts_endpoint

        appbuilder.sm.oauth_remotes["openlmis"].get = MagicMock(
            side_effect=[reference_user, user_data, user_email])
        csm = CustomSecurityManager(appbuilder=appbuilder)
        csm.oauth_tokengetter = MagicMock(
            return_value=["a337ec45-31a0-4f2b-9b2e-a105c4b669bb"])
        user_info = csm.oauth_user_info(provider="openlmis")
        assert user_info == result_info

    def test_oauth_user_info_no_provider(self):
        """
        Test that when no provider is provided
        None is returned
        """
        appbuilder = MagicMock()
        csm = CustomSecurityManager(appbuilder=appbuilder)
        user_info = csm.oauth_user_info(provider=None)
        assert user_info is None