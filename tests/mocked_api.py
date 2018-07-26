from base64 import b64encode
from datetime import datetime
from functools import wraps
import re

import responses
import xmltodict

from . import helper
from bluesnap import client


# Memory store
shoppers = {}
orders = {}

mock_responses = {
    'card_expired': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<messages
    xmlns="http://ws.plimus.com">
    <message>
        <error-name>EXPIRED_CARD</error-name>
        <code>14002</code>
        <description>Order creation could not be completed because of payment processing failure: 430306 - The expiration date entered is invalid. Enter valid expiration date or try another card</description>
    </message>
</messages>''',
    'insufficient_funds': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<messages
    xmlns="http://ws.plimus.com">
    <message>
        <error-name>INSUFFICIENT_FUNDS</error-name>
        <code>14002</code>
        <description>Order creation could not be completed because of payment processing failure: 430360 - Insufficient funds. Please use another card or contact your bank for assistance</description>
    </message>
</messages>''',
    'invalid_card_number': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<messages
    xmlns="http://ws.plimus.com">
    <message>
        <error-name>INVALID_CARD_NUMBER</error-name>
        <code>14002</code>
        <description>Order creation could not be completed because of payment processing failure: 430330 - Invalid card number. Please check the number and try again, or use a different card</description>
    </message>
</messages>''',
    'incorrect_information': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<messages
    xmlns="http://ws.plimus.com">
    <message>
        <error-name>INCORRECT_INFORMATION</error-name>
        <code>14002</code>
        <description>Order creation could not be completed because of payment processing failure: 430285 - Authorization has failed for this transaction. Please try again or contact your bank for assistance</description>
    </message>
</messages>''',
    'order_failed__wrong_payment_details': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<messages
    xmlns="http://ws.plimus.com">
    <message>
        <code>10000</code>
        <description>The order failed because shopper payment details were incorrect or insufficient.</description>
    </message>
</messages>''',
    'order_failed__no_payment_method': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<messages
    xmlns="http://ws.plimus.com">
    <message>
        <code>15009</code>
        <description>Order creation failure, since no payment information was provided.</description>
    </message>
</messages>''',
}

def _generate_card_signature(card):
    return '%s/%d/%d' % (
        card['card_number'],
        int(card['expiration_month']),
        int(card['expiration_year']))

credit_card_number_to_error_responses = {
    _generate_card_signature(helper.DUMMY_CARD_VISA__EXPIRED):
        mock_responses['card_expired'],
    _generate_card_signature(helper.DUMMY_CARD_VISA__INSUFFICIENT_FUNDS):
        mock_responses['insufficient_funds'],
    _generate_card_signature(helper.DUMMY_CARD_VISA__INVALID_CARD_NUMBER):
        mock_responses['invalid_card_number'],
    _generate_card_signature(helper.DUMMY_CARD_AMEX__AUTH_FAIL):
        mock_responses['incorrect_information'],
}


def _add_callbacks():
    _client = client.default()

    def assert_request_authorised(func):
        """
        Wrapper that ensures that the request has the correct API credentials.
        """
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            passwordString = bytes('%s:%s' % (_client.username, _client.password), encoding='utf-8')
            authDigest = b64encode(passwordString).decode('utf-8')
            expectedAuthHeader = ('Basic %s' % authDigest)
            authHeader = request.headers['authorization']
            assert authHeader == expectedAuthHeader
            return func(request, *args, **kwargs)
        return wrapper

    def parse_xml_in_request_body(func):
        """
        Wrapper that parses the XML body and authorises the request.
        """
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            assert request.headers['content-type'] == 'application/xml'

            body = xmltodict.parse(request.body)
            return func(request, body, *args, **kwargs)
        return wrapper

    def and_assert_shopper_is_authorised(func):
        """
        Wrapper that asserts that a shopper is authorised to perform an action.
        """
        @wraps(func)
        def wrapper(request, body, *args, **kwargs):
            # Check client configuration
            shopper_info = body['shopper']['shopper-info']
            assert shopper_info['store-id'] == _client.default_store_id
            assert shopper_info['shopper-currency'] == _client.default_currency
            assert shopper_info['locale'] == _client.locale
            return func(request, body, *args, **kwargs)
        return wrapper

    @assert_request_authorised
    @parse_xml_in_request_body
    @and_assert_shopper_is_authorised
    def create_shopper_callback(request, body):
        shopper_info = body['shopper']['shopper-info']

        new_shopper_id = max(shoppers.keys() or [0]) + 1

        shopper_info['shopper-id'] = new_shopper_id
        shopper_info['username'] = 'username_%d' % new_shopper_id
        shopper_info['password'] = 'password_%d' % new_shopper_id
        shopper_info['shipping-contact-info'] = None
        shopper_info['invoice-contacts-info'] = {
            'invoice-contact-info': dict(
                default=True,
                **shopper_info['shopper-contact-info']
            ),
        }

        try:
            credit_card_info = shopper_info['payment-info'][
                'credit-cards-info']['credit-card-info']
            credit_card = credit_card_info['credit-card']

            card_number = None

            # Attempt to extract credit card number
            if 'card-number' in credit_card:
                card_number = credit_card['card-number']
            elif ('encrypted-card-number' in credit_card
                    and credit_card['encrypted-card-number'].startswith(
                        'encrypted_')):
                card_number = credit_card['encrypted-card-number'][10:]

            # Check if invalid card numbers were used
            card_signature = _generate_card_signature({
                'card_number': card_number,
                'expiration_month': credit_card['expiration-month'],
                'expiration_year': credit_card['expiration-year'],
            })
            if card_signature in credit_card_number_to_error_responses:
                return (400,
                        {'content-type': 'application/xml'},
                        credit_card_number_to_error_responses[card_signature])

            credit_card['card-last-four-digits'] = card_number[-4:]

            # Remove unexpected fields
            keys_to_keep = {'card-type', 'card-last-four-digits'}
            for key_to_discard in (set(credit_card.keys()) - keys_to_keep):
                del credit_card[key_to_discard]

            credit_card_info = [credit_card_info]

        except (KeyError, TypeError):
            credit_card_info = []

        shopper_info['payment-info'] = {
            'credit-cards-info': {
                'credit-card-info': credit_card_info,
            }
        }

        shoppers[new_shopper_id] = body

        headers = {
            'location': '%s/services/2/shoppers/%d' % (
                _client.endpoint_url, new_shopper_id),
        }
        return (201, headers, '')

    @assert_request_authorised
    def get_shopper_callback(request):
        try:
            raw_shopper_id = request.path_url.split('/')[-1]
            shopper_id = int(raw_shopper_id)
            shopper = shoppers[shopper_id]
        except (KeyError, ValueError):
            return (404, {},
                    'User: %s is not authorized to view shopper: %s.' % (
                        _client.username, raw_shopper_id))
        else:
            return (200, {}, xmltodict.unparse(shopper))

    @assert_request_authorised
    def put_shopper_callback(request):
        try:
            raw_shopper_id = request.path_url.split('/')[-1]
            shopper_id = int(raw_shopper_id)
            shopper = shoppers[shopper_id]
        except (KeyError, ValueError):
            return (404, {},
                    'User: %s is not authorized to view shopper: %s.' % (
                        _client.username, raw_shopper_id))
        else:
            body = xmltodict.parse(request.body)
            payment_info = body['shopper']['shopper-info']['payment-info']
            credit_card = payment_info['credit-cards-info'][
                'credit-card-info']['credit-card']

            card_number = None

            # Attempt to extract credit card number
            if 'card-number' in credit_card:
                card_number = credit_card['card-number']
            elif ('encrypted-card-number' in credit_card
                    and credit_card['encrypted-card-number'].startswith(
                        'encrypted_')):
                card_number = credit_card['encrypted-card-number'][10:]

            # Check if invalid card numbers were used
            card_signature = _generate_card_signature({
                'card_number': card_number,
                'expiration_month': credit_card['expiration-month'],
                'expiration_year': credit_card['expiration-year'],
            })
            if card_signature in credit_card_number_to_error_responses:
                return (400,
                        {'content-type': 'application/xml'},
                        credit_card_number_to_error_responses[card_signature])

            credit_card['card-last-four-digits'] = card_number[-4:]

            # Remove unexpected fields
            keys_to_keep = {'card-type', 'card-last-four-digits'}
            for key_to_discard in (set(credit_card.keys()) - keys_to_keep):
                del credit_card[key_to_discard]

            # Update shopper
            credit_card_info = shopper['shopper']['shopper-info'][
                'payment-info']['credit-cards-info']['credit-card-info']
            credit_card_info.append(
                payment_info['credit-cards-info']['credit-card-info'])

            return (204, {}, '')

    @assert_request_authorised
    @parse_xml_in_request_body
    def post_order_callback(request, body):
        new_order_id = max(orders.keys() or [0]) + 1
        order_date = datetime.now().strftime('%d-%b-%y')

        order = body['order']

        order['order-id'] = new_order_id

        # Ordering shopper section
        ordering_shopper = order['ordering-shopper']

        # Validate shopper id
        try:
            raw_shopper_id = ordering_shopper['shopper-id']
            shopper_id = int(raw_shopper_id)
            shopper_body = shoppers[shopper_id]
        except (KeyError, ValueError):
            return (403, {},
                    'User: %s is not authorized to place an order for '
                    'shopper: %s.' % (_client.username, raw_shopper_id))

        try:
            credit_card = ordering_shopper['credit-card']
        except KeyError:
            return (400, {'content-type': 'application/xml'},
                    mock_responses['order_failed__no_payment_method'])

        # Validate credit card selection
        card_found = False
        for credit_card_info in shopper_body['shopper']['shopper-info'][
                'payment-info']['credit-cards-info']['credit-card-info']:
            print(dict(credit_card_info['credit-card']), dict(credit_card))
            if dict(credit_card_info['credit-card']) == dict(credit_card):
                card_found = True
                break

        if not card_found:
            return (400, {'content-type': 'application/xml'},
                    mock_responses['order_failed__wrong_payment_details'])

        cart = order['cart']
        sku = cart['cart-item']['sku']
        assert sku['sku-id'] == helper.TEST_PRODUCT_SKU_ID
        sku_charge_price = sku['sku-charge-price']
        cart['charged-currency'] = sku_charge_price['currency']
        cart['cart-item']['item-sub-total'] = sku_charge_price['amount']
        cart['tax'] = '0.00'
        cart['tax-rate'] = '0'
        cart['total-cart-cost'] = sku_charge_price['amount']

        order['post-sale-info'] = {
            'invoices': {
                'invoice': {
                    'invoice-id': 'invoice_%d' % new_order_id,
                    'url': 'https://sandbox.bluesnap.com/jsp/show_invoice.jsp',
                    'financial-transactions': {
                        'financial-transaction': {
                            'status': 'Pending',
                            'date-due': order_date,
                            'date-created': order_date,
                            'amount': sku_charge_price['amount'],
                            'currency': sku_charge_price['currency'],
                            'soft-descriptor': 'BLS*%s' % order[
                                'soft-descriptor'],
                            'payment-method': 'Credit Card',
                            'target-balance': 'PLIMUS_ACCOUNT',
                            'credit-card': order['ordering-shopper'][
                                'credit-card'],
                            'paypal-transaction-data': None,
                            'skus': {
                                'sku': {
                                    'sku-id': sku['sku-id'],
                                },
                            },
                        }
                    }
                }
            }
        }

        orders[new_order_id] = body

        return (200, {'content-type': 'application/xml'},
                xmltodict.unparse(body))

    responses.add_callback(
        responses.POST,
        '%s/services/2/shoppers' % _client.endpoint_url,
        callback=create_shopper_callback)
    responses.add_callback(
        responses.GET,
        re.compile(r'%s/services/2/shoppers/\d+' % _client.endpoint_url),
        callback=get_shopper_callback)
    responses.add_callback(
        responses.PUT,
        re.compile(r'%s/services/2/shoppers/\d+' % _client.endpoint_url),
        callback=put_shopper_callback)
    responses.add_callback(
        responses.POST,
        '%s/services/2/orders' % _client.endpoint_url,
        callback=post_order_callback)


def activate(func):
    """Mock api activation wrapper"""
    @wraps(func)
    @responses.activate
    def wrapper(*args, **kwargs):
        _add_callbacks()
        return func(*args, **kwargs)
    return wrapper
