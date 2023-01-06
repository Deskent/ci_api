from config import site
from services.utils import represent_phone

DEFAULT_CONTEXT = {
    "company_email": site.COMPANY_EMAIL,
    "company_phone": f"tel:{site.COMPANY_PHONE}",
    "company_represent_phone": f"tel: {represent_phone(site.COMPANY_PHONE)}",
    "google_play_link": site.GOOGLE_PLAY_LINK,
    "app_store_link": site.APP_STORE_LINK,
    "vk_link": site.VK_LINK,
    "youtube_link": site.YOUTUBE_LINK,
}
