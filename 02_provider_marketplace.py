from maoto_agent import *
from dotenv import load_dotenv

load_dotenv('.secrets_server')
load_dotenv('.env_server')

maoto = Maoto()

# send intents somewhere in your application:
"""
await maoto.send_intent(
    NewIntent(
        description="Book a ride using ride-hailing services.",
        tags=["Grab", "Tada", "Zig", "ride hailing"],
    )
)"
"""

@maoto.register_handler(IntentResponse)
async def response_handler(response: IntentResponse):
    print(f"Received response: {response}")
    # this might contain long text with offercallables, offerreferences, missinginfos, etc.

# call an offercallable
"""
await maoto.send_newoffercall(
    NewOfferCall(
        offercallable_id=uuid.uuid5(uuid.NAMESPACE_DNS, "rh1"),
        args={
            "current_user_location": {
                "longitude": 1234567890,
                "latitude": 1234567890
            },
            "destination": "Singapore"
        }
    )
)
"""

@maoto.register_handler(OfferCallResponse)
async def offercallresponse_handler(offercallresponse: OfferCallResponse):
    print(f"Received offercall response: {offercallresponse}")

# this is initiated by user confirmation link after logging in
@maoto.register_handler(LinkConfirmation)
async def linkconfirmation_handler(linkconfirmation: LinkConfirmation):
    print(f"Received link confirmation: {linkconfirmation}")

# this handler is just triggered, when payment wall for that agent is activated
@maoto.register_handler(PaymentRequest)
async def paymentrequest_handler(paymentrequest: PaymentRequest):
    print(f"Received payment request: {paymentrequest.payment_link}")
    # This is to open the payment link in browser

# execute this with:
# uvicorn 02_provider_marketplace:maoto --host 0.0.0.0 --port 8080 --workers 2
# ngrok http --scheme=http --host-header="localhost:8080" 8080






# TODO: enable referencing of offercallables, etc. in offercallresponses

# TODO: add resolver_id to OfferResponse

# TODO add embedding for specific openai model