# ESGSolax → Home Assistant Bridge

Локальный MQTT-мост для инвертора ESGSolax (Solax-совместимого) и Home Assistant.
Данные передаются напрямую через локальную сеть — без облака и внешних серверов.

## Что делает

- Опрашивает инвертор каждые 30 секунд по протоколу **Solarman V5** (порт 8899) или **Solax Local REST API**
- Публикует данные в MQTT: заряд батареи, мощность PV, AC параметры, температура, нагрузка
- Автоматически создаёт сенсоры в Home Assistant через **MQTT Discovery**
- При потере связи — HA сразу отображает сенсоры как "недоступные"

## Требования

- Docker и Docker Compose
- Home Assistant с установленной интеграцией **MQTT**
- Инвертор и сервер в одной локальной сети

## Установка

### 1. Найти IP и серийный номер инвертора

IP-адрес донгла — в роутере в разделе DHCP-клиентов (ищите устройство с именем типа `SolarmanWiFi` или `USR-WIFI`).

Серийный номер — **10-значное число** на наклейке донгла (только цифры).

### 2. Отредактировать config.yaml

```yaml
inverter:
  ip: "192.168.1.XXX"    # ← IP вашего донгла
  serial: XXXXXXXXXX     # ← 10-значный серийный номер
  rest_password: "XXXX"  # ← обычно тот же серийный номер
```

### 3. Запустить

```bash
cd inverter_bridge
docker-compose up -d
```

### 4. Проверить логи

```bash
docker-compose logs -f solax_bridge
```

Должно появиться:
```
Connected via Solarman V5 protocol (port 8899)
Published HA discovery payloads for 15 sensors
Published 15 values — SOC=87%
```

### 5. Подключить MQTT в Home Assistant

Настройки → Устройства и сервисы → Добавить интеграцию → **MQTT**

- Хост: IP вашего сервера (где запущен Docker)
- Порт: `1883`
- Без логина/пароля (по умолчанию)

После подключения в HA появится устройство **"Solax Inverter"** с сенсорами:

| Сенсор | Описание |
|--------|----------|
| Battery SOC | Заряд батареи (%) |
| Battery Voltage | Напряжение батареи (V) |
| Battery Current | Ток батареи (A, отриц. = заряд) |
| Battery Power | Мощность батареи (W) |
| AC Output Power | Мощность на выходе (W) |
| AC Voltage | Напряжение AC (V) |
| AC Frequency | Частота AC (Hz) |
| PV Total Power | Суммарная мощность PV (W) |
| Grid Power | Мощность сети (W, отриц. = экспорт) |
| Load Power | Мощность нагрузки (W) |
| Inverter Temperature | Температура инвертора (°C) |
| Run Mode | Режим работы |

## Блокировка облака (solar.wattseek.com)

Чтобы инвертор перестал отправлять данные в облако, добавьте в роутере DNS-запись:

```
solar.wattseek.com  →  0.0.0.0
```

Или в Pi-hole / AdGuard Home добавьте домен `wattseek.com` в чёрный список.

## Устранение неполадок

**"Solarman V5 failed" в логах** — попробуйте `protocol: "solax_rest"` в config.yaml и убедитесь что серийный номер верный.

**Сенсоры не появляются в HA** — проверьте что MQTT интеграция подключена к правильному брокеру. В Developer Tools → MQTT подпишитесь на топик `inverter/#` и нажмите Subscribe — должны появляться сообщения.

**SOC показывает неверное значение** — это может быть инвертор Gen3 (регистр SOC = 103 вместо 168). Откройте issue с моделью прошивки.
