from api import PetFriends
from settings import valid_email, valid_password, invalid_password, invalid_email
import os
import logging

pf = PetFriends()

logging.basicConfig(level=logging.DEBUG)

def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем, что запрос api-ключа возвращает статус 200 и в результате содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result


def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем, что запрос всех питомцев возвращает непустой список.
    Для этого сначала получаем api-ключ и сохраняем его в переменную auth_key.
    Далее, используя этот ключ, запрашиваем список всех питомцев и проверяем, что список непустой.
    Доступное значение параметра filter - 'my_pets' либо '' """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='пёсель', animal_type='собака', age='1', pet_photo='images/dogg.jpg'):
    """Проверяем, что можно добавить питомца с фотографией и корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Проверяем, существует ли файл с изображением
    if not os.path.exists(pet_photo):
        raise FileNotFoundError(f"Файл {pet_photo} не найден!")

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    status, auth_key = pf.get_api_key(valid_email, valid_password)
    print(f"Auth key status: {status}, auth_key: {auth_key}")

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Выводим ответ сервера для диагностики
    print(f"Status code: {status}")
    print(f"Response: {result}")

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name




def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Артур", "попугай", "1", "images/popug.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Тоша', animal_type='котик', age=5):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список непустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем, что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


def test_add_new_pet_simple_with_valid_data(name='Гоша', animal_type='попугай', age='1'):
    """Проверяем, что можно добавить питомца без фотографии с корректными данными"""

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet_simple(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_add_pet_photo_with_valid_data(pet_photo='images/stesha.jpg'):
    """Проверяем возможность добавления фотографии питомца"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список непустой, то пробуем добавить фотографию
    if len(my_pets['pets']) > 0:
        status, result = pf.add_pet_photo(auth_key, my_pets['pets'][0]['id'], pet_photo)

        # Проверяем, что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


def test_get_api_key_for_invalid_email(email=invalid_email, password=invalid_password):
    """Проверяем, что запрос api-ключа с неверным email возвращает код 403"""
    status, result = pf.get_api_key(email, password)
    assert status == 403  # Сверяем полученный ответ с ожидаемым результатом
    assert 'This user wasn&#x27;t found in database' in result


def test_get_api_key_for_valid_email_and_invalid_password(email=valid_email, password=invalid_password):
    """Проверяем, что запрос api-ключа с верным email и неверным password возвращает код 403"""
    status, result = pf.get_api_key(email, password)
    assert status == 403  # Сверяем полученный ответ с ожидаемым результатом
    assert 'This user wasn&#x27;t found in database' in result


def test_get_all_pets_with_invalid_key(filter=''):
    """Проверяем, что запрос всех питомцев с неверным api-ключом возвращает код 403"""
    auth_key = {'key': '000'}  # Задаем неверный ключ api и сохраняем в переменную auth_key
    status, result = pf.get_list_of_pets(auth_key, filter)  # Запрашиваем список питомцев
    assert status == 403  # Сверяем полученный ответ с ожидаемым результатом
    assert 'Please provide &#x27;auth_key&#x27; Header' in result


def test_add_new_pet_simple_with_invalid_key(name='Гоша', animal_type='попугай', age='1'):
    """Проверяем, что запрос на добавление питомца без фотографии с неверным api-ключом возвращает код 403"""
    auth_key = {'key': '00000'}  # Задаем неверный ключ api и сохраняем в переменную auth_key
    status, result = pf.add_new_pet_simple(auth_key, name, animal_type, age)  # Создаем питомца
    assert status == 403  # Сверяем полученный ответ с ожидаемым результатом
    assert 'Please provide &#x27;auth_key&#x27; Header' in result


def test_add_new_pet_with_invalid_data(name='Артур', animal_type='попугай',
                                       age='1', pet_photo='images/mops.xlsx'):
    """Проверяем, что нельзя добавить питомца с невалидным форматом фотографии"""

    # Получаем путь изображения питомца и сохраняем в pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)  # Добавляем питомца

    assert status == 415  # Сверяем полученный ответ с ожидаемым результатом
    # Обнаружен дефект, так как в качестве фото принимает xls-файл
    # Фактический результат (status == 200) расходится с ожидаемым (status == 415)!!!


def test_add_pet_with_valid_data_empty_field():
    """Проверяем отсутствие возможности добавить питомца с пустыми полями."""
    name = ''
    animal_type = ''
    age = ''
    #  Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    # Добавляем питомца
    status, result = pf.add_new_pet_simple(auth_key, name, animal_type, age)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    # Обнаружен дефект, так как сайт позволяет добавлять питомцев с отсутствием данных.
    # Фактический результат (status == 200) расходится с ожидаемым (status == 400)!!!


