from loguru import logger
from tortoise import BaseDBAsyncClient, Tortoise
from tortoise.transactions import atomic
from aerich import Command

import settings
from infrastructure.database.connection import sample_conf
from infrastructure.database.models import (Role,
                                            SystemUser,
                                            Visitor,
                                            Passport,
                                            Claim,
                                            Pass,
                                            Zone,
                                            ClaimWay,
                                            ClaimToZone,
                                            ParkingPlace,
                                            Parking,
                                            ParkingTimeSlot,
                                            AcquireParkingInterval,
                                            BlackList, MilitaryId, VisitSession, DriveLicense, Transport)
from core.utils.encrypt import encrypt_password


@atomic()
async def fill_with_default_data() -> None:
    root_role = await Role.create(name='root')
    admin_role = await Role.create(name='admin')
    operator_role = await Role.create(name='operator')
    seo_role = await Role.create(name="SEO")
    security_role = await Role.create(name="security_officer")

    crypted_password, salt = encrypt_password("123456")

    root = await SystemUser.create(first_name='firstName',
                                   last_name='lastName',
                                   username="root",
                                   password=crypted_password,
                                   salt=salt)
    await root.scopes.add(root_role, admin_role, security_role)

    visitor = await Visitor.create(first_name='Ivan',
                                   last_name='Gofnof')

    claim = await Claim.create(pass_type='temporary',
                               status='valid')

    passport = await Passport.create(number=4688123456,
                                     date_of_birth='19960213')

    militaryid = await MilitaryId.create(number="AM 1234567890")

    drive_license = await DriveLicense.create(number=1234567890)

    transport = await Transport.create(number="A123AA77RUS")
    await transport.claims.add(claim)

    visit_session = await VisitSession.create(visitor=visitor)

    pass_id = await Pass.create(pass_type='card',
                                valid_till='20220622',
                                rfid=9002241879)

    await Zone.bulk_create([
        Zone(name='reception'),
        Zone(name='parking'),
        Zone(name='2nd floor'),
    ])

    claim_way = await ClaimWay.create()
    await claim_way.roles.add(admin_role)
    await claim_way.system_users.add(root)

    claim_to_zone = await ClaimToZone.create(claim=claim,
                                             pass_id=pass_id)

    parking_place = await ParkingPlace.create(real_number=13)

    parking = await Parking.create(max_places=999,
                                   current_places=500)

    parking_time_slot = await ParkingTimeSlot.create(start='20220704T1100',
                                                     end='20220704T1139')

    acquire_parking_interval = await AcquireParkingInterval.create(start_interval='20220704T1045',
                                                                   end_interval='20220905T0123',
                                                                   reserved_interval=parking_time_slot)

    await BlackList.create(level='RED',
                           visitor=visitor)


async def make_migrations() -> None:
    """Making initial migrations"""
    import subprocess

    logger.info("make migrations")
    with subprocess.Popen([f'{settings.BASE_DIR}/migrations.sh']):
        logger.info("migrate")


async def setup_db(conn: BaseDBAsyncClient) -> None:
    row_count, rows = await conn.execute_query(
        "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'asbp'")
    if not row_count:
        await conn.execute_script("CREATE SCHEMA IF NOT EXISTS asbp;")
        logger.info("creating initial database")
        await Tortoise.generate_schemas()
        await fill_with_default_data()
        await make_migrations()
    else:
        command = Command(tortoise_config=sample_conf,
                          app="asbp",
                          location=f"{settings.BASE_DIR}/infrastructure/database/migrations/")
        await command.init()
        await command.migrate()

        await Tortoise.close_connections()
