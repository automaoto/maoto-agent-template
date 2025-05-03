import asyncio
from dotenv import load_dotenv
from maoto_agent import *

load_dotenv('.secrets_server')
load_dotenv('.env_server')

maoto = Maoto()

async def main():
    rndid1 = uuid.uuid5(uuid.NAMESPACE_DNS, "rh1")
    skill = await maoto.register(
        NewSkill(
            description=f"Books a ride using ride-hailing services.",
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

    # await maoto.unregister(obj_type=Skill, id=skill.id)
    # or alternatively:
    await maoto.unregister(skill)
    # or alternatively:
    # await maoto.unregister(solver_id=rndid1, obj_type=Skill)

    rndid2 = uuid.uuid5(uuid.NAMESPACE_DNS, "rh2")
    offercallable = await maoto.register(
        NewOfferCallable(
            solver_id=rndid2,
            description=f"Books a Grab ride.",
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

    # await maoto.unregister(obj_type=OfferCallable, id=offercallable.id)
    # or alternatively:
    await maoto.unregister(offercallable)
    # or alternatively:
    # await maoto.unregister(solver_id=rndid2, obj_type=OfferCallable)

    rndid3 = uuid.uuid5(uuid.NAMESPACE_DNS, "rh3")
    offerreference = await maoto.register(
        NewOfferReference(
            solver_id=rndid3,
            description=f"Books a Tada ride.",
            params={},
            tags=["Tada", "ride hailing"],
            followup=False, # OfferReference is not hidden
            cost=35.0, # agent will be asked for cost
            url="https://tada.com/ride/vghkgv76687"
        )
    )

    # await maoto.unregister(obj_type=OfferReference, id=offerreference.id)
    # or alternatively:
    await maoto.unregister(offerreference)
    # or alternatively:
    # await maoto.unregister(solver_id=rndid3, obj_type=OfferReference)


    # How to get all registered objects of a specific type
    """ 
    print("testa")
    skills = await maoto.get_registered(Skill)
    print("Skills:", skills)

    offercallables = await maoto.get_registered(OfferCallable)
    print("OfferCallable:", offercallables)

    offerreferences = await maoto.get_registered(OfferReference)
    print("OfferReference:", offerreferences)
    """


    """
    await maoto.create_refcode(
        NewRefCode(
            value="grab123",
            offercallable_id=offercallable.id,
        )
    )

    refcodes = await maoto.get_refcodes()
    print("Refcodes:", refcodes)

    await maoto.delete_refcode(
        offercallable_id=offercallable.id
    )
    """

asyncio.run(main())
