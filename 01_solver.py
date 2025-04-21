from maoto_agent import *
from dotenv import load_dotenv

load_dotenv('.secrets_server')
load_dotenv('.env_server')

maoto = Maoto()

@maoto.register_handler(OfferCall)
async def offercall_handler(offercall: OfferCall):
    print(f"Received offercall: {offercall}")
    await maoto.send_response(
        NewOfferCallResponse(
            offercall_id=offercall.id,
            offercallable_id=str(offercall.offercallable_id),
            description="The ride was booked successfully. It will arrive at your location in 5 minutes."
        )
    )

@maoto.register_handler(OfferRequest)
async def offerrequest_handler(offerrequest: OfferRequest):
    print(f"Received offerrequest:  {offerrequest}")
    await maoto.send_response(
        NewOfferResponse(
            intent_id=offerrequest.intent.id,
            offerreference_ids=[],
            offercallable_ids=[],
            missinginfos=[
                MissingInfo(
                    description="Please provide your current location."
                ),
                MissingInfo(
                    description="Please provide your destination."
                )
            ],
            newoffercallables=[
                NewOfferCallable(
                    solver_id=None,
                    description=f"Ride to Marina Bay Sands {datetime.now()}",
                    params={"passenger name": "str"},
                    tags=["ride", "taxi"],
                    followup=True,
                    cost=20.00,
                )
            ],
            newofferreferences=[
                NewOfferReference(
                    solver_id=None,
                    description=f"Ride to Marina Bay Sands {datetime.now()}",
                    params={"passenger name": "str"},
                    tags=["ride", "taxi"],
                    url="https://www.tada.com/ride/price/1234567890",
                    cost=15.00,
                    followup=True,
                )
            ]
        )
    )

@maoto.register_handler(OfferCallableCostRequest)
async def offercallablecostrequest_handler(offercallablecostrequest: OfferCallableCostRequest):
    print(f"Received offercallablecostrequest: {offercallablecostrequest}")
    await maoto.send_response(
        NewOfferCallableCostResponse(
            offercallable_id=offercallablecostrequest.offercallable_id,
            intent_id=offercallablecostrequest.intent.id,
            cost=20.00
        )
    )

@maoto.register_handler(OfferReferenceCostRequest)
async def offerreferencecostrequest_handler(offerreferencecostrequest: OfferReferenceCostRequest):
    print(f"Received offerreferencecostrequest: {offerreferencecostrequest}")
    await maoto.send_response(
        NewOfferReferenceCostResponse(
            offerreference_id=offerreferencecostrequest.offerreference_id,
            intent_id=offerreferencecostrequest.intent.id,
            cost=15.00,
            url="https://www.tada.com/ride/price/1234567890"
        )
    )

# execute this with:
# uvicorn 01_solver:maoto --host 0.0.0.0 --port 8080 --workers 2
# ngrok http --scheme=http --host-header="localhost:8080" 8080