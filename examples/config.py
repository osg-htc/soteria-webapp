# Required Configuration
# ======================

# The Harbor instance's homepage.
HARBOR_WEBSITE = "https://harbor.example.com/"

# The Harbor instance's API's base URL.
HARBOR_API = "https://harbor.example.com/api/v2.0"

# The username and password of the robot registration to use with the API.
# Environment variables of the same name will override the values set here.
HARBOR_ROBOT_USERNAME = "robot"
HARBOR_ROBOT_PASSWORD = "password"


# Optional Configuration
# ======================

# Controls whether debugging functionality is enabled.
# The default is `False` (disabled). Set to `True` to enable.
REGISTRY_DEBUG = False


# Configuration of Last Resort
# ============================

# The username and password of an administrator for the Harbor instance.
# Environment variables of the same name will override the values set here.
HARBOR_ADMIN_USERNAME = "admin"
HARBOR_ADMIN_PASSWORD = "password"
