from gyma.vdv.Entities.EntityLandlord import EntityLandlord
from gyma.vdv.Entities.EntitySimpleuser import EntitySimpleuser


def get_user_wide_info(account_objects):
    res = []
    for _ in account_objects:
        obj_dict = _.to_dict(['vdvid', 'name', 'phone', 'mediaid'])

        landlord = get_landlord_info(_.vdvid)
        if landlord:
            obj_dict['landlord'] = landlord

        simpleuser = get_simpleuser_info(_.vdvid)
        if simpleuser:
            obj_dict['simpleuser'] = simpleuser

        res.append(obj_dict)

    return res


def get_landlord_info(account_vdvid):
    landlords = EntityLandlord.get().filter_by(accountid=account_vdvid).all()
    if len(landlords) > 0:
        return EntityLandlord.get_wide_object(landlords[0].vdvid)
    return None


def get_simpleuser_info(account_vdvid):
    simpleusers = EntitySimpleuser.get().filter_by(accountid=account_vdvid).all()
    if len(simpleusers) > 0:
        return EntitySimpleuser.get_wide_object(simpleusers[0].vdvid)
    return None
