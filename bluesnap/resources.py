import re
from abc import abstractmethod
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


# ------------------
# XML API
# ------------------

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


# ------------------
# JSON API
# ------------------

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


class DictableObject:

    def __init__(self):
        pass

    @abstractmethod
    def toDict(self):
        raise NotImplementedError("Must implement this.")

    def _setToDictIfHasValue(self, resultDict: dict, key: str):
        '''
        Set a value to a dict if it has a value
        :param resultDict:
        :param key:
        :return:
        '''

        if hasattr(self, key) and getattr(self, key, None):
            resultDict[key] = getattr(self, key)

    def _setToDictIfHasValues(self, resultDict: dict, keys: list):
        for key in keys:
            self._setToDictIfHasValue(resultDict, key)


class ShippingContactInfo(DictableObject):

    def __init__(
            self,
            firstName: str,
            lastName: str,
            address1: str = None,
            address2: str = None,
            city: str = None,
            state: str = None,
            country: str = None,
            zip: str = None,
    ):
        '''
        Details of a Shipping Contact Info.

        More information here:
        https://developers.bluesnap.com/v8976-JSON/docs/shipping-contact-info

        :param firstName: Shopper's first name. Maximum 100 characters.
        :param lastName: Shopper's last name. Maximum 100 characters.
        :param address1: Shopper's address line 1. Maximum 100 characters.
        :param address2: Shopper's address line 2. Maximum 100 characters.
        :param city: Shopper's city. Between 2-42 characters.
        :param state: Based on https://developers.bluesnap.com/docs/state-and-province-codes
        :param country: Based on https://developers.bluesnap.com/docs/country-codes
        :param zip: Shopper's ZIP code. Maximum 20 characters.
        '''

        # Call base class init
        super(ShippingContactInfo, self).__init__()

        if not firstName or not lastName or not address1 or not city or not zip or not country:
            raise ValueError('firstName, lastName, address1, city, zip and country are '
                             'required are required.')

        self.firstName = firstName
        self.lastName = lastName
        self.address1 = address1
        self.address2 = address2
        self.city = city
        self.state = state
        self.country = country
        self.zip = zip

    def toDict(self) -> dict:
        result = {
            "firstName": self.firstName,
            "lastName": self.lastName,
            "address1": self.address1,
            "city": self.city,
            "zip": self.zip,
            "country": self.country,
        }

        self._setToDictIfHasValues(
            resultDict=result,
            keys=[
                "address2",
                "state",
            ]
        )

        return result



class CardHolderInfo(DictableObject):

    '''
    A Vaulted Shopper Info object, containing some of the fields defined here:
    https://developers.bluesnap.com/v8976-JSON/docs/vaulted-shopper
    '''

    def __init__(
            self,
            firstName: str,
            lastName: str,
            personalIdentificationNumber: str = None,
            merchantShopperId: str = None,
            address: str = None,
            address2: str = None,
            city: str = None,
            state: str = None,
            country: str = None,
            zip: str = None,
            email: str = None,
            phone: str = None,
    ):
        '''
        Details of a Card Holder.

        More information here:
        CardHolderInfo

        :param firstName: Shopper's first name. Maximum 100 characters.
        :param lastName: Shopper's last name. Maximum 100 characters.
        :param personalIdentificationNumber: The shopper's local personal identification number.
            These are the ID types per country:
            Argentina - DNI (length 7-11 chars)
            Brazil - CPF/CNPJ (length 11-14 chras)
            Chile - RUN (length 8-9 chars)
            Colombia - CC (length 6-10 chars)
            Mexico - CURP/RFC (length 10-18 chars)
        :param merchantShopperId: A merchant's ID for a specific shopper, up to 50 characters.
        :param address: Shopper's address line 1. Maximum 100 characters.
        :param address2: Shopper's address line 2. Maximum 100 characters.
        :param city: Shopper's city. Between 2-42 characters.
        :param state: Based on https://developers.bluesnap.com/docs/state-and-province-codes
        :param country: Based on https://developers.bluesnap.com/docs/country-codes
        :param zip: Shopper's ZIP code. Maximum 20 characters.
        :param email: Shopper's email address. Between 3-100 characters.
        :param phone: Shopper's phone number. Between 2-36 characters.
        '''

        # Call base class init
        super(CardHolderInfo, self).__init__()

        if not firstName or not lastName:
            raise ValueError('firstName and lastName are required.')

        self.firstName = firstName
        self.lastName = lastName
        self.personalIdentificationNumber = personalIdentificationNumber
        self.merchantShopperId = merchantShopperId
        self.address = address
        self.address2 = address2
        self.city = city
        self.state = state
        self.country = country
        self.zip = zip
        self.email = email
        self.phone = phone

    def toDict(self) -> dict:
        result = {
            "firstName": self.firstName,
            "lastName": self.lastName,
        }

        self._setToDictIfHasValues(
            resultDict=result,
            keys=[
                "personalIdentificationNumber",
                "merchantShopperId",
                "address",
                "address2",
                "city",
                "state",
                "country",
                "zip",
                "email",
                "phone",
            ]
        )

        return result

class BillingContactInfo(DictableObject):

    def __init__(
            self,
            firstName: str,
            lastName: str,
            personalIdentificationNumber: str = None,
            address1: str = None,
            address2: str = None,
            city: str = None,
            state: str = None,
            country: str = None,
            zip: str = None,
    ):
        '''
        Details of a Billing Contact Info.

        More information here:
        https://developers.bluesnap.com/v8976-JSON/docs/billing-contact-info

        :param firstName: Shopper's first name. Maximum 100 characters.
        :param lastName: Shopper's last name. Maximum 100 characters.
        :param personalIdentificationNumber: The shopper's local personal identification number.
            These are the ID types per country:
            Argentina - DNI (length 7-11 chars)
            Brazil - CPF/CNPJ (length 11-14 chras)
            Chile - RUN (length 8-9 chars)
            Colombia - CC (length 6-10 chars)
            Mexico - CURP/RFC (length 10-18 chars)
        :param address1: Shopper's address line 1. Maximum 100 characters.
        :param address2: Shopper's address line 2. Maximum 100 characters.
        :param city: Shopper's city. Between 2-42 characters.
        :param state: Based on https://developers.bluesnap.com/docs/state-and-province-codes
        :param country: Based on https://developers.bluesnap.com/docs/country-codes
        :param zip: Shopper's ZIP code. Maximum 20 characters.
        '''

        # Call base class init
        super(BillingContactInfo, self).__init__()

        if not firstName or not lastName or not address1 or not city or not zip or not country or \
                not personalIdentificationNumber:
            raise ValueError('firstName, lastName, address1, city, zip, country and personalIdentificationNumber are '
                             'required are required.')

        self.firstName = firstName
        self.lastName = lastName
        self.personalIdentificationNumber = personalIdentificationNumber
        self.address1 = address1
        self.address2 = address2
        self.city = city
        self.state = state
        self.country = country
        self.zip = zip

    def toDict(self) -> dict:
        result = {
            "firstName": self.firstName,
            "lastName": self.lastName,
            "address1": self.address1,
            "city": self.city,
            "zip": self.zip,
            "country": self.country,
            "personalIdentificationNumber": self.personalIdentificationNumber,
        }

        self._setToDictIfHasValues(
            resultDict=result,
            keys=[
                "address2",
                "state",
            ]
        )

        return result


class TransactionFraudInfo(DictableObject):

    def __init__(
            self,
            fraudSessionId: str,
            shopperIpAddress: str = None,
            company: str = None,
            shippingContactInfo: ShippingContactInfo = None,
            # TODO: enterpriseSiteId
            # TODO: enterpriseUdfs
    ):
        '''
        Transaction Fraud Info class.

        More information here:
        https://developers.bluesnap.com/v8976-JSON/docs/transaction-fraud-info

        :param fraudSessionId: Unique ID of the shopper whose device fingerprint information was collected on
            the checkout page. The Fraud Session ID should contain up to 32 alpha-numeric characters only.
            https://developers.bluesnap.com/docs/fraud-prevention#section-device-data-checks
        :param shopperIpAddress: Shopper's IP address. Should be a valid IPv4 or IPv6 address.
        :param company: Shopper's company name. Maximum 100 characters.
        :param shippingContactInfo: ShippingContactInfo object
        '''

        # Call base class init
        super(TransactionFraudInfo, self).__init__()

        if not fraudSessionId:
            raise ValueError('fraudSessionId is required.')

        self.fraudSessionId = fraudSessionId
        self.shopperIpAddress = shopperIpAddress
        self.company = company
        self.shippingContactInfo = shippingContactInfo

    def toDict(self) -> dict:
        result = {
            "fraudSessionId": self.fraudSessionId,
        }

        self._setToDictIfHasValues(
            resultDict=result,
            keys=[
                "shopperIpAddress",
                "company",
            ]
        )

        if self.shippingContactInfo:
            result["shippingContactInfo"] = self.shippingContactInfo.toDict()

        return result


class VaultedShopperInfo(DictableObject):
    '''
    A Vaulted Shopper Info object, containing some of the fields defined here:
    https://developers.bluesnap.com/v8976-JSON/docs/vaulted-shopper
    '''

    def __init__(
            self,
            firstName: str,
            lastName: str,
            companyName: str = None,
            personalIdentificationNumber: str = None,
            shopperCurrency: str = 'USD',
            softDescriptor: str = None,
            descriptorPhoneNumber: str = None,
            merchantShopperId: str = None,
            address: str = None,
            address2: str = None,
            city: str = None,
            state: str = None,
            country: str = None,
            zip: str = None,
            email: str = None,
            phone: str = None,
            shippingContactInfo: ShippingContactInfo = None,
            transactionFraudInfo: TransactionFraudInfo = None,
    ):
        '''
        Details of a Vaulted Shopper.

        More information here:
        https://developers.bluesnap.com/v8976-JSON/docs/create-vaulted-shopper#section-request-content

        :param firstName: Shopper's first name. Maximum 100 characters.
        :param lastName: Shopper's last name. Maximum 100 characters.
        :param companyName: Shopper's company name. Maximum 100 characters.
        :param personalIdentificationNumber: The shopper's local personal identification number.
            These are the ID types per country:
            Argentina - DNI (length 7-11 chars)
            Brazil - CPF/CNPJ (length 11-14 chras)
            Chile - RUN (length 8-9 chars)
            Colombia - CC (length 6-10 chars)
            Mexico - CURP/RFC (length 10-18 chars)
        :param shopperCurrency: Shopper's currency. Based on https://developers.bluesnap.com/docs/currency-codes
        :param softDescriptor: Description that may appear on the shopper's bank statement when BlueSnap validates
            the card. Maximum 20 characters.
            More info here: https://developers.bluesnap.com/docs/statement-descriptor
        :param descriptorPhoneNumber: Merchant's support phone number that may appear on the shopper's bank statement
            when BlueSnap validates the card. Maximum 20 characters.
            More info here: https://developers.bluesnap.com/docs/statement-descriptor
        :param merchantShopperId: A merchant's ID for a specific shopper, up to 50 characters.
        :param address: Shopper's address line 1. Maximum 100 characters.
        :param address2: Shopper's address line 2. Maximum 100 characters.
        :param city: Shopper's city. Between 2-42 characters.
        :param state: Based on https://developers.bluesnap.com/docs/state-and-province-codes
        :param country: Based on https://developers.bluesnap.com/docs/country-codes
        :param zip: Shopper's ZIP code. Maximum 20 characters.
        :param email: Shopper's email address. Between 3-100 characters.
        :param phone: Shopper's phone number. Between 2-36 characters.
        :param shippingContactInfo: ShippingContactInfo object
        :param transactionFraudInfo: TransactionFraudInfo
        # TODO: walletId
        '''

        # Call base class init
        super(VaultedShopperInfo, self).__init__()

        if not firstName or not lastName:
            raise ValueError('firstName and lastName are required.')

        self.firstName = firstName
        self.lastName = lastName
        self.companyName = companyName
        self.personalIdentificationNumber = personalIdentificationNumber
        self.shopperCurrency = shopperCurrency
        self.softDescriptor = softDescriptor
        self.descriptorPhoneNumber = descriptorPhoneNumber
        self.merchantShopperId = merchantShopperId
        self.address = address
        self.address2 = address2
        self.city = city
        self.state = state
        self.country = country
        self.zip = zip
        self.email = email
        self.phone = phone
        self.shippingContactInfo = shippingContactInfo
        self.transactionFraudInfo = transactionFraudInfo

    def toDict(self) -> dict:
        result = {
            "firstName": self.firstName,
            "lastName": self.lastName,
        }

        self._setToDictIfHasValues(
            resultDict=result,
            keys=[
                "companyName",
                "personalIdentificationNumber",
                "shopperCurrency",
                "softDescriptor",
                "descriptorPhoneNumber",
                "merchantShopperId",
                "address",
                "address2",
                "city",
                "state",
                "country",
                "zip",
                "email",
                "phone",
                "fraudSessionId",
            ]
        )

        if self.shippingContactInfo:
            result["shippingContactInfo"] = self.shippingContactInfo.toDict()

        if self.transactionFraudInfo:
            result["transactionFraudInfo"] = self.transactionFraudInfo.toDict()

        return result


class Level3DataItem(DictableObject):

    '''
    Contains Level 2/3 data properties for each item purchased
    https://developers.bluesnap.com/v8976-JSON/docs/level3dataitems

    While all level3DataItems properties are optional in the request, each data level (such as Level 2 and Level 3)
    has specific requirements. See the Level 2/3 Data guide for complete details.
    https://developers.bluesnap.com/docs/level-23-data
    '''

    def __init__(
            self,
            lineItemTotal: str = None,
            commodityCode: str = None,
            description: str = None,
            discountAmount: str = None,
            discountIndicator: str = None,
            grossNetIndicator: str = None,
            productCode: str = None,
            itemQuantity: str = None,
            taxAmount: str = None,
            taxRate: str = None,
            taxType: str = None,
            unitCost: str = None,
            unitOfMeasure: str = None,
    ):
        '''

        :param lineItemTotal: Total item amount.
        :param commodityCode: Commodity code used to classify item.
        :param description: Item description
        :param discountAmount: Discount amount applied to item
        :param discountIndicator: Indicates whether item amount is discounted. 'Y' or 'N'
        :param grossNetIndicator: Indicates whether tax is included in item amount. 'Y' or 'N'
        :param productCode: Product code for item
        :param itemQuantity: Item quantity purchased
        :param taxAmount: Tax amount for item
        :param taxRate: Tax rate applied to item
        :param taxType: Type of tax being applied
        :param unitCost: Unit cost
        :param unitOfMeasure: Unit of measure
        '''

        # Call base class init
        super(Level3DataItem, self).__init__()

        self.lineItemTotal = lineItemTotal
        self.commodityCode = commodityCode
        self.description = description
        self.discountAmount = discountAmount
        self.discountIndicator = discountIndicator
        self.grossNetIndicator = grossNetIndicator
        self.productCode = productCode
        self.itemQuantity = itemQuantity
        self.taxAmount = taxAmount
        self.taxRate = taxRate
        self.taxType = taxType
        self.unitCost = unitCost
        self.unitOfMeasure = unitOfMeasure

    def toDict(self) -> dict:
        result = {
        }

        self._setToDictIfHasValues(
            resultDict=result,
            keys=[
                "lineItemTotal",
                "commodityCode",
                "description",
                "discountAmount",
                "discountIndicator",
                "grossNetIndicator",
                "productCode",
                "itemQuantity",
                "taxAmount",
                "taxRate",
                "taxType",
                "unitCost",
                "unitOfMeasure",
            ]
        )

        return result

class Level3Data(DictableObject):

    '''
    Contains Level 2/3 data properties for the transaction

    While all level3Data properties are optional in the request, each data level (such as Level 2 and Level 3) has
    specific requirements. See the Level 2/3 Data guide for complete details.
    https://developers.bluesnap.com/docs/level-23-data
    '''

    def __init__(
            self,
            customerReferenceNumber: str = None,
            salesTaxAmount: str = None,
            freightAmount: str = None,
            dutyAmount: str = None,
            destinationZipCode: str = None,
            destinationCountryCode: str = None,
            shipFromZipCode: str = None,
            discountAmount: str = None,
            taxAmount: str = None,
            taxRate: str = None,
            level3DataItems: list = [],
    ):

        # Call base class init
        super(Level3Data, self).__init__()

        self.customerReferenceNumber = customerReferenceNumber
        self.salesTaxAmount          = salesTaxAmount
        self.freightAmount           = freightAmount
        self.dutyAmount              = dutyAmount
        self.destinationZipCode      = destinationZipCode
        self.destinationCountryCode  = destinationCountryCode
        self.shipFromZipCode         = shipFromZipCode
        self.discountAmount          = discountAmount
        self.taxAmount               = taxAmount
        self.taxRate                 = taxRate
        self.level3DataItems         = level3DataItems

    def toDict(self) -> dict:
        result = {
        }

        self._setToDictIfHasValues(
            resultDict=result,
            keys=[
                "customerReferenceNumber",
                "salesTaxAmount",
                "freightAmount",
                "dutyAmount",
                "destinationZipCode",
                "destinationCountryCode",
                "shipFromZipCode",
                "discountAmount",
                "taxAmount",
                "taxRate",
            ]
        )

        if self.level3DataItems:
            level3DataItems = []

            for dataItem in self.level3DataItems:
                level3DataItems.append(
                    dataItem.toDict()
                )
            result["level3DataItems"] = level3DataItems

        return result


class VaultedShopperResource(Resource):
    path = '/services/2/vaulted-shoppers'

    def __init__(self):
        self._tokenId = None
        super(VaultedShopperResource, self).__init__()

    def retrieve(self, vaultedShopperId: str) -> dict:
        '''
        The Retrieve Vaulted Shopper request retrieves all the saved details for the shopper associated with the
        vaultedShopperId you send in the request.

        https://developers.bluesnap.com/v8976-JSON/docs/retrieve-vaulted-shopper

        :param vaultedShopperId:
        :return:
        '''

        response, body = self.request('GET', '%s/%s' % (self.path, vaultedShopperId))

        return dict(body['vaulted-shopper'])

    def createFromPaymentFieldsToken(
            self,
            vaultedShopperInfo: VaultedShopperInfo,
            paymentFieldsTokenId: str,
            billingContactInfo: BillingContactInfo,
            # TODO: creditCard
            # TODO: ecpInfo
            # TODO: sepaDirectDebitInfo
    ) -> dict:
        '''
        The Create Vaulted Shopper request enables you to store a shopper's details (including payment info) securely
        in BlueSnap. BlueSnap will provide a token (vaultedShopperId) for that saved shopper.

        This method creates it based on a Hosted Payment Fields token.

        You can then use the vaultedShopperId in order to complete payment transactions, improve the checkout
        experience for a returning shopper, and update the shopper's payment details.

        https://developers.bluesnap.com/v8976-JSON/docs/create-vaulted-shopper

        :param vaultedShopperInfo: This is used for invoices, and to show information about the user in BlueSnap itself
        :param paymentFieldsTokenId: Required if using Hosted Payment Fields. Do not include credit-card resource if
            using this token
        :param billingContactInfo: Contains billing contact information. This is connected to the payment method and
            will NOT be used for invoicing, etc.
        :return:
        '''

        data = {
            "paymentSources": {
                "creditCardInfo": [
                    {
                        "pfToken": paymentFieldsTokenId,
                        'billingContactInfo': billingContactInfo.toDict()
                    }
                ]
            },
        }
        data.update(vaultedShopperInfo.toDict())

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

    def __init__(self, value: str, key: str, description: str):

        if value is None or value == "" or key is None or key == "" or description is None or description == "":
            raise ValueError(
                'Missing value %s, key %s or description %s.' % (value, key, description)
            )

        self.value = str(value)
        self.key = str(key)
        self.description = str(description)

        if len(self.value) > 500 or len(self.key) > 40 or len(self.description) > 40:
            raise ValueError('Maximum length in chars - value: 500, key: 40, description: 40')

    def toDict(self) -> dict:

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
            amount: str,
            currency: str,

            vaultedShopperId: str = None,
            pfToken: str = None,
            cardHolderInfo: CardHolderInfo = None,

            merchantTransactionId: str = None,
            softDescriptor: str = None,
            descriptorPhoneNumber: str = None,
            level3Data: Level3Data = None,

            transactionMetadataObjectList: list = ()
    ) -> dict:
        '''
        Auth Capture performs two actions via a single request:

            authorize: checks whether a credit card is valid and has the funds to complete a specific
                transaction (i.e. purchase)
            capture: submits the authorized transaction for settlement (i.e. payment by the shopper)

        https://developers.bluesnap.com/v8976-JSON/docs/auth-capture

        :param amount:
        :param currency:
        :param vaultedShopperId:
        :param pfToken:
        :param cardHolderInfo:
        :param merchantTransactionId: Merchant's unique ID for a new transaction. Between 1-50 characters.
        :param softDescriptor: Description of the transaction, which appears on the shopper's credit card statement.
            Maximum 20 characters. Overrides merchant default value.
        :param descriptorPhoneNumber: Merchant's support phone number that will appear on the shopper's credit card
            statement. Maximum 20 characters. Overrides merchant default value.
        :param level3Data: Contains Level 2/3 data properties for the transaction
        :param transactionMetadataObjectList:
        :return:
        '''

        return self._executeTransaction(
            cardTransactionType="AUTH_CAPTURE",
            amount=amount,
            currency=currency,
            vaultedShopperId=vaultedShopperId,
            pfToken=pfToken,
            cardHolderInfo=cardHolderInfo,
            merchantTransactionId=merchantTransactionId,
            softDescriptor=softDescriptor,
            descriptorPhoneNumber=descriptorPhoneNumber,
            level3Data=level3Data,
            transactionMetadataObjectList=transactionMetadataObjectList
        )

    def retrieve(self, transactionId: str) -> dict:

        '''
        Retrieve is a request that gets details about a past transaction, such as the transaction type, amount,
        cardholder or vaulted shopper, credit card, processing info, and so on.

        :param transactionId: transaction ID received in the response from BlueSnap
        :return:
        '''

        response, body = self.request('GET', '%s/%s' % (self.path, transactionId))

        return dict(body['card-transaction'])

    def auth(
            self,
            amount: str,
            currency: str,
            vaultedShopperId: str = None,
            pfToken: str = None,
            cardHolderInfo: CardHolderInfo = None,
    ) -> dict:
        '''
        Auth Only is a request to check whether a credit card is valid and has the funds to complete a specific
        transaction (i.e. purchase). It does not actually run the charge on the card, but does temporarily hold
        the funds aside. Note that each credit card company will only hold the authorization for a limited period
        (for example, 3-10 days, depending on the credit card scheme).

        Zero value auth for card validity checks:

        If you wish to check the validity of a card without authorizing any charge amount, simply enter 0 as the
        value for the amount property in this request.

        https://developers.bluesnap.com/v8976-JSON/docs/auth-only

        :param amount:
        :param currency:
        :param vaultedShopperId:
        :param pfToken:
        :param cardHolderInfo:
        :return:
        '''

        return self._executeTransaction(
            cardTransactionType="AUTH_ONLY",
            amount=amount,
            currency=currency,
            vaultedShopperId=vaultedShopperId,
            pfToken=pfToken,
            cardHolderInfo=cardHolderInfo,
        )

    def _executeTransaction(
            self,
            cardTransactionType: str,
            amount: str,
            currency: str,
            vaultedShopperId: str = None,
            pfToken: str = None,
            cardHolderInfo: CardHolderInfo = None,
            merchantTransactionId: str = None,
            softDescriptor: str = None,
            descriptorPhoneNumber: str = None,
            level3Data: Level3Data=None,
            transactionMetadataObjectList: list = (),
    ) -> dict:
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
            "amount": amount,
            "currency": currency,
            "cardTransactionType": cardTransactionType,
        }

        if not pfToken and not vaultedShopperId:
            raise RuntimeError("Must supply either vaultedShopperId or pfToken.")

        if vaultedShopperId:
            pfToken = None

        if vaultedShopperId:
            data["vaultedShopperId"] = vaultedShopperId

        if pfToken:
            data["pfToken"] = pfToken

        if cardHolderInfo:
            data['cardHolderInfo'] = cardHolderInfo.toDict()

        if merchantTransactionId:
            data['merchantTransactionId'] = merchantTransactionId

        if softDescriptor:
            data['softDescriptor'] = softDescriptor

        if descriptorPhoneNumber:
            data['descriptorPhoneNumber'] = softDescriptor

        if level3Data:
            data['level3Data'] = level3Data.toDict()

        transactionMetaData = []
        for currentMetadataObject in transactionMetadataObjectList:
            transactionMetaData.append(currentMetadataObject.toDict())
        if transactionMetaData:
            data['transactionMetaData'] = {
                'metaData': transactionMetaData
            }

        response, body = self.request('POST', self.path, data=data)

        return body
