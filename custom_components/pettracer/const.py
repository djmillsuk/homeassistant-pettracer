"""Constants for the PetTracer integration."""

DOMAIN = "pettracer"
CONF_API_KEY = "api_key"
CONF_EMAIL = "email"
CONF_PASSWORD = "password"
UPDATE_INTERVAL_SECONDS = 180

API_BASE_URL = "https://portal.pettracer.com/api"
API_ENDPOINT_LOGIN = "/user/login"
API_ENDPOINT_IMAGE = "/image/"
API_ENDPOINT_GET_CCS = "/map/getccs"
API_ENDPOINT_SET_MODE = "/map/setccmode"

# Modes mapping from collection.bru
# Mode-Live: 11, Mode-Fast: 1, Mode-Normal: 2, Mode-Slow: 3, 
# Mode-Slow-Plus: 7, Mode-Fast-Plus: 8, Mode-Normal-Plus: 14
MODE_MAP = {
    "Fast": 1,
    "Normal": 2,
    "Slow": 3,
    "Slow+": 7,
    "Fast+": 8,
    "Live": 11,
    "Normal+": 14,
}
MODE_MAP_INV = {v: k for k, v in MODE_MAP.items()}
