import asyncio
from dotenv import load_dotenv
from maoto_agent import *

load_dotenv('.secrets_server')
load_dotenv('.env_server')

maoto = Maoto()

async def main():
    rndid1 = uuid.uuid5(uuid.NAMESPACE_DNS, "rh1")
    rndid2 = uuid.uuid5(uuid.NAMESPACE_DNS, "rh2")
    rndid3 = uuid.uuid5(uuid.NAMESPACE_DNS, "rh3")
    curr_time = datetime.now()

    skill = await maoto.register(
        NewSkill(
            description=f"Books a ride using ride-hailing services.{curr_time}",
            params={
                "current_user_location": {
                    "longitude": "int",
                    "latitude": "int"
                },
                "destination": "str"
            },
            resolver_id=rndid1,
            tags=["Grab", "Tada", "Zig", "ride hailing"],
        )
    )

    await maoto.unregister(skill)

    offercallable = await maoto.register(
        NewOfferCallable(
            resolver_id=rndid2,
            description=f"Books a Grab ride.{curr_time}",
            params={
                "current_user_location": {
                    "longitude": "int",
                    "latitude": "int"
                },
                "destination": "str"
            },
            tags=["Grab", "ride hailing"],
            followup=False, # OfferCallable is not hidden
            cost=None # agent will be asked for cost
        )
    )

    await maoto.unregister(offercallable)

    offerreference = await maoto.register(
        NewOfferReference(
            resolver_id=rndid3,
            description=f"Books a Tada ride.{curr_time}",
            params={
                "current_user_location": {
                    "longitude": "int",
                    "latitude": "int"
                },
                "destination": "str"
            },
            tags=["Tada", "ride hailing"],
            followup=False, # OfferReference is not hidden
            cost=None, # agent will be asked for cost
            url=None
        )
    )

    await maoto.unregister(offerreference)

asyncio.run(main())
