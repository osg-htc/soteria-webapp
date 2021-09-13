# Required Configuration
# ======================

## The email address to use for "contact us" links.

CONTACT_EMAIL = "someone@example.com"

## Where a user should go to link their ORCID iD.

ORCID_ID_ENROLLMENT_PAGE = "https://registry.example.com/enroll/orcid"

## The Harbor instance's homepage and API base URL.

HARBOR_HOMEPAGE = "https://harbor.example.com/"
HARBOR_API = "https://harbor.example.com/api/v2.0"

## The username and password for the robot account to use.
## Environment variables of the same name will override the values set here.

HARBOR_ROBOT_USERNAME = "robot"
HARBOR_ROBOT_PASSWORD = "keep this a secret!"

## Docs URL

DOCS_URL = "https://cannonlock.github.io/Soteria-Docs"

# Optional Configuration
# ======================

## Controls whether debugging functionality is enabled.

REGISTRY_DEBUG = False


# Configuration of Last Resort
# ============================

## The username and password for the Harbor instance's "admin" account.
## Environment variables of the same name will override the values set here.

HARBOR_ADMIN_USERNAME = "admin"
HARBOR_ADMIN_PASSWORD = "keep this a secret!"
