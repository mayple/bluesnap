from unittest import TestCase

import responses

from mock import MagicMock

from bluesnap import client, exceptions
from bluesnap.models import ContactInfo, PlainCreditCard, CreditCardSelection, EncryptedCreditCard
from bluesnap.resources import OrderResource, ShopperResource
from . import helper
from . import mocked_api


helper.configure_client()


class ShopperTestCase(TestCase):
    maxDiff = None

    @property
    def encrypted_credit_card(self):
        if not hasattr(self, '_encrypted_credit_card'):
            self._encrypted_credit_card = EncryptedCreditCard(
                card_type=helper.DUMMY_CARD_VISA['card_type'],
                expiration_month=helper.DUMMY_CARD_VISA['expiration_month'],
                expiration_year=helper.DUMMY_CARD_VISA['expiration_year'],
                encrypted_card_number='encrypted_%s' % helper.DUMMY_CARD_VISA['card_number'],
                encrypted_security_code=helper.DUMMY_CARD_VISA['encrypted_security_code']
            )
        return self._encrypted_credit_card

    @property
    def encrypted_second_credit_card(self):
        if not hasattr(self, '_encrypted_second_credit_card'):
            self._encrypted_second_credit_card = EncryptedCreditCard(
                card_type=helper.DUMMY_CARD_MASTERCARD['card_type'],
                expiration_month=helper.DUMMY_CARD_MASTERCARD['expiration_month'],
                expiration_year=helper.DUMMY_CARD_MASTERCARD['expiration_year'],
                encrypted_card_number='encrypted_%s' % helper.DUMMY_CARD_MASTERCARD['card_number'],
                encrypted_security_code=helper.DUMMY_CARD_MASTERCARD['encrypted_security_code']
            )
        return self._encrypted_second_credit_card

    @property
    def encrypted_third_credit_card(self):
        if not hasattr(self, '_encrypted_third_credit_card'):
            self._encrypted_third_credit_card = EncryptedCreditCard(
                card_type=helper.DUMMY_CARD_AMEX['card_type'],
                expiration_month=helper.DUMMY_CARD_AMEX['expiration_month'],
                expiration_year=helper.DUMMY_CARD_AMEX['expiration_year'],
                encrypted_card_number='encrypted_%s' % helper.DUMMY_CARD_AMEX['card_number'],
                encrypted_security_code=helper.DUMMY_CARD_AMEX['encrypted_security_code']
            )
        return self._encrypted_third_credit_card

    def setUp(self):
        self.contact_info = ContactInfo(
            first_name='John',
            last_name='Doe',
            email='test@justyoyo.com',
            zip_='SW5',
            country='gb',
            phone='07777777777')

        self.credit_card = PlainCreditCard(
            card_type=helper.DUMMY_CARD_VISA['card_type'],
            expiration_month=helper.DUMMY_CARD_VISA['expiration_month'],
            expiration_year=helper.DUMMY_CARD_VISA['expiration_year'],
            card_number=helper.DUMMY_CARD_VISA['card_number'],
            security_code=helper.DUMMY_CARD_VISA['security_code'])
        self.second_credit_card = PlainCreditCard(
            card_type=helper.DUMMY_CARD_MASTERCARD['card_type'],
            expiration_month=helper.DUMMY_CARD_MASTERCARD['expiration_month'],
            expiration_year=helper.DUMMY_CARD_MASTERCARD['expiration_year'],
            card_number=helper.DUMMY_CARD_MASTERCARD['card_number'],
            security_code=helper.DUMMY_CARD_MASTERCARD['security_code'])
        self.third_credit_card = PlainCreditCard(
            card_type=helper.DUMMY_CARD_AMEX['card_type'],
            expiration_month=helper.DUMMY_CARD_AMEX['expiration_month'],
            expiration_year=helper.DUMMY_CARD_AMEX['expiration_year'],
            card_number=helper.DUMMY_CARD_AMEX['card_number'],
            security_code=helper.DUMMY_CARD_AMEX['security_code'])

    @mocked_api.activate
    def test_create_with_valid_contact_info_returning_id(self):
        shopper = ShopperResource()
        shopper_id = shopper.create(
            contact_info=self.contact_info)

        self.assertIsNotNone(shopper_id)

    @mocked_api.activate
    def test_create_with_valid_contact_info_returning_object(self):
        shopper = ShopperResource()

        shopper_id = shopper.create(
            contact_info=self.contact_info)
        shopper_obj = shopper.find_by_shopper_id(shopper_id)

        self.assertIsInstance(shopper_obj, dict)
        shopper_info = shopper_obj['shopper-info']
        shopper_contact_info = shopper_info['shopper-contact-info']
        self.assertEqual(shopper_contact_info['first-name'], self.contact_info.first_name)
        self.assertEqual(shopper_contact_info['last-name'], self.contact_info.last_name)
        self.assertEqual(shopper_info['store-id'], shopper.client.default_store_id)
        self.assertIsNone(shopper_info['payment-info']['credit-cards-info'])

    @mocked_api.activate
    def test_create_with_valid_contact_info_and_credit_card(self):
        shopper = ShopperResource()

        shopper_id = shopper.create(
            contact_info=self.contact_info,
            credit_card=self.credit_card)
        shopper_obj = shopper.find_by_shopper_id(shopper_id)

        self.assertIsInstance(shopper_obj, dict)
        shopper_info = shopper_obj['shopper-info']
        shopper_contact_info = shopper_info['shopper-contact-info']
        self.assertEqual(shopper_contact_info['first-name'], self.contact_info.first_name)
        self.assertEqual(shopper_contact_info['last-name'], self.contact_info.last_name)
        self.assertEqual(shopper_info['store-id'], shopper.client.default_store_id)

    @mocked_api.activate
    def test_create_with_valid_contact_info_and_encrypted_credit_card(self):
        shopper = ShopperResource()

        shopper_id = shopper.create(
            contact_info=self.contact_info,
            credit_card=self.encrypted_credit_card)
        shopper_obj = shopper.find_by_shopper_id(shopper_id)

        self.assertIsInstance(shopper_obj, dict)
        shopper_info = shopper_obj['shopper-info']
        shopper_contact_info = shopper_info['shopper-contact-info']
        self.assertEqual(shopper_contact_info['first-name'], self.contact_info.first_name)
        self.assertEqual(shopper_contact_info['last-name'], self.contact_info.last_name)
        self.assertEqual(shopper_info['store-id'], shopper.client.default_store_id)

    @responses.activate
    def test_create_with_invalid_parameters(self):
        error_msg = (
            'Seller 397608 encountered a problem creating a new shopper due '
            'to incorrect input.')
        responses.add(
            responses.POST,
            '%s/services/2/shoppers' % client.default().endpoint_url,
            status=400,
            content_type='application/xml',
            body='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<messages xmlns="http://ws.plimus.com">
<message>
    <description>%s</description>
</message>
<message>
    <code>10001</code>
    <description>'Email Address' is not a valid email address.</description>
    <invalid-property>
        <name>shopperInfo.shopperContactInfo.email</name>
        <message-value/>
    </invalid-property>
</message>
<message>
    <code>10001</code>
    <description>Field 'Email Address' is required.</description>
    <invalid-property>
        <name>shopperInfo.shopperContactInfo.email</name>
        <message-value/>
    </invalid-property>
</message>
<message>
    <code>10001</code>
    <description>Field 'Email Address' is required.</description>
    <invalid-property>
        <name>shopperInfo.invoiceContactsInfo.invoiceContactInfo.email</name>
        <message-value/>
    </invalid-property>
</message>
<message>
    <code>10001</code>
    <description>'Email Address' is not a valid email address.</description>
    <invalid-property>
        <name>shopperInfo.invoiceContactsInfo.invoiceContactInfo.email</name>
        <message-value/>
    </invalid-property>
</message>
</messages>''' % error_msg)

        shopper = ShopperResource()

        with self.assertRaises(exceptions.APIError) as cm:
            shopper.create(
                contact_info=ContactInfo(email=''),
                credit_card=self.credit_card
            )

        self.assertEqual(cm.exception.status_code, 400)
        self.assertEqual(cm.exception.description, 'None')
        self.assertGreater(len(cm.exception.messages), 1)
        self.assertEqual(cm.exception.messages[0]['description'], error_msg)

    @responses.activate
    def test_create_with_invalid_parameters_encrypted(self):
        error_msg = 'Invalid encrypted input'

        responses.add(
            responses.POST,
            '%s/services/2/shoppers' % client.default().endpoint_url,
            status=400,
            content_type='application/xml',
            body='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<messages xmlns="http://ws.plimus.com">
<message>
    <code>19002</code>
    <description>%s</description>
</message>
</messages>''' % error_msg)

        shopper = ShopperResource()

        with self.assertRaises(exceptions.APIError) as cm:
            shopper.create(
                contact_info=ContactInfo(email=''),
                credit_card=self.encrypted_credit_card
            )
        self.assertEqual(cm.exception.status_code, 400)
        self.assertEqual(cm.exception.description, error_msg)

    @mocked_api.activate
    def test_find_by_shopper_id(self):
        shopper = ShopperResource()
        shopper_id = shopper.create(
            contact_info=self.contact_info)

        self.assertIsNotNone(shopper_id)

        # find_by_shopper_id
        shopper_obj = shopper.find_by_shopper_id(shopper_id)

        self.assertIsInstance(shopper_obj, dict)
        shopper_contact_info = shopper_obj['shopper-info']['shopper-contact-info']
        self.assertEqual(shopper_contact_info['first-name'], self.contact_info.first_name)
        self.assertEqual(shopper_contact_info['last-name'], self.contact_info.last_name)
        self.assertEqual(shopper_obj['shopper-info']['store-id'], shopper.client.default_store_id)

    @mocked_api.activate
    def test_find_by_seller_shopper_id(self):
        seller_id = 'seller_id'
        seller_shopper_id = 'seller_shopper_id'

        # Set up
        shopper = ShopperResource()
        shopper.client.seller_id = seller_id
        shopper.find_by_shopper_id = MagicMock()

        # find_by_seller_shopper_id
        shopper.find_by_seller_shopper_id(seller_shopper_id)

        shopper.find_by_shopper_id.assert_called_once_with(
            '{seller_shopper_id},{seller_id}'.format(
                seller_shopper_id=seller_shopper_id,
                seller_id=seller_id))

    @responses.activate
    def test_find_by_bogus_shopper_id_and_seller_shopper_id_raises_exception(self):
        bogus_shopper_id = 'bogus_shopper_id'
        bogus_seller_shopper_id = 'bogus_seller_shopper_id'

        responses.add(
            responses.GET,
            '%s/services/2/shoppers/%s' % (
                client.default().endpoint_url, bogus_shopper_id),
            status=403,
            content_type='application/xml',
            body='User: %s is not authorized to view shopper: %s.' % (
                client.default().username, bogus_shopper_id)
        )
        responses.add(
            responses.GET,
            '%s/services/2/shoppers/%s,%s' % (
                client.default().endpoint_url,
                bogus_seller_shopper_id,
                client.default().seller_id),
            status=403,
            content_type='application/xml',
            body='User: %s is not authorized to view seller shopper: %s.' % (
                client.default().username, bogus_seller_shopper_id)
        )

        with self.assertRaises(exceptions.APIError) as cm:
            ShopperResource().find_by_shopper_id(bogus_shopper_id)
            self.assertTrue(False, 'APIError not raised')
        self.assertEqual(cm.exception.status_code, 403)
        self.assertRegexpMatches(
            cm.exception.description,
            'User: %s is not authorized to view shopper: %s.' % (
                client.default().username, bogus_shopper_id))

        with self.assertRaises(exceptions.APIError) as cm:
            ShopperResource().find_by_seller_shopper_id(bogus_seller_shopper_id)
            self.assertTrue(False, 'APIError not raised')
        self.assertEqual(cm.exception.status_code, 403)
        self.assertRegexpMatches(
            cm.exception.description,
            'User: %s is not authorized to view seller shopper: %s.' % (
                client.default().username, bogus_seller_shopper_id))

    @responses.activate
    def test_update_fails_with_invalid_shopper_id(self):
        shopper_id = '1'
        error_msg = 'User: %s is not authorized to update shopper: %s.' % (
            client.default().username, shopper_id)

        responses.add(
            responses.PUT,
            '%s/services/2/shoppers/%s' % (
                client.default().endpoint_url, shopper_id),
            status=403,
            content_type='application/xml',
            body=error_msg)

        shopper = ShopperResource()

        with self.assertRaises(exceptions.APIError) as cm:
            shopper.update(shopper_id, contact_info=self.contact_info)
        self.assertEqual(cm.exception.status_code, 403)
        self.assertEqual(cm.exception.description, error_msg)

    @mocked_api.activate
    def test_add_credit_card(self):
        # Create a shopper, ensuring no credit card info was added
        shopper = ShopperResource()
        shopper_id = shopper.create(
            contact_info=self.contact_info)
        shopper_obj = shopper.find_by_shopper_id(shopper_id)
        self.assertIsNone(shopper_obj['shopper-info']['payment-info']['credit-cards-info'])

        # Add first credit card
        update_successful = shopper.update(
            shopper_id=shopper_id,
            contact_info=self.contact_info,
            credit_card=self.credit_card)
        self.assertTrue(update_successful)

        shopper_obj = shopper.find_by_shopper_id(shopper_id)
        credit_card_info = shopper_obj['shopper-info']['payment-info']['credit-cards-info']['credit-card-info']
        self.assertIsInstance(credit_card_info['credit-card'], dict)
        self.assertEqual(credit_card_info['credit-card']['card-last-four-digits'], self.credit_card.card_number[-4:])
        self.assertEqual(credit_card_info['credit-card']['card-type'], self.credit_card.card_type)

        # Add second credit card
        update_successful = shopper.update(
            shopper_id=shopper_id,
            contact_info=self.contact_info,
            credit_card=self.second_credit_card)
        self.assertTrue(update_successful)

        shopper_obj = shopper.find_by_shopper_id(shopper_id)
        credit_cards_info = shopper_obj['shopper-info']['payment-info']['credit-cards-info']['credit-card-info']
        self.assertIsInstance(credit_cards_info, list)
        self.assertEqual(len(credit_cards_info), 2)

        # The order of the credit cards is not known, so we sort the items before comparing.
        cards = [ dict(c['credit-card']) for c in  credit_cards_info ]
        self.assertEqual(
            cards,
            [{'card-last-four-digits': self.credit_card.card_number[-4:],
              'card-type': self.credit_card.card_type},
             {'card-last-four-digits': self.second_credit_card.card_number[-4:],
              'card-type': self.second_credit_card.card_type}])

        # Add third credit card
        update_successful = shopper.update(
            shopper_id=shopper_id,
            contact_info=self.contact_info,
            credit_card=self.third_credit_card)
        self.assertTrue(update_successful)

        shopper_obj = shopper.find_by_shopper_id(shopper_id)
        credit_cards_info = shopper_obj['shopper-info']['payment-info']['credit-cards-info']['credit-card-info']
        self.assertIsInstance(credit_cards_info, list)
        self.assertEqual(len(credit_cards_info), 3)

        # Last added credit card displays first
        cards = [dict(c['credit-card']) for c in credit_cards_info]
        self.assertEqual(
            cards,
            [{'card-last-four-digits': self.credit_card.card_number[-4:],
              'card-type': self.credit_card.card_type},
             {'card-last-four-digits': self.second_credit_card.card_number[-4:],
              'card-type': self.second_credit_card.card_type},
             {'card-last-four-digits': self.third_credit_card.card_number[-4:],
              'card-type': self.third_credit_card.card_type}])

    @mocked_api.activate
    def test_add_encrypted_credit_card(self):
        # Create a shopper, ensuring no credit card info was added
        shopper = ShopperResource()
        shopper_id = shopper.create(
            contact_info=self.contact_info)
        shopper_obj = shopper.find_by_shopper_id(shopper_id)
        self.assertIsNone(shopper_obj['shopper-info']['payment-info']['credit-cards-info'])

        # Add first credit card
        update_successful = shopper.update(
            shopper_id=shopper_id,
            contact_info=self.contact_info,
            credit_card=self.encrypted_credit_card)
        self.assertTrue(update_successful)

        shopper_obj = shopper.find_by_shopper_id(shopper_id)
        credit_card_info = shopper_obj['shopper-info']['payment-info']['credit-cards-info']['credit-card-info']
        self.assertIsInstance(credit_card_info['credit-card'], dict)
        # Since credit_card and encrypted_credit_card are the same I can get the last 4 digits from the non encrypted
        self.assertEqual(credit_card_info['credit-card']['card-last-four-digits'], self.credit_card.card_number[-4:])
        self.assertEqual(credit_card_info['credit-card']['card-type'], self.encrypted_credit_card.card_type)

        # Add second credit card
        update_successful = shopper.update(
            shopper_id=shopper_id,
            contact_info=self.contact_info,
            credit_card=self.encrypted_second_credit_card)
        self.assertTrue(update_successful)

        shopper_obj = shopper.find_by_shopper_id(shopper_id)
        credit_cards_info = shopper_obj['shopper-info']['payment-info']['credit-cards-info']['credit-card-info']
        self.assertIsInstance(credit_cards_info, list)
        self.assertEqual(len(credit_cards_info), 2)

        # The order of the credit cards is not known, so we sort the items before comparing.
        cards = [dict(c['credit-card']) for c in credit_cards_info]
        self.assertEqual(
            cards,
            [{'card-last-four-digits': self.credit_card.card_number[-4:],
              'card-type': self.encrypted_credit_card.card_type},
             {'card-last-four-digits': self.second_credit_card.card_number[-4:],
              'card-type': self.encrypted_second_credit_card.card_type}])

        # Add third credit card
        update_successful = shopper.update(
            shopper_id=shopper_id,
            contact_info=self.contact_info,
            credit_card=self.encrypted_third_credit_card)
        self.assertTrue(update_successful)

        shopper_obj = shopper.find_by_shopper_id(shopper_id)
        credit_cards_info = shopper_obj['shopper-info']['payment-info']['credit-cards-info']['credit-card-info']
        self.assertIsInstance(credit_cards_info, list)
        self.assertEqual(len(credit_cards_info), 3)

        # Last added credit card displays first
        cards = [dict(c['credit-card']) for c in credit_cards_info]
        self.assertEqual(
            cards,
            [{'card-last-four-digits': self.credit_card.card_number[-4:],
              'card-type': self.encrypted_credit_card.card_type},
             {'card-last-four-digits': self.second_credit_card.card_number[-4:],
              'card-type': self.encrypted_second_credit_card.card_type},
             {'card-last-four-digits': self.third_credit_card.card_number[-4:],
              'card-type': self.encrypted_third_credit_card.card_type}])

    @mocked_api.activate
    def test_add_invalid_credit_card(self):
        # Create a shopper, ensuring no credit card info was added
        shopper = ShopperResource()
        shopper_id = shopper.create(
            contact_info=self.contact_info)
        shopper_obj = shopper.find_by_shopper_id(shopper_id)
        self.assertIsNone(shopper_obj['shopper-info']['payment-info']['credit-cards-info'])

        # Add expired card
        with self.assertRaises(exceptions.CardError) as e:
            shopper.update(
                shopper_id=shopper_id,
                contact_info=self.contact_info,
                credit_card=PlainCreditCard(
                    card_type=helper.DUMMY_CARD_VISA__EXPIRED['card_type'],
                    expiration_month=helper.DUMMY_CARD_VISA__EXPIRED['expiration_month'],
                    expiration_year=helper.DUMMY_CARD_VISA__EXPIRED['expiration_year'],
                    card_number=helper.DUMMY_CARD_VISA__EXPIRED['card_number'],
                    security_code=helper.DUMMY_CARD_VISA__EXPIRED['security_code']))
        self.assertEqual(e.exception.code, '430306-14002')
        self.assertEqual(e.exception.description,
                         'The expiration date entered is invalid. Enter valid expiration date or try another card')
        self.assertEqual(e.exception.verbose_description,
                         'Order creation could not be completed because of payment processing failure: 430306 '
                         '- The expiration date entered is invalid. Enter valid expiration date or try another card')

        # Add card with insufficient funds
        with self.assertRaises(exceptions.CardError) as e:
            shopper.update(
                shopper_id=shopper_id,
                contact_info=self.contact_info,
                credit_card=PlainCreditCard(
                    card_type=helper.DUMMY_CARD_VISA__INSUFFICIENT_FUNDS['card_type'],
                    expiration_month=helper.DUMMY_CARD_VISA__INSUFFICIENT_FUNDS['expiration_month'],
                    expiration_year=helper.DUMMY_CARD_VISA__INSUFFICIENT_FUNDS['expiration_year'],
                    card_number=helper.DUMMY_CARD_VISA__INSUFFICIENT_FUNDS['card_number'],
                    security_code=helper.DUMMY_CARD_VISA__INSUFFICIENT_FUNDS['security_code']))
        self.assertEqual(e.exception.code, '430360-14002')
        self.assertEqual(e.exception.description,
                         'Insufficient funds. Please use another card or contact your bank for assistance')
        self.assertEqual(e.exception.verbose_description,
                         'Order creation could not be completed because of payment processing failure: 430360 '
                         '- Insufficient funds. Please use another card or contact your bank for assistance')

        # Add card with invalid number
        with self.assertRaises(exceptions.CardError) as e:
            shopper.update(
                shopper_id=shopper_id,
                contact_info=self.contact_info,
                credit_card=PlainCreditCard(
                    card_type=helper.DUMMY_CARD_VISA__INVALID_CARD_NUMBER['card_type'],
                    expiration_month=helper.DUMMY_CARD_VISA__INVALID_CARD_NUMBER['expiration_month'],
                    expiration_year=helper.DUMMY_CARD_VISA__INVALID_CARD_NUMBER['expiration_year'],
                    card_number=helper.DUMMY_CARD_VISA__INVALID_CARD_NUMBER['card_number'],
                    security_code=helper.DUMMY_CARD_VISA__INVALID_CARD_NUMBER['security_code']))
        self.assertEqual(e.exception.code, '430330-14002')
        self.assertEqual(e.exception.description,
                         'Invalid card number. Please check the number and try again, or use a different card')
        self.assertEqual(e.exception.verbose_description,
                         'Order creation could not be completed because of payment processing failure: 430330 '
                         '- Invalid card number. Please check the number and try again, or use a different card')

        # Add card with invalid number
        with self.assertRaises(exceptions.CardError) as e:
            shopper.update(
                shopper_id=shopper_id,
                contact_info=self.contact_info,
                credit_card=PlainCreditCard(
                    card_type=helper.DUMMY_CARD_AMEX__AUTH_FAIL['card_type'],
                    expiration_month=helper.DUMMY_CARD_AMEX__AUTH_FAIL['expiration_month'],
                    expiration_year=helper.DUMMY_CARD_AMEX__AUTH_FAIL['expiration_year'],
                    card_number=helper.DUMMY_CARD_AMEX__AUTH_FAIL['card_number'],
                    security_code=helper.DUMMY_CARD_AMEX__AUTH_FAIL['security_code']))
        self.assertEqual(e.exception.code, '430285-14002')
        self.assertEqual(e.exception.description,
                         'Authorization has failed for this transaction. '
                         'Please try again or contact your bank for assistance')

    @mocked_api.activate
    def test_add_invalid_encrypted_credit_card(self):
        # Create a shopper, ensuring no credit card info was added
        shopper = ShopperResource()
        shopper_id = shopper.create(
            contact_info=self.contact_info)
        shopper_obj = shopper.find_by_shopper_id(shopper_id)
        self.assertIsNone(shopper_obj['shopper-info']['payment-info']['credit-cards-info'])

        # Add expired card
        with self.assertRaises(exceptions.CardError) as e:
            shopper.update(
                shopper_id=shopper_id,
                contact_info=self.contact_info,
                credit_card=EncryptedCreditCard(
                    card_type=helper.DUMMY_CARD_VISA__EXPIRED['card_type'],
                    expiration_month=helper.DUMMY_CARD_VISA__EXPIRED['expiration_month'],
                    expiration_year=helper.DUMMY_CARD_VISA__EXPIRED['expiration_year'],
                    encrypted_card_number='encrypted_%s' % helper.DUMMY_CARD_VISA__EXPIRED['card_number'],
                    encrypted_security_code=helper.DUMMY_CARD_VISA__EXPIRED['encrypted_security_code']))
        self.assertEqual(e.exception.code, '430306-14002')
        self.assertEqual(e.exception.description,
                         'The expiration date entered is invalid. Enter valid expiration date or try another card')
        self.assertEqual(e.exception.verbose_description,
                         'Order creation could not be completed because of payment processing failure: 430306 '
                         '- The expiration date entered is invalid. Enter valid expiration date or try another card')

        # Add card with insufficient funds
        with self.assertRaises(exceptions.CardError) as e:
            shopper.update(
                shopper_id=shopper_id,
                contact_info=self.contact_info,
                credit_card=EncryptedCreditCard(
                    card_type=helper.DUMMY_CARD_VISA__INSUFFICIENT_FUNDS['card_type'],
                    expiration_month=helper.DUMMY_CARD_VISA__INSUFFICIENT_FUNDS['expiration_month'],
                    expiration_year=helper.DUMMY_CARD_VISA__INSUFFICIENT_FUNDS['expiration_year'],
                    encrypted_card_number='encrypted_%s' % helper.DUMMY_CARD_VISA__INSUFFICIENT_FUNDS['card_number'],
                    encrypted_security_code=helper.DUMMY_CARD_VISA__INSUFFICIENT_FUNDS['encrypted_security_code']))
        self.assertEqual(e.exception.code, '430360-14002')
        self.assertEqual(e.exception.description,
                         'Insufficient funds. Please use another card or contact your bank for assistance')
        self.assertEqual(e.exception.verbose_description,
                         'Order creation could not be completed because of payment processing failure: 430360 '
                         '- Insufficient funds. Please use another card or contact your bank for assistance')

        # Add card with invalid number
        with self.assertRaises(exceptions.CardError) as e:
            shopper.update(
                shopper_id=shopper_id,
                contact_info=self.contact_info,
                credit_card=EncryptedCreditCard(
                    card_type=helper.DUMMY_CARD_VISA__INVALID_CARD_NUMBER['card_type'],
                    expiration_month=helper.DUMMY_CARD_VISA__INVALID_CARD_NUMBER['expiration_month'],
                    expiration_year=helper.DUMMY_CARD_VISA__INVALID_CARD_NUMBER['expiration_year'],
                    encrypted_card_number='encrypted_%s' % helper.DUMMY_CARD_VISA__INVALID_CARD_NUMBER['card_number'],
                    encrypted_security_code=helper.DUMMY_CARD_VISA__INVALID_CARD_NUMBER['encrypted_security_code']))
        self.assertEqual(e.exception.code, '430330-14002')
        self.assertEqual(e.exception.description,
                         'Invalid card number. Please check the number and try again, or use a different card')
        self.assertEqual(e.exception.verbose_description,
                         'Order creation could not be completed because of payment processing failure: 430330 '
                         '- Invalid card number. Please check the number and try again, or use a different card')

        # Add card with invalid number
        with self.assertRaises(exceptions.CardError) as e:
            shopper.update(
                shopper_id=shopper_id,
                contact_info=self.contact_info,
                credit_card=EncryptedCreditCard(
                    card_type=helper.DUMMY_CARD_AMEX__AUTH_FAIL['card_type'],
                    expiration_month=helper.DUMMY_CARD_AMEX__AUTH_FAIL['expiration_month'],
                    expiration_year=helper.DUMMY_CARD_AMEX__AUTH_FAIL['expiration_year'],
                    encrypted_card_number='encrypted_%s' % helper.DUMMY_CARD_AMEX__AUTH_FAIL['card_number'],
                    encrypted_security_code=helper.DUMMY_CARD_AMEX__AUTH_FAIL['encrypted_security_code']))
        self.assertEqual(e.exception.code, '430285-14002')
        self.assertEqual(e.exception.description,
                         'Authorization has failed for this transaction. '
                         'Please try again or contact your bank for assistance')


class OrderTestCase(TestCase):
    @mocked_api.activate
    def setUp(self):
        self.contact_info = ContactInfo(
            first_name='John',
            last_name='Doe',
            email='test@justyoyo.com',
            zip_='SW5',
            country='gb',
            phone='07777777777')

        self.credit_card = PlainCreditCard(
            card_type=helper.DUMMY_CARD_VISA['card_type'],
            expiration_month=helper.DUMMY_CARD_VISA['expiration_month'],
            expiration_year=helper.DUMMY_CARD_VISA['expiration_year'],
            card_number=helper.DUMMY_CARD_VISA['card_number'],
            security_code=helper.DUMMY_CARD_VISA['security_code'])

        self.encrypted_credit_card = EncryptedCreditCard(
            card_type=helper.DUMMY_CARD_VISA['card_type'],
            expiration_month=helper.DUMMY_CARD_VISA['expiration_month'],
            expiration_year=helper.DUMMY_CARD_VISA['expiration_year'],
            encrypted_card_number='encrypted_%s' % helper.DUMMY_CARD_VISA['card_number'],
            encrypted_security_code=helper.DUMMY_CARD_VISA['encrypted_security_code'])

        self.credit_card_selection = CreditCardSelection(
            card_type=helper.DUMMY_CARD_VISA['card_type'],
            card_last_four_digits=helper.DUMMY_CARD_VISA['card_number'][-4:])

        shopper = ShopperResource()

        self.shopper_id_with_one_credit_card = shopper.create(
            contact_info=self.contact_info,
            credit_card=self.credit_card)

        self.shopper_id_with_one_encrypted_credit_card = shopper.create(
            contact_info=self.contact_info,
            credit_card=self.encrypted_credit_card)

        self.shopper_id_without_credit_card = shopper.create(
            contact_info=self.contact_info)

        self.shopper_id_with_two_credit_cards = shopper.create(
            contact_info=self.contact_info,
            credit_card=self.credit_card)
        self.assertTrue(shopper.update(
            shopper_id=self.shopper_id_with_two_credit_cards,
            contact_info=self.contact_info,
            credit_card=PlainCreditCard(
                card_type=helper.DUMMY_CARD_MASTERCARD['card_type'],
                expiration_month=helper.DUMMY_CARD_MASTERCARD['expiration_month'],
                expiration_year=helper.DUMMY_CARD_MASTERCARD['expiration_year'],
                card_number=helper.DUMMY_CARD_MASTERCARD['card_number'],
                security_code=helper.DUMMY_CARD_MASTERCARD['security_code'])))

        self.shopper_id_with_two_encrypted_credit_cards = shopper.create(
            contact_info=self.contact_info,
            credit_card=self.encrypted_credit_card)
        self.assertTrue(shopper.update(
            shopper_id=self.shopper_id_with_two_encrypted_credit_cards,
            contact_info=self.contact_info,
            credit_card=EncryptedCreditCard(
                card_type=helper.DUMMY_CARD_MASTERCARD['card_type'],
                expiration_month=helper.DUMMY_CARD_MASTERCARD['expiration_month'],
                expiration_year=helper.DUMMY_CARD_MASTERCARD['expiration_year'],
                encrypted_card_number='encrypted_%s' % helper.DUMMY_CARD_MASTERCARD['card_number'],
                encrypted_security_code=helper.DUMMY_CARD_MASTERCARD['encrypted_security_code'])))

    @mocked_api.activate
    def test_shopper_with_credit_card_creating_order_succeeds(self):
        amount_in_pence = 150
        amount = amount_in_pence / 100.0
        description = 'order description'

        order = OrderResource()

        order_obj = order.create(
            shopper_id=self.shopper_id_with_one_credit_card,
            sku_id=helper.TEST_PRODUCT_SKU_ID,
            amount_in_pence=amount_in_pence,
            credit_card=self.credit_card_selection,
            description=description)

        self.assertIsInstance(order_obj, dict)
        self.assertEqual(order_obj['ordering-shopper']['shopper-id'], self.shopper_id_with_one_credit_card)
        self.assertEqual(order_obj['cart']['charged-currency'], order.client.currency)
        self.assertEqual(order_obj['cart']['cart-item']['sku']['sku-id'], helper.TEST_PRODUCT_SKU_ID)
        self.assertEqual(int(order_obj['cart']['cart-item']['quantity']), 1)
        self.assertEqual(float(order_obj['cart']['cart-item']['item-sub-total']), amount)
        self.assertEqual(float(order_obj['cart']['tax']), 0.0)
        self.assertEqual(int(order_obj['cart']['tax-rate']), 0)
        self.assertEqual(float(order_obj['cart']['total-cart-cost']), amount)
        self.assertIsNotNone(order_obj['post-sale-info']['invoices']['invoice']['invoice-id'])
        self.assertIsNotNone(order_obj['post-sale-info']['invoices']['invoice']['url'])
        self.assertIsNotNone(
            order_obj['post-sale-info']['invoices']['invoice']['financial-transactions']['financial-transaction'][
                'soft-descriptor'], description)
        self.assertEqual(float(
            order_obj['post-sale-info']['invoices']['invoice']['financial-transactions']['financial-transaction'][
                'amount']), amount)
        self.assertEqual(
            order_obj['post-sale-info']['invoices']['invoice']['financial-transactions']['financial-transaction'][
                'currency'], order.client.currency)
        self.assertEqual(
            order_obj['post-sale-info']['invoices']['invoice']['financial-transactions']['financial-transaction'][
                'credit-card']['card-last-four-digits'], self.credit_card.card_number[-4:])

    @mocked_api.activate
    def test_shopper_with_encrypted_credit_card_creating_order_succeeds(self):
        amount_in_pence = 150
        amount = amount_in_pence / 100.0
        description = 'order description'

        order = OrderResource()

        order_obj = order.create(
            shopper_id=self.shopper_id_with_one_encrypted_credit_card,
            sku_id=helper.TEST_PRODUCT_SKU_ID,
            amount_in_pence=amount_in_pence,
            credit_card=self.credit_card_selection,
            description=description)

        self.assertIsInstance(order_obj, dict)
        self.assertEqual(order_obj['ordering-shopper']['shopper-id'], self.shopper_id_with_one_encrypted_credit_card)
        self.assertEqual(order_obj['cart']['charged-currency'], order.client.currency)
        self.assertEqual(order_obj['cart']['cart-item']['sku']['sku-id'], helper.TEST_PRODUCT_SKU_ID)
        self.assertEqual(int(order_obj['cart']['cart-item']['quantity']), 1)
        self.assertEqual(float(order_obj['cart']['cart-item']['item-sub-total']), amount)
        self.assertEqual(float(order_obj['cart']['tax']), 0.0)
        self.assertEqual(int(order_obj['cart']['tax-rate']), 0)
        self.assertEqual(float(order_obj['cart']['total-cart-cost']), amount)
        self.assertIsNotNone(order_obj['post-sale-info']['invoices']['invoice']['invoice-id'])
        self.assertIsNotNone(order_obj['post-sale-info']['invoices']['invoice']['url'])
        self.assertIsNotNone(
            order_obj['post-sale-info']['invoices']['invoice']['financial-transactions']['financial-transaction'][
                'soft-descriptor'], description)
        self.assertEqual(float(
            order_obj['post-sale-info']['invoices']['invoice']['financial-transactions']['financial-transaction'][
                'amount']), amount)
        self.assertEqual(
            order_obj['post-sale-info']['invoices']['invoice']['financial-transactions']['financial-transaction'][
                'currency'], order.client.currency)
        self.assertEqual(
            order_obj['post-sale-info']['invoices']['invoice']['financial-transactions']['financial-transaction'][
                'credit-card']['card-last-four-digits'], self.credit_card_selection.card_last_four_digits)

    @mocked_api.activate
    def test_shopper_without_credit_card_creating_order_fails(self):
        order = OrderResource()

        # Without credit card selection
        with self.assertRaises(exceptions.APIError) as e:
            order.create(
                shopper_id=self.shopper_id_without_credit_card,
                sku_id=helper.TEST_PRODUCT_SKU_ID,
                amount_in_pence=100)
        self.assertEqual(e.exception.code, '15009')
        self.assertEqual(e.exception.description, 'Order creation failure, since no payment information was provided.')

        # With bogus credit card selection
        with self.assertRaises(exceptions.APIError) as e:
            order.create(
                shopper_id=self.shopper_id_without_credit_card,
                sku_id=helper.TEST_PRODUCT_SKU_ID,
                amount_in_pence=100,
                credit_card=self.credit_card_selection)
        self.assertEqual(e.exception.code, '10000')
        self.assertEqual(e.exception.description,
                         'The order failed because shopper payment details were incorrect or insufficient.')

    @mocked_api.activate
    def test_shopper_with_two_credit_cards_with_valid_selection_succeeds(self):
        amount_in_pence = 150
        amount = amount_in_pence / 100.0
        description = 'order description'

        order = OrderResource()

        order_obj = order.create(
            shopper_id=self.shopper_id_with_two_credit_cards,
            sku_id=helper.TEST_PRODUCT_SKU_ID,
            amount_in_pence=amount_in_pence,
            credit_card=self.credit_card_selection,
            description=description)

        self.assertIsInstance(order_obj, dict)
        self.assertEqual(order_obj['ordering-shopper']['shopper-id'], self.shopper_id_with_two_credit_cards)
        self.assertEqual(order_obj['cart']['charged-currency'], order.client.currency)
        self.assertEqual(order_obj['cart']['cart-item']['sku']['sku-id'], helper.TEST_PRODUCT_SKU_ID)
        self.assertEqual(int(order_obj['cart']['cart-item']['quantity']), 1)
        self.assertEqual(float(order_obj['cart']['cart-item']['item-sub-total']), amount)
        self.assertEqual(float(order_obj['cart']['tax']), 0.0)
        self.assertEqual(int(order_obj['cart']['tax-rate']), 0)
        self.assertEqual(float(order_obj['cart']['total-cart-cost']), amount)
        self.assertIsNotNone(order_obj['post-sale-info']['invoices']['invoice']['invoice-id'])
        self.assertIsNotNone(order_obj['post-sale-info']['invoices']['invoice']['url'])
        self.assertIsNotNone(
            order_obj['post-sale-info']['invoices']['invoice']['financial-transactions']['financial-transaction'][
                'soft-descriptor'], description)
        self.assertEqual(float(
            order_obj['post-sale-info']['invoices']['invoice']['financial-transactions']['financial-transaction'][
                'amount']), amount)
        self.assertEqual(
            order_obj['post-sale-info']['invoices']['invoice']['financial-transactions']['financial-transaction'][
                'currency'], order.client.currency)
        self.assertEqual(
            order_obj['post-sale-info']['invoices']['invoice']['financial-transactions']['financial-transaction'][
                'credit-card']['card-last-four-digits'], self.credit_card_selection.card_last_four_digits)

    @mocked_api.activate
    def test_shopper_with_two_encrypted_credit_cards_with_valid_selection_succeeds(self):
        amount_in_pence = 150
        amount = amount_in_pence / 100.0
        description = 'order description'

        order = OrderResource()

        order_obj = order.create(
            shopper_id=self.shopper_id_with_two_encrypted_credit_cards,
            sku_id=helper.TEST_PRODUCT_SKU_ID,
            amount_in_pence=amount_in_pence,
            credit_card=self.credit_card_selection,
            description=description)

        self.assertIsInstance(order_obj, dict)
        self.assertEqual(order_obj['ordering-shopper']['shopper-id'], self.shopper_id_with_two_encrypted_credit_cards)
        self.assertEqual(order_obj['cart']['charged-currency'], order.client.currency)
        self.assertEqual(order_obj['cart']['cart-item']['sku']['sku-id'], helper.TEST_PRODUCT_SKU_ID)
        self.assertEqual(int(order_obj['cart']['cart-item']['quantity']), 1)
        self.assertEqual(float(order_obj['cart']['cart-item']['item-sub-total']), amount)
        self.assertEqual(float(order_obj['cart']['tax']), 0.0)
        self.assertEqual(int(order_obj['cart']['tax-rate']), 0)
        self.assertEqual(float(order_obj['cart']['total-cart-cost']), amount)
        self.assertIsNotNone(order_obj['post-sale-info']['invoices']['invoice']['invoice-id'])
        self.assertIsNotNone(order_obj['post-sale-info']['invoices']['invoice']['url'])
        self.assertIsNotNone(
            order_obj['post-sale-info']['invoices']['invoice']['financial-transactions']['financial-transaction'][
                'soft-descriptor'], description)
        self.assertEqual(float(
            order_obj['post-sale-info']['invoices']['invoice']['financial-transactions']['financial-transaction'][
                'amount']), amount)
        self.assertEqual(
            order_obj['post-sale-info']['invoices']['invoice']['financial-transactions']['financial-transaction'][
                'currency'], order.client.currency)
        self.assertEqual(
            order_obj['post-sale-info']['invoices']['invoice']['financial-transactions']['financial-transaction'][
                'credit-card']['card-last-four-digits'], self.credit_card_selection.card_last_four_digits)

    @mocked_api.activate
    def test_shopper_with_two_credit_cards_with_invalid_selection_fails(self):
        order = OrderResource()

        with self.assertRaises(exceptions.APIError) as e:
            order.create(
                shopper_id=self.shopper_id_with_two_credit_cards,
                sku_id=helper.TEST_PRODUCT_SKU_ID,
                amount_in_pence=100,
                credit_card=CreditCardSelection(
                    card_type=helper.DUMMY_CARD_AMEX['card_type'],
                    card_last_four_digits=helper.DUMMY_CARD_AMEX['card_number'][-4:]))
        self.assertEqual(e.exception.description,
                         'The order failed because shopper payment details were incorrect or insufficient.')
