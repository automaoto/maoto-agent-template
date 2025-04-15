from maoto_agent import *
from dotenv import load_dotenv

load_dotenv('.secrets_server')
load_dotenv('.env_server')

maoto = Maoto()

@maoto.register_handler(OfferCall)
async def offercall_handler(offercall: OfferCall):
    print(f"Agent internal id: {offercall.solver_id}")
    await maoto.send_response(
        NewOfferCallResponse(
            offercall_id=offercall.id,
            offercallable_id=offercall.offercallable_id,
            description="The ride was booked successfully. It will arrive at your location in 5 minutes."
        )
    )

@maoto.register_handler(OfferRequest)
async def offerrequest_handler(offerrequest: OfferRequest):
    print(f"Agent internal id: {offerrequest.solver_id}")
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
            newoffercallables=[],
            newofferreferences=[]
        )
    )

@maoto.register_handler(OfferCallableCostRequest)
async def offercallablecostrequest_handler(offercallablecostrequest: OfferCallableCostRequest):
    print(f"Agent internal id: {offercallablecostrequest.solver_id}")
    await maoto.send_response(
        NewOfferCallableCostResponse(
            offercallable_id=offercallablecostrequest.offercallable_id,
            intent_id=offercallablecostrequest.intent.id,
            cost=20.00
        )
    )

@maoto.register_handler(OfferReferenceCostRequest)
async def offerreferencecostrequest_handler(offerreferencecostrequest: OfferReferenceCostRequest):
    print(f"Agent internal id: {offerreferencecostrequest.solver_id}")
    await maoto.send_response(
        NewOfferReferenceCostResponse(
            offerreference_id=offerreferencecostrequest.offerreference_id,
            intent_id=offerreferencecostrequest.intent.id,
            cost=15.00,
            url="https://www.tada.com/ride/price/1234567890"
        )
    )

# execute this with:
# uvicorn 01_solver:maoto --host 0.0.0.0 --port 30000 --workers 2
# ngrok http --scheme=http --host-header="localhost:8080" 8080