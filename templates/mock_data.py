# ===================================
# Mock Data for an Authenticated User
# ===================================

#
# Values set under `MOCK_OIDC_CLAIM` will override environment variables of
# the same name. For example, setting `OIDC_CLAIM_iss` and `OIDC_CLAIM_sub`
# will cause the application to behave as if mod_auth_openidc authenticated
# the user.
#
# This is primarily useful when testing the web application locally, where
# it is unlikely to have an externally reachable hostname that can be used
# to configure an OIDC client and its callback.
#
MOCK_OIDC_CLAIM = {
    "OIDC_CLAIM_iss": "https://cilogon.org",
    "OIDC_CLAIM_sub": "http://cilogon.org/<id>",
}