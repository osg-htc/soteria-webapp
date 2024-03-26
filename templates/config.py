# fmt: off


# ======================
# Required Configuration
# ======================

#
# The email address to use for "contact us" links.
#
CONTACT_EMAIL = "someone@example.com"

#
# The directory to use for long-term storage of data.
# An environment variable of the same name will override the value set here.
#
DATA_DIR = "/data"

#
# The base URL for SOTERIA's online documentation.
#
DOCS_URL = "https://soteria.example.com/documentation"

#
# The API key for Freshdesk.
# An environment variable of the same name will override the value set here.
#
FRESHDESK_API_KEY = "keep this a secret!"

#
# The Harbor instance's name, homepage URL, and API base URL.
#
HARBOR_NAME = "Example Harbor Instance"
HARBOR_HOMEPAGE_URL = "https://harbor.example.com"
HARBOR_API_URL = f"{HARBOR_HOMEPAGE_URL}/api/v2.0"

#
# The username and password for the Harbor instance's "admin" account.
# Environment variables of the same name will override the values set here.
#
HARBOR_ADMIN_USERNAME = "admin"
HARBOR_ADMIN_PASSWORD = "keep this a secret!"

#
# The LDAP instance to query for users' attributes.
# Environment variables of the same name will override the values set here.
#
LDAP_URL = "ldaps://ldap.registry.example.com"
LDAP_USERNAME = "uid=readonly_user,o=soteria,dc=example,dc=com"
LDAP_PASSWORD = "keep this a secret!"
LDAP_BASE_DN = "o=soteria,dc=example,dc=com"

#
# The name of the session cookie used by mod_auth_openidc.
#
MOD_AUTH_OPENIDC_SESSION_COOKIE_NAME = "mod_auth_openidc_session"

#
# Where a user should go to link their ORCID iD.
#
ORCID_ID_ENROLLMENT_URL = "https://registry.example.com/enroll/orcid"

#
# The COmanage instance's name, homepage URL, CO ID, and API base URL.
#
REGISTRY_NAME = "Example COmanage Registry"
REGISTRY_HOMEPAGE_URL = "https://registry.example.com"
REGISTRY_CO_ID = 0
REGISTRY_API_URL = f"{REGISTRY_HOMEPAGE_URL}/registry"

#
# The username and password for the COmanage instance's API user.
# Environment variables of the same name will override the values set here.
#
REGISTRY_API_USERNAME = "co_0.soteria"
REGISTRY_API_PASSWORD = "keep this a secret!"

#
# A random string that may be used for security related purposes.
# An environment variable of the same name will override the value set here.
#
SECRET_KEY = "keep this a secret!"

#
# Where a user should go to enroll in the SOTERIA COU.
#
SOTERIA_ENROLLMENT_FOR_EXISTING_ORG_ID_URL = "https://registry.example.com/enroll/existing"
SOTERIA_ENROLLMENT_FOR_NEW_ORG_ID_URL = "https://registry.example.com/enroll/new"

#
# The SOTERIA instance's homepage URL and API base URL.
#
SOTERIA_HOMEPAGE_URL = "https://soteria.example.com"
SOTERIA_API_URL = f"{SOTERIA_HOMEPAGE_URL}/api/v1"

#
# Bearer token that must be presented to invoke the Harbor webhook.
# An environment variable of the same name will override the value set here.
#
WEBHOOKS_HARBOR_BEARER_TOKEN = "keep this a secret!"


# ======================
# Optional Configuration
# ======================

#
# Controls whether debugging functionality is enabled.
#
SOTERIA_DEBUG = False

#
# The version string to display to users.
#
SOTERIA_VERSION = "0.0.0+template"
