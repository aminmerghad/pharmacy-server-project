# Chargily Payment Integration Testing Guide

This guide provides detailed instructions for testing the Chargily payment integration with our Invoice Service. It includes real URLs, example API calls, and step-by-step instructions for both manual and automated testing.

## Prerequisites

1. A Chargily account with API access
2. Your Chargily API key (available in your Chargily dashboard)
3. Access to your application's backend or API testing tool like Postman

## Chargily API Endpoints

| Environment | Base URL |
|-------------|----------|
| Test | `https://pay.chargily.net/test/api/v2` |
| Production | `https://pay.chargily.net/api/v2` |

## Testing Process Overview

1. Create an invoice in your system
2. Initiate a payment request to Chargily
3. Complete the payment on Chargily's checkout page
4. Handle the webhook notification
5. Verify the invoice status update

## Step 1: Create an Invoice

Create an invoice using your application's API:

```
POST /invoice/invoices
{
  "order_id": "ord-123456",
  "user_id": "user-123456",
  "items": [
    {
      "product_id": "prod-123456", 
      "description": "Test Product",
      "quantity": 1,
      "unit_price": 2500.0
    }
  ]
}
```

Note the `invoice_id` in the response for use in subsequent steps.

## Step 2: Generate Payment Parameters

You can get sample payment parameters for testing using:

```
GET /invoice/invoices/{invoice_id}/pay/chargily
```

This will return a sample payload and curl command that can be used for testing.

## Step 3: Initiate a Payment Request

Initiate a payment request to Chargily using the following API call:

```
POST /invoice/invoices/{invoice_id}/pay
{
  "payment_method": "edahabia",  // or "cib" for CIB cards
  "amount": 2500.0,
  "currency": "dzd",
  "success_url": "https://your-app.com/invoice/payment/success",
  "failure_url": "https://your-app.com/invoice/payment/failure",
  "webhook_endpoint": "https://your-app.com/webhooks/chargily",
  "description": "Payment for invoice #{invoice_id}"
}
```

### API Response

The API will respond with:

```json
{
  "status": "success",
  "message": "Payment initiated successfully",
  "data": {
    "invoice_id": "inv_12345",
    "payment_url": "https://pay.chargily.net/test/checkout/checkout_abcdef123456",
    "transaction_id": "checkout_abcdef123456",
    "redirect_user": true
  }
}
```

## Step 4: Complete the Payment

To complete the payment, open the `payment_url` from the response in a browser. This will take you to Chargily's checkout page.

### Test Card Details

For testing in the test environment, you can use the following card details:

**Edahabia Card:**
- Card Number: 5555 5555 5555 4444
- Expiry Date: Any future date
- CVV: Any 3 digits

**CIB Card:**
- Card Number: 4242 4242 4242 4242
- Expiry Date: Any future date
- CVV: Any 3 digits

## Step 5: Handle the Webhook Notification

After payment completion, Chargily will send a webhook notification to the `webhook_endpoint` URL you provided. 

### Example Webhook Payload

```json
{
  "id": "checkout_abcdef123456",
  "status": "paid",
  "amount": 250000,
  "currency": "dzd",
  "created_at": 1626862420,
  "metadata": {
    "invoice_id": "inv_12345"
  },
  "payment_method": "edahabia"
}
```

### Webhook Status Values

- `pending`: Payment is pending
- `paid`: Payment is completed successfully
- `failed`: Payment failed
- `expired`: Payment link has expired
- `canceled`: Payment was canceled

### Testing Webhooks Locally

For testing webhooks locally, you can use tools like ngrok or localtunnel to expose your local server to the internet:

```
ngrok http 5000
```

Then use the generated URL as your webhook endpoint:

```
"webhook_endpoint": "https://abc123.ngrok.io/webhooks/chargily"
```

## Step 6: Verify Invoice Status

After the webhook is processed, verify that the invoice status has been updated:

```
GET /invoice/invoices/{invoice_id}
```

The response should show the invoice status as "PAID" if the payment was successful.

## Manual Testing with cURL

Here are some cURL commands for manual testing:

### 1. Create an Invoice

```bash
curl -X POST \
  https://your-app.com/invoice/invoices \
  -H 'Content-Type: application/json' \
  -d '{
  "order_id": "ord-123456",
  "user_id": "user-123456",
  "items": [
    {
      "product_id": "prod-123456", 
      "description": "Test Product",
      "quantity": 1,
      "unit_price": 2500.0
    }
  ]
}'
```

### 2. Initiate Payment

```bash
curl -X POST \
  https://your-app.com/invoice/invoices/{invoice_id}/pay \
  -H 'Content-Type: application/json' \
  -d '{
  "payment_method": "edahabia",
  "amount": 2500.0,
  "currency": "dzd",
  "success_url": "https://your-app.com/invoice/payment/success",
  "failure_url": "https://your-app.com/invoice/payment/failure",
  "webhook_endpoint": "https://your-app.com/webhooks/chargily",
  "description": "Payment for invoice #{invoice_id}"
}'
```

### 3. Check Invoice Status

```bash
curl -X GET \
  https://your-app.com/invoice/invoices/{invoice_id}
```

### 4. Simulate a Webhook

To simulate a webhook notification for testing:

```bash
curl -X POST \
  https://your-app.com/webhooks/chargily \
  -H 'Content-Type: application/json' \
  -d '{
  "id": "checkout_abcdef123456",
  "status": "paid",
  "amount": 250000,
  "currency": "dzd",
  "created_at": 1626862420,
  "metadata": {
    "invoice_id": "{invoice_id}"
  },
  "payment_method": "edahabia"
}'
```

## Direct Chargily API Testing

If you want to test the Chargily API directly:

### Create a Checkout Session

```bash
curl -X POST \
  https://pay.chargily.net/test/api/v2/checkouts \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
  "amount": 2500,
  "currency": "dzd",
  "payment_method": "edahabia",
  "success_url": "https://your-app.com/success",
  "failure_url": "https://your-app.com/failure",
  "webhook_endpoint": "https://your-app.com/webhook",
  "description": "Test payment",
  "locale": "en",
  "metadata": {
    "invoice_id": "inv_12345"
  }
}'
```

### Check Checkout Status

```bash
curl -X GET \
  https://pay.chargily.net/test/api/v2/checkouts/{checkout_id} \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -H 'Content-Type: application/json'
```

## Troubleshooting

### Common Issues

1. **Authentication Error**: Ensure your API key is correct and valid
2. **Webhook Not Received**: Check that your webhook endpoint is publicly accessible
3. **Invalid Currency**: Chargily only supports DZD currency
4. **Failed Transactions**: Verify that you're using the correct test card numbers

### Debug Steps

1. Check the application logs for detailed error messages
2. Verify all required parameters are included in your requests
3. Ensure your webhook endpoint is correctly configured and accessible
4. Test the direct Chargily API to isolate issues

## Security Best Practices

1. Always verify webhook signatures using the webhook secret
2. Use HTTPS for all endpoints
3. Don't expose your API key in client-side code
4. Validate all input data before sending to Chargily
5. Implement proper error handling and logging 