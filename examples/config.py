# fmt: off


# Required Configuration
# ======================

## The email address to use for "contact us" links.

CONTACT_EMAIL = "someone@example.com"

## The base URL for SOTERIA's online documentation.

DOCS_URL = "https://soteria.example.com/documentation"

## Where a user should go to enroll in SOTERIA.

SOTERIA_ENROLLMENT_FOR_EXISTING_ORG_ID_URL = "https://registry.example.com/enroll/existing"
SOTERIA_ENROLLMENT_FOR_NEW_ORG_ID_URL = "https://registry.example.com/enroll/new"

## Where a user should go to enroll as a researcher.

SOTERIA_RESEARCHER_ENROLLMENT_URL = "https://registry.example.com/enroll/researcher"

## Where a user should go to link their ORCID iD.

ORCID_ID_ENROLLMENT_URL = "https://registry.example.com/enroll/orcid"

## The Harbor instance's name, homepage URL, and API base URL.

HARBOR_NAME = "Example Harbor Instance"
HARBOR_HOMEPAGE_URL = "https://harbor.example.com"
HARBOR_API_URL = "https://harbor.example.com/api/v2.0"

## The username and password for the Harbor robot account to use.
## Environment variables of the same name will override the values set here.

HARBOR_ROBOT_USERNAME = "robot"
HARBOR_ROBOT_PASSWORD = "keep this a secret!"

## The LDAP server, username, and password to use.

LDAP_URL = "ldaps://ldap.registry.example.com"
LDAP_USERNAME = "uid=readonly_user"
LDAP_PASSWORD = "keep this a secret!"

## The name of the session cookie used by mod_auth_openidc.

MOD_AUTH_OPENIDC_SESSION_COOKIE_NAME = "mod_auth_openidc_session"


# Optional Configuration
# ======================

## Controls whether debugging functionality is enabled.

SOTERIA_DEBUG = False


# Configuration of Last Resort
# ============================

## The username and password for the Harbor instance's "admin" account.
## Environment variables of the same name will override the values set here.

HARBOR_ADMIN_USERNAME = "admin"
HARBOR_ADMIN_PASSWORD = "keep this a secret!"
