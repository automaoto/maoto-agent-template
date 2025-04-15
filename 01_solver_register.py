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
            solver_id=rndid1,
            tags=["Grab", "Tada", "Zig", "ride hailing"],
        )
    )

    # await maoto.unregister(id=skill.id)
    # or alternatively:
    # await maoto.unregister(skill)
    # or alternatively:
    await maoto.unregister(solver_id=rndid1, obj_type=Skill)

    offercallable = await maoto.register(
        NewOfferCallable(
            solver_id=rndid2,
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

    # await maoto.unregister(id=offercallable.id)
    # or alternatively:
    # await maoto.unregister(offercallable)
    # or alternatively:
    await maoto.unregister(solver_id=rndid2, obj_type=OfferCallable)

    offerreference = await maoto.register(
        NewOfferReference(
            solver_id=rndid3,
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

    # await maoto.unregister(id=offerreference.id)
    # or alternatively:
    # await maoto.unregister(offerreference)
    # or alternatively:
    await maoto.unregister(solver_id=rndid3, obj_type=OfferReference)

asyncio.run(main())
