"""Constants for the PetTracer integration."""

DOMAIN = "pettracer"
CONF_API_KEY = "api_key"
CONF_EMAIL = "email"
CONF_PASSWORD = "password"
UPDATE_INTERVAL_SECONDS = 60

API_BASE_URL = "https://portal.pettracer.com/api"
API_WS_URL = "wss://pt.pettracer.com/sc"
API_ENDPOINT_LOGIN = "/user/login"
API_ENDPOINT_IMAGE = "/image/"
API_ENDPOINT_GET_CCS = "/map/getccs"
API_ENDPOINT_GET_HOMESTATIONS = "/user/gethomestations"
API_ENDPOINT_SET_MODE = "/map/setccmode"

# Modes mapping from collection.bru
# Mode-Live: 11, Mode-Fast: 1, Mode-Normal: 2, Mode-Slow: 3, 
# Mode-Slow-Plus: 7, Mode-Fast-Plus: 8, Mode-Normal-Plus: 14
MODE_MAP = {
    "Slow": 3,
    "Slow+": 7,
    "Normal": 2,
    "Normal+": 14,
    "Fast": 1,
    "Fast+": 8,
    "Live": 11,
}
MODE_MAP_INV = {v: k for k, v in MODE_MAP.items()}
