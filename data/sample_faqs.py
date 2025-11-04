"""
Sample FAQ data for customer support
"""

SAMPLE_FAQS = [
    # Shipping FAQs
    {
        "category": "shipping",
        "question": "What are your shipping options?",
        "answer": "We offer Standard Shipping (5-7 business days, $5.99), Express Shipping (2-3 business days, $12.99), and Overnight Shipping (1 business day, $24.99). Free standard shipping on orders over $50."
    },
    {
        "category": "shipping",
        "question": "How long does shipping take?",
        "answer": "Standard shipping takes 5-7 business days, Express shipping takes 2-3 business days, and Overnight shipping takes 1 business day. International shipping typically takes 10-15 business days."
    },
    {
        "category": "shipping",
        "question": "Do you ship internationally?",
        "answer": "Yes, we ship to over 100 countries worldwide. International shipping rates vary by destination and are calculated at checkout. Please note that customs duties and import taxes may apply."
    },
    {
        "category": "shipping",
        "question": "Can I track my order?",
        "answer": "Yes! Once your order ships, you'll receive a tracking number via email. You can track your package using this number on our website or the carrier's tracking page."
    },
    {
        "category": "shipping",
        "question": "What if my package is lost or damaged?",
        "answer": "If your package is lost or arrives damaged, please contact us within 48 hours with photos (for damaged items). We'll initiate a claim with the carrier and send you a replacement or issue a full refund."
    },
    
    # Returns & Refunds
    {
        "category": "returns",
        "question": "What is your return policy?",
        "answer": "We accept returns within 30 days of delivery for most items. Products must be unused, in original packaging, and in resalable condition. Some items like opened software or personalized products cannot be returned."
    },
    {
        "category": "returns",
        "question": "How do I start a return?",
        "answer": "Log into your account, go to Order History, select the order, and click 'Return Item'. Follow the prompts to print a prepaid return label. Drop off the package at any authorized carrier location."
    },
    {
        "category": "returns",
        "question": "When will I get my refund?",
        "answer": "Refunds are processed within 5-7 business days after we receive and inspect your return. The refund will be credited to your original payment method. Bank processing may take an additional 3-5 business days."
    },
    {
        "category": "returns",
        "question": "Do I have to pay for return shipping?",
        "answer": "Return shipping is free for defective items or if we made an error. For other returns, a $6.99 return shipping fee will be deducted from your refund. Premium members get free returns on all items."
    },
    {
        "category": "returns",
        "question": "Can I exchange an item?",
        "answer": "We don't offer direct exchanges. Please return the original item for a refund and place a new order for the item you want. This ensures faster processing and you get the item you need sooner."
    },
    
    # Billing & Payment
    {
        "category": "billing",
        "question": "What payment methods do you accept?",
        "answer": "We accept Visa, Mastercard, American Express, Discover, PayPal, Apple Pay, Google Pay, and Shop Pay. We also offer buy now, pay later options through Affirm and Klarna."
    },
    {
        "category": "billing",
        "question": "Is it safe to use my credit card on your site?",
        "answer": "Absolutely! We use industry-standard SSL encryption and are PCI DSS compliant. We never store your full credit card information on our servers. All transactions are processed through secure payment gateways."
    },
    {
        "category": "billing",
        "question": "Why was my payment declined?",
        "answer": "Common reasons include insufficient funds, incorrect card details, billing address mismatch, or security holds by your bank. Please verify your information and try again. If the issue persists, contact your bank or use a different payment method."
    },
    {
        "category": "billing",
        "question": "Can I use multiple payment methods?",
        "answer": "Currently, we only support one payment method per order. You cannot split payment between multiple cards or methods. Consider using a service like PayPal if you need to combine balances."
    },
    {
        "category": "billing",
        "question": "Do you charge sales tax?",
        "answer": "Yes, we're required to collect sales tax in states where we have nexus. Tax is calculated based on your shipping address and applicable local rates. The exact amount will be shown before you complete your purchase."
    },
    
    # Account Management
    {
        "category": "account",
        "question": "How do I create an account?",
        "answer": "Click 'Sign Up' in the top right corner, enter your email, create a password, and fill in your basic information. You can also sign up using your Google or Facebook account for faster registration."
    },
    {
        "category": "account",
        "question": "I forgot my password. What should I do?",
        "answer": "Click 'Forgot Password' on the login page, enter your email address, and we'll send you a password reset link. Follow the link to create a new password. The link expires in 24 hours."
    },
    {
        "category": "account",
        "question": "How do I change my email address?",
        "answer": "Log into your account, go to Settings > Profile, click 'Edit' next to your email, enter your new email, and verify it by clicking the link we send you. Your old email will remain active until verification."
    },
    {
        "category": "account",
        "question": "Can I delete my account?",
        "answer": "Yes. Go to Settings > Privacy > Delete Account. Please note this action is permanent and cannot be undone. You'll lose your order history, saved addresses, and preferences. Active orders must be completed first."
    },
    {
        "category": "account",
        "question": "What are the benefits of creating an account?",
        "answer": "Benefits include faster checkout, order tracking, saved addresses and payment methods, exclusive member discounts, early access to sales, personalized recommendations, and order history for easy reordering."
    },
    
    # Products
    {
        "category": "products",
        "question": "Are your products authentic?",
        "answer": "Yes, all our products are 100% authentic and sourced directly from manufacturers or authorized distributors. We guarantee authenticity and offer full refunds if any product is found to be counterfeit."
    },
    {
        "category": "products",
        "question": "Do you offer gift wrapping?",
        "answer": "Yes! Gift wrapping is available for $4.99 per item. You can add a personalized message at no extra charge. Select the gift wrap option during checkout and customize your message."
    },
    {
        "category": "products",
        "question": "How do I find my size?",
        "answer": "Each product page has a detailed size chart. Click 'Size Guide' near the size selector. For clothing, we also offer a size recommendation tool based on your measurements. If you're between sizes, we generally recommend sizing up."
    },
    {
        "category": "products",
        "question": "When will items be back in stock?",
        "answer": "Out-of-stock items usually restock within 2-4 weeks. Click 'Notify Me' on the product page to receive an email when it's available. Popular items may sell out quickly upon restocking, so act fast!"
    },
    {
        "category": "products",
        "question": "Do you offer product warranties?",
        "answer": "Yes, most electronics and appliances come with manufacturer warranties (typically 1 year). We also offer extended warranty plans at checkout. Warranty details are listed on each product page."
    },
    
    # Orders
    {
        "category": "orders",
        "question": "Can I cancel my order?",
        "answer": "Orders can be cancelled within 1 hour of placement. Go to Order History, select your order, and click 'Cancel'. After 1 hour, orders enter processing and cannot be cancelled, but you can return items once received."
    },
    {
        "category": "orders",
        "question": "Can I change my shipping address after ordering?",
        "answer": "You can change the address within 1 hour of placing your order. Go to Order History and click 'Edit Address'. After the order enters processing, address changes aren't possible. Contact support immediately for urgent changes."
    },
    {
        "category": "orders",
        "question": "What does each order status mean?",
        "answer": "Pending: Payment being verified. Processing: Being prepared for shipment. Shipped: On the way to you. Delivered: Successfully received. Cancelled: Order was cancelled. Returned: Items sent back."
    },
    {
        "category": "orders",
        "question": "Can I order without an account?",
        "answer": "Yes, you can checkout as a guest. However, you'll need to provide an email address for order confirmation and tracking. Creating an account makes future purchases easier and lets you track all your orders in one place."
    },
    {
        "category": "orders",
        "question": "What's the minimum order amount?",
        "answer": "There's no minimum order amount. However, orders under $25 may incur a small order handling fee of $3.99. Free standard shipping applies to orders over $50."
    },
    
    # Promotions & Discounts
    {
        "category": "promotions",
        "question": "How do I use a promo code?",
        "answer": "Enter your promo code in the 'Discount Code' field at checkout and click 'Apply'. The discount will be reflected in your order total. Only one promo code can be used per order."
    },
    {
        "category": "promotions",
        "question": "Can I combine multiple discount codes?",
        "answer": "No, only one promo code can be applied per order. However, promo codes can be combined with member discounts and loyalty rewards. The system automatically applies the best available discount."
    },
    {
        "category": "promotions",
        "question": "Why isn't my promo code working?",
        "answer": "Common reasons: code expired, minimum purchase requirement not met, excluded items in cart, or code already used (one-time use codes). Check the promo terms and conditions or contact support for help."
    },
    {
        "category": "promotions",
        "question": "Do you have a loyalty program?",
        "answer": "Yes! Our Rewards program lets you earn 1 point per dollar spent. Earn 100 points to get a $5 reward. Members also get exclusive discounts, early sale access, and birthday bonuses. Join free in your account settings."
    },
    {
        "category": "promotions",
        "question": "When do you have sales?",
        "answer": "We have seasonal sales (Spring, Summer, Fall, Winter), holiday sales (Black Friday, Cyber Monday, Christmas), and flash sales throughout the year. Subscribe to our newsletter to get sale notifications and exclusive early access."
    },
    
    # Customer Service
    {
        "category": "support",
        "question": "How can I contact customer service?",
        "answer": "Contact us via: Live chat (available 9 AM - 9 PM EST), Email (support@company.com, 24-hour response), Phone (1-800-123-4567, 9 AM - 9 PM EST Mon-Fri), or submit a support ticket through your account."
    },
    {
        "category": "support",
        "question": "What are your business hours?",
        "answer": "Our customer service team is available Monday-Friday 9 AM - 9 PM EST, and Saturday-Sunday 10 AM - 6 PM EST. Email support is monitored 24/7 and we respond within 24 hours, typically much faster."
    },
    {
        "category": "support",
        "question": "Do you offer phone support?",
        "answer": "Yes, call us at 1-800-123-4567 during business hours (Mon-Fri 9 AM - 9 PM EST). For faster service, try our live chat or email support, which often have shorter wait times."
    },
    {
        "category": "support",
        "question": "How do I leave a product review?",
        "answer": "Log into your account, go to Order History, find the product you want to review, and click 'Write Review'. You can rate the product (1-5 stars), add comments, and upload photos. Reviews appear after moderation (usually 24 hours)."
    },
    {
        "category": "support",
        "question": "What should I do if I received the wrong item?",
        "answer": "We sincerely apologize! Contact us immediately with your order number and photos of the wrong item. We'll send you the correct item via expedited shipping at no charge and provide a prepaid return label for the wrong item."
    },
    
    # Privacy & Security
    {
        "category": "privacy",
        "question": "How do you protect my personal information?",
        "answer": "We use industry-standard encryption (SSL/TLS), secure servers, and strict access controls. We never sell your personal information to third parties. Read our Privacy Policy for full details on data protection and usage."
    },
    {
        "category": "privacy",
        "question": "Do you share my data with third parties?",
        "answer": "We only share data with service providers necessary for operations (payment processors, shipping carriers, email services). They're bound by strict confidentiality agreements. We never sell your data to marketers or advertisers."
    },
    {
        "category": "privacy",
        "question": "How do I opt out of marketing emails?",
        "answer": "Click 'Unsubscribe' at the bottom of any marketing email, or update preferences in your account under Settings > Email Preferences. You'll still receive important transactional emails (order confirmations, shipping updates)."
    },
    {
        "category": "privacy",
        "question": "Can I request my personal data?",
        "answer": "Yes, you have the right to access your data. Go to Settings > Privacy > Download Data, and we'll compile your information and send it to your email within 7 business days in a standard format (JSON or CSV)."
    },
    {
        "category": "privacy",
        "question": "Do you use cookies?",
        "answer": "Yes, we use cookies to improve your experience, remember your preferences, and analyze site traffic. Essential cookies are required for the site to function. You can manage non-essential cookies in your browser settings or our cookie consent banner."
    },
    
    # Technical Issues
    {
        "category": "technical",
        "question": "The website isn't working properly. What should I do?",
        "answer": "Try these steps: clear your browser cache and cookies, try a different browser, disable browser extensions, check your internet connection, or try on a different device. If issues persist, contact our technical support team."
    },
    {
        "category": "technical",
        "question": "Why can't I log in?",
        "answer": "Common issues: incorrect password (try password reset), caps lock enabled, browser cookies disabled, account suspended (check email), or temporary server issues. Try resetting your password or contact support if problems continue."
    },
    {
        "category": "technical",
        "question": "The checkout page isn't loading. Help!",
        "answer": "This is often due to browser issues. Try: clearing cache/cookies, disabling ad blockers, using a different browser or incognito mode, or checking if your security software is blocking the page. Contact support if the issue persists."
    },
    {
        "category": "technical",
        "question": "Is there a mobile app?",
        "answer": "Yes! Download our app from the App Store (iOS) or Google Play (Android). The app offers exclusive mobile-only deals, faster checkout, push notifications for order updates, and a better shopping experience."
    },
    {
        "category": "technical",
        "question": "Why are images not loading?",
        "answer": "This could be due to slow internet connection, browser cache issues, or ad blockers. Try: refreshing the page, clearing your browser cache, disabling ad blockers, or checking your internet connection. Contact support if images still don't load."
    }
]

# Additional categories for comprehensive coverage
ADDITIONAL_FAQS = [
    # Business & Wholesale
    {
        "category": "business",
        "question": "Do you offer wholesale or bulk pricing?",
        "answer": "Yes! We offer volume discounts for bulk orders (20+ units). Contact our B2B team at wholesale@company.com with your requirements for a custom quote. Business accounts get NET-30 payment terms and dedicated support."
    },
    {
        "category": "business",
        "question": "Can I get a tax exemption certificate?",
        "answer": "Yes, if you're a qualified business or organization. Upload your tax exemption certificate in your account under Business Settings > Tax Documents. Allow 2-3 business days for verification before placing tax-exempt orders."
    },
    
    # Sustainability
    {
        "category": "sustainability",
        "question": "What is your environmental policy?",
        "answer": "We're committed to sustainability: carbon-neutral shipping, recyclable packaging, partnerships with eco-friendly brands, and donations to environmental causes. Check our Sustainability page for our full environmental impact report."
    },
    {
        "category": "sustainability",
        "question": "Do you offer eco-friendly packaging?",
        "answer": "Yes! We use 100% recyclable cardboard, biodegradable packing peanuts, and minimal plastic. We're transitioning to compostable mailers for soft goods. You can opt for 'Minimal Packaging' at checkout to reduce waste further."
    },
]

# Combine all FAQs
ALL_FAQS = SAMPLE_FAQS + ADDITIONAL_FAQS

def get_faqs_by_category(category: str):
    """Get FAQs for a specific category"""
    return [faq for faq in ALL_FAQS if faq["category"] == category]

def get_all_categories():
    """Get list of all FAQ categories"""
    return list(set(faq["category"] for faq in ALL_FAQS))
