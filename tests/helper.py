import datetime
import logging
import os

from lxml import etree


logger = logging.getLogger('tests')

now = datetime.datetime.now()
future = now + datetime.timedelta(days=1)

__path__ = os.path.dirname(os.path.realpath(__file__))

NAMESPACE_PREFIX = '{http://ws.plimus.com}'

SANDBOX_CLIENT_CONFIG = {
    'env': 'sandbox',
    'username': 'API_14127729102161320867365',
    'password': 'JustYoyo1',
    'default_store_id': '13945',
    'seller_id': '397608',
    'default_currency': 'GBP'
}

TEST_PRODUCT_SKU_ID = '2152476'


# This class is a dict that helps return encrypted keys at access time (since bluesnap
# encryption includes the timestamp in the payload).
# The encryption is done by the javascript code they provided (with modifications so that
# it can run without a browser)
class CardDict(dict):
    import execjs
    import os

    # Initialise Javascript VM within Python
    with open(os.path.join(os.path.dirname(__file__), 'bluesnap.js')) as f:
        _js_context = execjs.compile(f.read())

    _encrypted_key_prefix = 'encrypted_'

    def __encrypt(self, data):
        return self.__class__._js_context.call('window.bluesnap.encrypt', data)

    def __getitem__(self, key):
        try:
            return super(CardDict, self).__getitem__(key)
        except KeyError:
            if key.startswith(self._encrypted_key_prefix):
                key_without_prefix = key[len(self._encrypted_key_prefix):]
                value = self.__encrypt(self[key_without_prefix])
                self.__setitem__(key, value)
                return value
            raise


# Dummy cards taken from
# http://home.bluesnap.com/integrationguide/default.htm#WordManual/Working_with_Sandbox_Testing.htm
# http://avners.info/api/constant-values/test-credit-card-numbers
DUMMY_CARD_VISA = CardDict(
    card_type='VISA',
    card_number='4111111111111111',
    expiration_month=future.month,
    expiration_year=future.year,
    security_code='123',
)

DUMMY_CARD_DISCOVER = CardDict(
    card_type='MASTERCARD',
    card_number='60115564485789458',
    expiration_month=12,
    expiration_year=2018,
    security_code='411',
)
DUMMY_CARD_VISA__EXPIRED = CardDict(
    card_type='VISA',
    card_number='4917484589897107',
    expiration_month=4,
    expiration_year=2018,
    security_code='411',
)

DUMMY_CARD_VISA__INSUFFICIENT_FUNDS = CardDict(
    card_type='VISA',
    card_number='4917484589897107',
    expiration_month=5,
    expiration_year=2018,
    security_code='411',
)

DUMMY_CARD_VISA__INVALID_CARD_NUMBER = CardDict(
    card_type='VISA',
    card_number='4917484589897107',
    expiration_month=8,
    expiration_year=2018,
    security_code='411',
)

DUMMY_CARD_MASTERCARD = CardDict(
    card_type='MASTERCARD',
    card_number='5105105105105100',
    expiration_month=future.month,
    expiration_year=future.year,
    security_code='123',
)

DUMMY_CARD_AMEX = CardDict(
    card_type='AMEX',
    card_number='378282246310005',
    expiration_month=future.month,
    expiration_year=future.year,
    security_code='4111',
)

DUMMY_CARD_AMEX__AUTH_FAIL = CardDict(
    card_type='AMEX',
    card_number='378282246310005',
    expiration_month=5,
    expiration_year=2018,
    security_code='4111',
)

DUMMY_CARD_MASTERCARD_2 = CardDict(
    card_type='MASTERCARD',
    card_number='5425233430109903',
    expiration_month=4,
    expiration_year=2018,
    security_code='411',
)

DUMMY_CARDS = (
    ('Visa', DUMMY_CARD_VISA),
    ('MasterCard', DUMMY_CARD_MASTERCARD),
    ('MasterCard 2', DUMMY_CARD_MASTERCARD_2),
    ('American Express', DUMMY_CARD_AMEX),
    ('Discover', DUMMY_CARD_DISCOVER)
)


def configure_client():
    from bluesnap import client
    client.configure(logger=logger, **SANDBOX_CLIENT_CONFIG)


def get_xml_schema(file_name):
    return etree.XMLSchema(etree.parse(os.path.join(__path__, 'schemas', file_name)))
