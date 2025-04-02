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

    await maoto.register(
        NewSkill(
            description="Books a ride using ride-hailing services.",
            args={
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

    await maoto.register(
        NewOfferCallable(
            resolver_id=rndid2,
            description="Books a Grab ride.",
            args={
                "longitude": "int",
                "latitude": "int",
                "destination": "str"
            },
            tags=["Grab", "ride hailing"],
            followup=False, # OfferCallable is not hidden
            cost=None # agent will be asked for cost
        )
    )

    await maoto.register(
        NewOfferReference(
            resolver_id=rndid3,
            description="Books a Tada ride.",
            args={
                "longitude": "int",
                "latitude": "int",
                "destination": "str"
            },
            tags=["Tada", "ride hailing"],
            followup=False, # OfferReference is not hidden
            cost=None, # agent will be asked for cost
            url=None
        )
    )

asyncio.run(main())
