# Chargily Customer Integration Guide

This guide explains how to use the automatic customer creation feature with Chargily payment integration.

## Overview

When processing payments with Chargily, you can now:
1. Use an existing Chargily customer ID
2. Let the system automatically create a customer in Chargily

The automatic customer creation feature simplifies the payment flow by creating a customer record in Chargily's system directly from the payment request, without requiring a separate API call.

## API Usage

### Option 1: Use Existing Customer ID

If you already have a customer ID from Chargily, you can include it directly in your payment request:

```json
POST /invoice/invoices/{invoice_id}/pay
{
  "payment_method": "edahabia",
  "amount": 2500.0,
  "currency": "dzd",
  "success_url": "https://your-app.com/success",
  "failure_url": "https://your-app.com/failure",
  "webhook_endpoint": "https://your-app.com/webhook",
  "customer_id": "01hj0p5s3ygy2mx1czg2wzcc4x"
}
```

### Option 2: Automatic Customer Creation

To create a customer automatically during checkout, include `user_data` in your payment request:

```json
POST /invoice/invoices/{invoice_id}/pay
{
  "payment_method": "edahabia",
  "amount": 2500.0,
  "currency": "dzd",
  "success_url": "https://your-app.com/success",
  "failure_url": "https://your-app.com/failure",
  "webhook_endpoint": "https://your-app.com/webhook",
  "user_data": {
    "name": "Customer Name",
    "email": "customer@example.com",
    "phone": "+213500000000",
    "address": {
      "country": "DZ",
      "state": "Algiers",
      "address": "123 Customer Street"
    },
    "metadata": {
      "user_id": "your-user-123"
    }
  }
}
```

The system will:
1. First create a customer in Chargily using the provided user data
2. Then use the returned customer ID to create the checkout
3. Return a single payment URL to the client

## User Data Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Customer name |
| email | string | No | Customer email |
| phone | string | No | Customer phone number |
| address | object | No | Customer address details |
| address.country | string | No | ISO 3166-1 alpha-2 two-letter country code (e.g., DZ for Algeria) |
| address.state | string | No | State/province/wilaya |
| address.address | string | No | Street address |
| metadata | object | No | Additional customer data |

## Example with cURL

```bash
curl -X POST \
  https://your-app.com/invoice/invoices/inv-12345/pay \
  -H 'Content-Type: application/json' \
  -d '{
  "payment_method": "edahabia",
  "amount": 2500.0,
  "currency": "dzd",
  "success_url": "https://your-app.com/success",
  "failure_url": "https://your-app.com/failure",
  "webhook_endpoint": "https://your-app.com/webhook",
  "user_data": {
    "name": "Test Customer",
    "email": "customer@example.com",
    "phone": "+213500000000",
    "address": {
      "country": "DZ",
      "state": "Algiers",
      "address": "123 Test Street"
    }
  }
}'
```

## Response

The response will include the payment URL, transaction ID, and additionally the customer ID if a new customer was created:

```json
{
  "status": "success",
  "message": "Payment initiated successfully",
  "data": {
    "invoice_id": "inv-12345",
    "payment_url": "https://pay.chargily.net/test/checkout/checkout_abcdef123456",
    "transaction_id": "checkout_abcdef123456",
    "customer_id": "01hj0p5s3ygy2mx1czg2wzcc4x",
    "redirect_user": true
  }
}
```

## Benefits of Customer Integration

1. **Simplified Checkout**: Create both customer and payment in a single API call
2. **Customer Management**: Build a customer database in Chargily for future payments
3. **Payment Analytics**: Track payments by customer
4. **Improved User Experience**: Pre-fill customer information in checkout forms
5. **Repeat Purchases**: Enable easier repeat purchases for returning customers

## Direct Chargily API Calls

If you need to manage customers directly, you can use these Chargily API endpoints:

### Create a Customer

```bash
curl -X POST \
  https://pay.chargily.net/test/api/v2/customers \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Customer Name",
  "email": "customer@example.com",
  "phone": "+213500000000",
  "address": {
    "country": "DZ",
    "state": "Algiers",
    "address": "123 Customer Street"
  },
  "metadata": {
    "user_id": "your-user-123"
  }
}'
```

### Get a Customer

```bash
curl -X GET \
  https://pay.chargily.net/test/api/v2/customers/{customer_id} \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json'
```

### List Customers

```bash
curl -X GET \
  https://pay.chargily.net/test/api/v2/customers \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json'
```

## Troubleshooting

If you encounter issues with customer creation:

1. **Invalid Data**: Ensure all provided customer data is valid
2. **API Authentication**: Verify your API key is correct
3. **Required Fields**: Check that name is provided (it's required)
4. **Country Code**: Use ISO 3166-1 alpha-2 two-letter country code (e.g., DZ for Algeria)
5. **Address Format**: Ensure address data is properly formatted as an object 