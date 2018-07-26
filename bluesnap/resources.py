import re
from urllib.parse import urlparse

import requests
from lxml import etree

from . import models
from .client import default as default_client


class Resource(object):
    def __init__(self, client=None):
        self.client = client or default_client()
        """:type : .client.Client"""

    def request(self, method, path, data=None):
        response, body = self.client.request(method, path, data)
        return response, body


class ShopperResource(Resource):
    shoppers_path = '/services/2/shoppers'
    shopper_path = shoppers_path + '/{shopper_id}'
    shopper_id_path_pattern = re.compile('{}/(\d+)'.format(shoppers_path))  # /services/2/shoppers/(\d+)

    def find_by_shopper_id(self, shopper_id):
        """
        :param shopper_id: BlueSnap shopper id
        :return: shopper dictionary
        """
        response, body = self.request('GET', self.shopper_path.format(shopper_id=shopper_id))
        return body['shopper']

    def find_by_seller_shopper_id(self, seller_shopper_id):
        """
        :param seller_shopper_id: Seller-specific shopper id
        :return: shopper dictionary
        """
        return self.find_by_shopper_id('{seller_shopper_id},{seller_id}'.format(
            seller_shopper_id=seller_shopper_id,
            seller_id=self.client.seller_id))

    def _create_shopper_element(self, contact_info, credit_card=None,
                                seller_shopper_id=None, client_ip=None):
        # noinspection PyPep8Naming
        E = self.client.E

        credit_cards_info = []
        if credit_card is not None:
            credit_cards_info.append(getattr(E, 'credit-card-info')(
                contact_info.to_xml('billing'),
                credit_card.to_xml()
            ))

        shopper_info = []
        if seller_shopper_id is not None:
            shopper_info.append(getattr(E, 'seller-shopper-id')(seller_shopper_id))

        return E.shopper(
            getattr(E, 'shopper-info')(
                getattr(E, 'store-id')(self.client.store_id),
                getattr(E, 'shopper-currency')(self.client.currency),
                E.locale(self.client.locale),
                contact_info.to_xml('shopper'),
                getattr(E, 'payment-info')(
                    getattr(E, 'credit-cards-info')(*credit_cards_info)
                ),
                *shopper_info
            ),
            models.WebInfo(ip=client_ip).to_xml()
        )

    def create(self, contact_info, credit_card=None, seller_shopper_id=None,
               client_ip=None):
        """
        Creates a new shopper
        :type contact_info: models.ContactInfo
        :type credit_card: models.AbstractCreditCard
        :param seller_shopper_id: Seller-specific shopper id
        :return: Returns the newly created BlueSnap shopper id
        """
        shopper_element = self._create_shopper_element(
            contact_info, credit_card, seller_shopper_id, client_ip=client_ip)
        data = etree.tostring(shopper_element)

        response, body = self.request('POST', self.shoppers_path, data=data)

        # Extract shopper id from location header
        new_shopper_url = urlparse(response.headers['location'])
        shopper_id = self.shopper_id_path_pattern.match(new_shopper_url.path).group(1)

        return shopper_id

    def update(self, shopper_id, contact_info, credit_card=None, client_ip=None):
        """
        Updates an existing shopper
        :param shopper_id: BlueSnap shopper id
        :type contact_info: models.ContactInfo
        :type credit_card: models.AbstractCreditCard
        :rtype: bool
        """
        shopper_element = self._create_shopper_element(
            contact_info, credit_card, client_ip=client_ip)
        data = etree.tostring(shopper_element)

        response, _ = self.request('PUT', self.shopper_path.format(shopper_id=shopper_id), data=data)
        return response.status_code == requests.codes.no_content


class OrderResource(Resource):
    path = '/services/2/orders'

    def create(self, shopper_id, sku_id, amount_in_pence, credit_card=None,
               description=None, client_ip=None):
        """
        :type shopper_id: int or str
        :type sku_id: int or str
        :type amount_in_pence: int
        :type credit_card: models.CreditCardSelection
        :param description: Order description
        :return:
        """
        # noinspection PyPep8Naming
        E = self.client.E

        amount = '{:.2f}'.format(amount_in_pence / 100.0)

        order = []
        if description is not None:
            order.append(getattr(E, 'soft-descriptor')(description))

        ordering_shopper = []
        if credit_card is not None:
            ordering_shopper.append(credit_card.to_xml())

        order_element = E.order(
            getattr(E, 'ordering-shopper')(
                getattr(E, 'shopper-id')(str(shopper_id)),
                models.WebInfo(ip=client_ip).to_xml(),
                *ordering_shopper
            ),
            E.cart(
                getattr(E, 'cart-item')(
                    E.sku(
                        getattr(E, 'sku-id')(str(sku_id)),
                        getattr(E, 'sku-charge-price')(
                            getattr(E, 'charge-type')('initial'),
                            E.amount(amount),
                            E.currency(self.client.currency)
                        )
                    ),
                    E.quantity('1'),
                ),
            ),
            getattr(E, 'expected-total-price')(
                E.amount(amount),
                E.currency(self.client.currency)
            ),
            *order
        )

        data = etree.tostring(order_element)
        response, body = self.request('POST', self.path, data=data)
        return body['order']


class PaymentFieldsTokenResource(Resource):
    '''
    If you would like to build your custom checkout flow using the API, but keep your PCI compliance requirements
    limited to the minimal SAQ-A level, BlueSnap’s Hosted Payment Fields are the ideal solution.

    Hosted Payment Fields are iframes that replace sensitive credit card input fields in your checkout page.
    When the shopper submits the checkout form, BlueSnap binds this payment data to a token. You can then easily
    process payments or save shopper details by including the token in your BlueSnap API requests.

    https://developers.bluesnap.com/v8976-Tools/docs/hosted-payment-fields

    '''
    path = '/services/2/payment-fields-tokens'

    def __init__(self):
        self._tokenId = None
        super(PaymentFieldsTokenResource, self).__init__()

    def create(self):
        '''
        Create a Hosted Payment Fields token by sending a server-to-server POST request to BlueSnap
        :return:
        '''
        # noinspection PyPep8Naming
        E = self.client.E

        response, body = self.request('POST', self.path)

        locationHeader = response.headers['Location']
        self._tokenId = locationHeader.split('/')[-1]
        return self._tokenId

    def tokenId(self):
        return self._tokenId


class VaultedShopperResource(Resource):
    path = '/services/2/vaulted-shoppers'

    def __init__(self):
        self._tokenId = None
        super(VaultedShopperResource, self).__init__()

    def retrieve(self, vaultedShopperId):
        '''
        The Retrieve Vaulted Shopper request retrieves all the saved details for the shopper associated with the
        vaultedShopperId you send in the request.

        https://developers.bluesnap.com/v8976-JSON/docs/retrieve-vaulted-shopper

        :param vaultedShopperId:
        :return:
        '''

        response, body = self.request('GET', '%s/%s' % (self.path, vaultedShopperId))

        return dict(body['vaulted-shopper'])

    def createFromPaymentFieldsToken(self, paymentFieldsTokenId, firstName, lastName):
        '''
        The Create Vaulted Shopper request enables you to store a shopper's details (including payment info) securely
        in BlueSnap. BlueSnap will provide a token (vaultedShopperId) for that saved shopper.

        This method creates it based on a Hosted Payment Fields token.

        You can then use the vaultedShopperId in order to complete payment transactions, improve the checkout
        experience for a returning shopper, and update the shopper's payment details.

        https://developers.bluesnap.com/v8976-JSON/docs/create-vaulted-shopper

        :param paymentFieldsTokenId:
        :param firstName:
        :param lastName:
        :return:
        '''

        data = {
            "paymentSources": {"creditCardInfo": [{"pfToken": paymentFieldsTokenId}]},
            "firstName": firstName,
            "lastName": lastName
        }

        response, body = self.request('POST', self.path, data=data)

        return body


class TransactionMetadata:
    '''
    The Payment API enables you to associate any data you wish to any type of transaction by using the flexible
    metadata property in your requests. This elegant approach to handling key business data allows you to create
    fields that append key information to a payment, such as product info, customer info, key dates, shipping and tax,
    or more. By using metadata, you can store the info that is most useful for your business and build the reporting
    needed.

    https://developers.bluesnap.com/v8976-JSON/docs/metadata

    Examples:
    [
        {
            "metaValue": 20,
            "metaKey": "stateTaxAmount",
            "metaDescription": "State Tax Amount"
        },
        {
            "metaValue": 20,
            "metaKey": "cityTaxAmount",
            "metaDescription": "City Tax Amount"
        },
        {
            "metaValue": 10,
            "metaKey": "shippingAmount",
            "metaDescription": "Shipping Amount"
        }
    ]
    '''

    def __init__(self, value, key, description):

        if value is None or value == "" or key is None or key == "" or description is None or description == "":
            raise ValueError(
                'Missing value %s, key %s or description %s.' % (value, key, description)
            )

        self.value = str(value)
        self.key = str(key)
        self.description = str(description)

        if len(self.value) > 500 or len(self.key) > 40 or len(self.description) > 40:
            raise ValueError('Maximum length in chars - value: 500, key: 40, description: 40')

    def toDict(self):

        return {
            "metaValue": self.value,
            "metaKey": self.key,
            "metaDescription": self.description
        }


class TransactionResource(Resource):
    path = '/services/2/transactions'

    def __init__(self):
        super(TransactionResource, self).__init__()

    def authCapture(
            self,
            vaultedShopperId,
            amount,
            currency,
            softDescriptor=None,
            transactionMetadataObjectList=()
    ):
        '''
        Auth Capture performs two actions via a single request:

            authorize: checks whether a credit card is valid and has the funds to complete a specific
                transaction (i.e. purchase)
            capture: submits the authorized transaction for settlement (i.e. payment by the shopper)

        https://developers.bluesnap.com/v8976-JSON/docs/auth-capture

        :param vaultedShopperId:
        :param amount:
        :param currency:
        :param softDescriptor:
        :param transactionMetadataObjectList:
        :return:
        '''

        return self._executeTransaction(
            cardTransactionType="AUTH_CAPTURE",
            vaultedShopperId=vaultedShopperId,
            amount=amount,
            currency=currency,
            softDescriptor=softDescriptor,
            transactionMetadataObjectList=transactionMetadataObjectList
        )

    def auth(
            self,
            vaultedShopperId,
            amount,
            currency,
            softDescriptor=None,
    ):
        '''
        Auth Only is a request to check whether a credit card is valid and has the funds to complete a specific
        transaction (i.e. purchase). It does not actually run the charge on the card, but does temporarily hold
        the funds aside. Note that each credit card company will only hold the authorization for a limited period
        (for example, 3-10 days, depending on the credit card scheme).

        Zero value auth for card validity checks:

        If you wish to check the validity of a card without authorizing any charge amount, simply enter 0 as the
        value for the amount property in this request.

        https://developers.bluesnap.com/v8976-JSON/docs/auth-only

        :param vaultedShopperId:
        :param amount:
        :param currency:
        :param softDescriptor:
        :return:
        '''

        return self._executeTransaction(
            cardTransactionType="AUTH_ONLY",
            vaultedShopperId=vaultedShopperId,
            amount=amount,
            currency=currency,
            softDescriptor=softDescriptor,
            transactionMetadataObjectList=[]
        )

    def retrieve(self, transactionId):

        '''
        Retrieve is a request that gets details about a past transaction, such as the transaction type, amount,
        cardholder or vaulted shopper, credit card, processing info, and so on.

        :param transactionId: transaction ID received in the response from BlueSnap
        :return:
        '''

        response, body = self.request('GET', '%s/%s' % (self.path, transactionId))

        return dict(body['card-transaction'])

    def _executeTransaction(
            self,
            cardTransactionType,
            vaultedShopperId,
            amount,
            currency,
            softDescriptor=None,
            transactionMetadataObjectList=[]
    ):
        '''
        Internal, perform an auth/capture operation.

        :param cardTransactionType:
        :param vaultedShopperId:
        :param amount:
        :param currency:
        :param softDescriptor:
        :param transactionMetadataObjectList:
        :return:
        '''

        data = {
            "vaultedShopperId": vaultedShopperId,
            "amount": amount,
            "currency": currency,
            "cardTransactionType": cardTransactionType,
        }

        if softDescriptor:
            data['softDescriptor'] = softDescriptor

        transactionMetaData = []
        for currentMetadataObject in transactionMetadataObjectList:
            transactionMetaData.append(currentMetadataObject.toDict())
        if transactionMetaData:
            data['transactionMetaData'] = {
                'metaData': transactionMetaData
            }

        response, body = self.request('POST', self.path, data=data)

        return body
