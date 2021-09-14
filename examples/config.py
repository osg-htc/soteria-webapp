# Required Configuration
# ======================

## The email address to use for "contact us" links.

CONTACT_EMAIL = "someone@example.com"

## The base URL for SOTERIA's online documentation.

DOCS_URL = "https://soteria.example.com/documentation"

## Where a user should go to link their ORCID iD.

ORCID_ID_ENROLLMENT_URL = "https://registry.example.com/enroll/orcid"

## The Harbor instance's homepage and API base URLs.

HARBOR_HOMEPAGE_URL = "https://harbor.example.com"
HARBOR_API_URL = "https://harbor.example.com/api/v2.0"

## The username and password for the Harbor robot account to use.
## Environment variables of the same name will override the values set here.

HARBOR_ROBOT_USERNAME = "robot"
HARBOR_ROBOT_PASSWORD = "keep this a secret!"


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
