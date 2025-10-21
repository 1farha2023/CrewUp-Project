/**
 * Stripe Payment Gateway Frontend Actions
 * Reusable JavaScript module for handling Stripe payments
 */

class StripePaymentHandler {
    constructor(options = {}) {
        this.options = {
            loginUrl: options.loginUrl || '/auth/login/',
            checkoutEndpoint: options.checkoutEndpoint || '/payment/create-checkout/',
            onSuccess: options.onSuccess || this.defaultOnSuccess,
            onError: options.onError || this.defaultOnError,
            onLoading: options.onLoading || this.defaultOnLoading,
            ...options
        };
    }

    /**
     * Initialize the payment handler
     */
    init() {
        // Any initialization logic can go here
        console.log('Stripe Payment Handler initialized');
    }

    /**
     * Handle payment for a specific plan
     * @param {string} planType - The plan type (e.g., 'pro', 'basic', 'enterprise')
     * @param {string} billingCycle - The billing cycle ('monthly' or 'yearly')
     * @param {Object} options - Additional options for the payment
     */
    async handlePayment(planType, billingCycle = 'monthly', options = {}) {
        try {
            // Show loading state
            this.options.onLoading(true, options.button);

            // Check if user is authenticated (client-side check)
            if (!this.isUserAuthenticated()) {
                this.redirectToLogin();
                return;
            }

            // Validate plan type
            if (!this.isValidPlanType(planType)) {
                throw new Error('Invalid plan type selected');
            }

            // Validate billing cycle
            if (!this.isValidBillingCycle(billingCycle)) {
                throw new Error('Invalid billing cycle selected');
            }

            // Create checkout session
            const response = await this.createCheckoutSession(planType, billingCycle);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));

                // Handle authentication errors
                if (response.status === 401 || response.status === 403) {
                    this.redirectToLogin();
                    return;
                }

                throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            if (!data.checkout_url) {
                throw new Error('No checkout URL received from server');
            }

            // Call success callback
            this.options.onSuccess(data, planType, billingCycle);

            // Redirect to Stripe Checkout
            window.location.href = data.checkout_url;

        } catch (error) {
            console.error('Payment error:', error);
            this.options.onError(error, options.button);
        }
    }

    /**
     * Create checkout session via API
     * @param {string} planType
     * @param {string} billingCycle
     * @returns {Promise<Response>}
     */
    async createCheckoutSession(planType, billingCycle) {
        const url = `${this.options.checkoutEndpoint}${planType}/${billingCycle}/`;

        return fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken(),
            },
            credentials: 'same-origin',
        });
    }

    /**
     * Handle enterprise plan contact
     */
    handleEnterpriseContact() {
        // You can customize this to redirect to a contact form or open a modal
        alert('Please contact our sales team for Enterprise pricing and custom solutions.');

        // Alternative: redirect to contact page
        // window.location.href = '/contact/';

        // Or open a modal if you have modal functionality
        // this.openEnterpriseModal();
    }

    /**
     * Check if user is authenticated (client-side approximation)
     * @returns {boolean}
     */
    isUserAuthenticated() {
        // This is a client-side check - the server will do the real authentication
        // We can check for a user indicator in the DOM or a global variable
        return document.body.classList.contains('user-authenticated') ||
               window.userAuthenticated === true ||
               document.querySelector('[data-user-authenticated]') !== null;
    }

    /**
     * Redirect to login page with return URL
     */
    redirectToLogin() {
        const currentUrl = encodeURIComponent(window.location.pathname + window.location.search);
        window.location.href = `${this.options.loginUrl}?next=${currentUrl}`;
    }

    /**
     * Validate plan type
     * @param {string} planType
     * @returns {boolean}
     */
    isValidPlanType(planType) {
        const validPlans = ['basic', 'pro', 'enterprise'];
        return validPlans.includes(planType);
    }

    /**
     * Validate billing cycle
     * @param {string} billingCycle
     * @returns {boolean}
     */
    isValidBillingCycle(billingCycle) {
        const validCycles = ['monthly', 'yearly'];
        return validCycles.includes(billingCycle);
    }

    /**
     * Get CSRF token from cookies
     * @returns {string|null}
     */
    getCsrfToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    /**
     * Default success callback
     * @param {Object} data
     * @param {string} planType
     * @param {string} billingCycle
     */
    defaultOnSuccess(data, planType, billingCycle) {
        console.log('Payment session created successfully:', data);
    }

    /**
     * Default error callback
     * @param {Error} error
     * @param {HTMLElement} button
     */
    defaultOnError(error, button) {
        const message = error.message || 'An error occurred during payment processing';
        alert(`Payment error: ${message}\n\nPlease try again or contact support if the problem persists.`);

        // Reset button state
        if (button) {
            button.textContent = button.dataset.originalText || 'Try Again';
            button.disabled = false;
        }
    }

    /**
     * Default loading callback
     * @param {boolean} isLoading
     * @param {HTMLElement} button
     */
    defaultOnLoading(isLoading, button) {
        if (button) {
            if (isLoading) {
                button.dataset.originalText = button.textContent;
                button.textContent = 'Processing...';
                button.disabled = true;
            } else {
                button.textContent = button.dataset.originalText || button.textContent;
                button.disabled = false;
            }
        }
    }

    /**
     * Get current billing cycle from toggle
     * @param {string} toggleId - ID of the billing toggle element
     * @returns {string}
     */
    static getBillingCycle(toggleId = 'billing-toggle') {
        const toggle = document.getElementById(toggleId);
        return toggle && toggle.checked ? 'yearly' : 'monthly';
    }

    /**
     * Update pricing display based on billing cycle
     * @param {string} toggleId
     * @param {string} priceSelector
     */
    static updatePricingDisplay(toggleId = 'billing-toggle', priceSelector = '.monthly-price') {
        const toggle = document.getElementById(toggleId);
        const prices = document.querySelectorAll(priceSelector);

        if (!toggle) return;

        const updatePrices = () => {
            const isYearly = toggle.checked;

            prices.forEach(price => {
                const text = price.textContent.trim();
                if (text === 'Free' || text === 'Custom Pricing') return;

                if (isYearly) {
                    // Apply 50% discount for yearly
                    const monthlyPrice = parseInt(text.replace('$', ''));
                    const yearlyPrice = Math.floor(monthlyPrice * 12 * 0.5);
                    price.textContent = '$' + yearlyPrice;
                } else {
                    // Reset to monthly price
                    price.textContent = '$99';
                }
            });
        };

        // Initial update
        updatePrices();

        // Listen for changes
        toggle.addEventListener('change', updatePrices);
    }
}

// Create global instance
const stripePayment = new StripePaymentHandler();

// Export for module usage (if using modules)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = StripePaymentHandler;
}

// Make available globally
window.StripePaymentHandler = StripePaymentHandler;
window.stripePayment = stripePayment;