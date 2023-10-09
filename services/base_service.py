from sqlalchemy import select, Result
from sqlalchemy.orm import joinedload, selectinload

from config_reader import session_db
from database import User, CitySM


async def cmd_start(telegram_id: int, telegram_name: str):
    async with session_db() as session:
        user, user_scalar = await get_user(session, telegram_id)
        if user_scalar is None:
            res_create_user = await create_user(session, telegram_id, telegram_name)
            if res_create_user:
                return "create"
            else:
                return False
        user_telegram_name = user_scalar.telegram_name

        if user_telegram_name != telegram_name:
            user.telegram_name = telegram_name
            await session.commit()
            return "update"
        return None


async def create_user(session, telegram_id: int, telegram_name: str):
    try:
        new_user = User(telegram_id=str(telegram_id), telegram_name=telegram_name)
        session.add(new_user)
        await session.commit()
        return True
    except Exception as e:
        return False


async def get_user(session, user_id: int):
    user: Result = await session.execute(select(User)
                                         .where(User.telegram_id == str(user_id)))
    scalar_user = user.scalar_one_or_none()
    return user, scalar_user


async def get_user_with_fav_cities(session, user_id: int):
    user = await session.execute(select(User)
                                 .where(User.telegram_id == str(user_id))
                                 # .options(joinedload(User.favourite_cities)))
                                 .options(selectinload(User.favourite_cities)))
    scalar_user = user.scalar()
    return user, scalar_user


async def get_city(session, city_id):
    city = await session.execute(select(CitySM)
                                 .where(CitySM.city_id == str(city_id)))
    scalar_city = city.scalar()
    return city, scalar_city

# async def delete_favourite_city(session, city_id):
#     city = await session.execute(select(CitySM)
#                                      .where(CitySM.city_id == str(city_id)))
#     scalar_city = new_city.scalar()
#     return new_city, scalar_city
