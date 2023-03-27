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
    'OIDC_CLAIM_sub': 'http://cilogon.org/serverA/users/9265706',
    'OIDC_CLAIM_idp_name': 'University of Wisconsin-Madison',
    'OIDC_CLAIM_eppn': 'clock@wisc.edu',
    'OIDC_CLAIM_cert_subject_dn': '/DC=org/DC=cilogon/C=US/O=University of Wisconsin-Madison/CN=CANNON LOCK E51992',
    'OIDC_CLAIM_eptid': 'https://login.wisc.edu/idp/shibboleth!https://cilogon.org/shibboleth!PiHGInAjgOQXOiT5K7ru3U5tOSE=',
    'OIDC_CLAIM_iss': 'https://cilogon.org',
    'OIDC_CLAIM_groups': 'CO:members:all,CO:COU:SOTERIA-Affiliates:members:all,CO:members:active,CO:COU:SOTERIA-Affiliates:members:active,CO:admins,ap7-login,ap1-login,path-facility-login',
    'OIDC_CLAIM_given_name': 'CANNON',
    'OIDC_CLAIM_acr': 'https://refeds.org/profile/mfa',
    'OIDC_CLAIM_aud': 'cilogon:/client_id/3ebf60531be150d38cb1fe8bfd584c2e',
    'OIDC_CLAIM_idp': 'https://login.wisc.edu/idp/shibboleth',
    'OIDC_CLAIM_affiliation': 'MEMBER@wisc.edu;EMPLOYEE@wisc.edu;AFFILIATE@wisc.edu',
    'OIDC_CLAIM_name': 'CANNON C LOCK',
    'OIDC_CLAIM_family_name': 'LOCK',
    'OIDC_CLAIM_email': 'CLOCK@WISC.EDU',
    'OIDC_CLAIM_jti': 'https://cilogon.org/oauth2/idToken/782392c322df8b05e412467c511b995a/1679500941325',
    'OIDC_CLAIM_nonce': 'RCoZXITAS4EI-dvqLFfVklA4k3e1P_f6relA3xhBS8E',
    'OIDC_CLAIM_auth_time': '1679497751',
    'OIDC_CLAIM_exp': '1679501841',
    'OIDC_CLAIM_iat': '1679500941',
    'OIDC_access_token': 'NB2HI4DTHIXS6Y3JNRXWO33OFZXXEZZPN5QXK5DIGIXWGNJXME4DCMRVMNSGKZRWHEYGCNZTMRQTEYLBGE2WMZRSGY3TGP3UPFYGKPLBMNRWK43TKRXWWZLOEZ2HGPJRGY3TSNJQGA4TIMJZGIZCM5TFOJZWS33OHV3DELRQEZWGSZTFORUW2ZJ5HEYDAMBQGA',
    'OIDC_access_token_expires': '1679501842'
}
