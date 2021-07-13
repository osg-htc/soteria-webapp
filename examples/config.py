# Required Configuration
# ======================

## The email address to use for "contact us" links.

CONTACT_EMAIL = "someone@example.com"

## The Harbor instance's homepage and API base URL.

HARBOR_HOMEPAGE = "https://harbor.example.com/"
HARBOR_API = "https://harbor.example.com/api/v2.0"

## The username and password of the robot account to use with the API.
## Environment variables of the same name will override the values set here.

HARBOR_ROBOT_USERNAME = "robot"
HARBOR_ROBOT_PASSWORD = "password"


# Optional Configuration
# ======================

## Controls whether debugging functionality is enabled.

REGISTRY_DEBUG = False


# Configuration of Last Resort
# ============================

## The username and password of the administrator of the Harbor instance.
## Environment variables of the same name will override the values set here.

HARBOR_ADMIN_USERNAME = "admin"
HARBOR_ADMIN_PASSWORD = "password"
