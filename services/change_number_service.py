from api.api_mp import ApiSm


async def send_sms(api: ApiSm, phone: str):
    status = await api.send_sms(phone)
    if status == 200:
        message = 'Код выслан на указанный номер. Отправьте его в чат. Если код не пришел, то проблема в номере, используйте другой, ранее не использованный в Спортмастер. У вас есть 3 попытки отправки кода в день'
    elif status == 400:
        message = 'Слишком много попыток запроса кода. Обратитесь в поддержку'
    else:
        message = 'Возможно бан аккаунта. Обратитесь в поддержку или попробуйте еще раз'

    return status, message


async def phone_change(api: ApiSm, code: str):
    flag_clear = True

    status_verify, json = await api.verify_check(code)
    if status_verify == 200:
        status_change, json_change = await api.change_phone()

        if status_change == 200:
            answer_message = "✅ Номер успешно изменен. Можете авторизовываться в аккаунт"
            flag_clear = False
        else:
            error_code = json_change['error'].get("code")
            if error_code == "PHONE_ALREADY_USED":
                answer_message = '❌ Номер уже занят. Попробуйте заново и введите ранее не зарегистрированный в Спортмастер'
            else:
                answer_message = '❌ Какая то непридвиденная ошибка при изменении номера. Попробуйте еще раз или обратитесь в поддержку'

    elif status_verify == 400:
        answer_message = json['error'].get("message")
        flag_clear = False
    else:
        answer_message = "❌ Непредвиденная ошибка. Попробуйте еще раз или обратитесь в поддержку"

    return flag_clear, answer_message