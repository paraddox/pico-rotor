# Pico Rotor Controller

Controller pentru rotor de antenă satelit cu Raspberry Pi Pico W, cu suport pentru două axe (azimut/elevație).

## Funcționalități

- **Protocol Hamlib rotctld** - Server TCP compatibil cu GPredict, SDRConsole și alte programe de radioamatori
- **Interfață Web** - Panou de control responsive, optimizat pentru mobil, cu afișare poziție în timp real
- **Setări via Web** - Configurează toți parametrii din browser (nu necesită editare de cod)
- **Control Viteză PWM** - Control motor cu două viteze pentru poziționare de precizie
- **Două Moduri de Operare** - Control manual și tracking automat
- **Calibrare Live** - Afișare tensiune în timp real pentru calibrare ușoară a potențiometrelor
- **Mod AP de Rezervă** - Creează hotspot WiFi dacă rețeaua configurată nu este disponibilă

## Cerințe Hardware

- Raspberry Pi Pico W
- Driver motor H-Bridge (L298N, TB6612 sau similar)
- Două motoare DC (azimut și elevație)
- Două potențiometre pentru feedback poziție
- Sursă de alimentare 5V (în funcție de motoare)

## Conexiuni

### Conexiuni Motoare (H-Bridge)

| Funcție        | Pin Pico | H-Bridge |
|----------------|----------|----------|
| Azimut A       | GP2      | IN1      |
| Azimut B       | GP3      | IN2      |
| Elevație A     | GP4      | IN3      |
| Elevație B     | GP5      | IN4      |

### Senzori Poziție (Potențiometre)

| Funcție   | Pin Pico | Interval Tensiune       |
|-----------|----------|-------------------------|
| Azimut    | GP26     | 0.54V (0°) - 2.32V (360°) |
| Elevație  | GP27     | 0.53V (0°) - 0.98V (90°)  |

## Instalare

### Opțiunea 1: Folosind Thonny (Windows - Recomandat pentru începători)

1. Descarcă și instalează Thonny de la https://thonny.org/

2. Conectează Pico W la USB ținând apăsat butonul BOOTSEL

3. În Thonny, mergi la **Tools → Options → Interpreter**:
   - Selectează "MicroPython (Raspberry Pi Pico)"
   - Click pe "Install or update MicroPython"
   - Selectează Pico-ul tău și instalează ultima versiune
   - Click OK

4. Creează fișierul de configurare WiFi:
   - În Thonny, mergi la **File → New**
   - Lipește acest conținut (editează cu datele tale WiFi):
     ```json
     {
         "wifi_ssid": "NumeleReteleiTale",
         "wifi_password": "ParolaTa"
     }
     ```
   - Mergi la **File → Save as...**
   - Selectează "Raspberry Pi Pico" în dialog
   - Salvează ca `settings.json`

5. Încarcă toate fișierele firmware:
   - Deschide fiecare fișier `.py` din acest proiect în Thonny
   - Pentru fiecare fișier: **File → Save as...** → Selectează "Raspberry Pi Pico" → Salvează cu același nume
   - Încarcă aceste fișiere: `settings.py`, `motors.py`, `position.py`, `controller.py`, `rotctld.py`, `webserver.py`, `main.py`

6. Resetează Pico (deconectează și reconectează USB). Vezi adresa IP în panoul Shell din Thonny.

### Opțiunea 2: Folosind mpremote (Linux/macOS/Windows linie de comandă)

1. Instalează MicroPython pe Pico W (dacă nu este deja instalat):
   - Descarcă de la https://micropython.org/download/RPI_PICO_W/
   - Ține apăsat butonul BOOTSEL în timp ce conectezi USB
   - Copiază fișierul .uf2 pe drive-ul montat

2. Copiază toate fișierele `.py` pe Pico:
   ```bash
   # Instalează mpremote întâi: pip install mpremote
   mpremote cp settings.py motors.py position.py controller.py rotctld.py webserver.py main.py :
   ```

3. Configurează credențialele WiFi folosind **una** din aceste metode:

   **Opțiunea A: Pre-configurare înainte de deploy (recomandat)**

   Creează un fișier `settings.json` cu credențialele tale WiFi:
   ```bash
   cat > settings.json << 'EOF'
   {
       "wifi_ssid": "NumeleReteleiTale",
       "wifi_password": "ParolaTa"
   }
   EOF
   mpremote cp settings.json :
   ```
   Pico se va conecta automat la WiFi la pornire.

   **Opțiunea B: Configurare prin mod AP**

   Dacă nu există `settings.json` sau conexiunea WiFi eșuează:
   - Pico creează AP-ul "PicoRotor-Setup" (parolă: rotorsetup)
   - Conectează-te la această rețea și accesează http://192.168.4.1/settings
   - Introdu credențialele WiFi și click pe Save, apoi Reboot

4. Pico se va conecta la WiFi-ul tău și va afișa IP-ul în consola serială.

## Setări Web

Toți parametrii sunt configurabili prin interfața web la `http://<ip>/settings`:

### Setări Rețea
- SSID și parolă WiFi
- Port server web (implicit: 80)
- Port Rotctld (implicit: 4533)

### Pini GPIO
- Pini control motor pentru azimut și elevație
- Pini ADC pentru potențiometrele de poziție

### Calibrare
- Mapare tensiune-grade pentru fiecare axă
- Afișare tensiune live ajută la calibrare
- Intervale grade min/max

### Control Motor
- Frecvență PWM (Hz)
- Valori viteză rapidă, viteză lentă, viteză minimă
- Tensiune referință ADC

### Poziționare
- Toleranță (precizia opririi în grade)
- Prag lent (când să treacă la viteză de precizie)
- Interval actualizare buclă de control

### Limite și Parcare
- Limite deplasare azimut și elevație
- Coordonate poziție parcare

## Utilizare

### Interfață Web

Deschide `http://<pico-ip>/` într-un browser. Interfața oferă:

- **Afișare Poziție** - Citiri azimut și elevație în timp real
- **Butoane Direcție** - Apasă și ține pentru mișcare continuă
- **Mergi La Poziție** - Introdu coordonate și click GO
- **Buton Parcare** - Întoarcere la 0°, 0°
- **Oprire de Urgență** - Oprește imediat orice mișcare

### Configurare GPredict

1. Edit → Preferences → Interfaces → Rotators
2. Adaugă rotor nou:
   - **Name:** Pico Rotor
   - **Host:** <pico-ip>
   - **Port:** 4533
   - **Az Type:** 0° to 360°
   - **El Type:** 0° to 90°

### Configurare SDRConsole

Folosește funcția de tracking rotor cu:
- Protocol: Hamlib rotctld
- IP: <pico-ip>
- Port: 4533

### Testare Linie de Comandă

Testează cu netcat:
```bash
# Obține poziția
echo "p" | nc <pico-ip> 4533

# Setează poziția (az=180, el=45)
echo "P 180 45" | nc <pico-ip> 4533

# Oprire
echo "S" | nc <pico-ip> 4533

# Parcare
echo "K" | nc <pico-ip> 4533
```

## Referință Protocol rotctld

| Comandă | Descriere | Răspuns |
|---------|-----------|---------|
| `p` | Obține poziția | `AZ\nEL` |
| `P az el` | Setează poziția | `RPRT 0` |
| `S` | Oprire | `RPRT 0` |
| `K` | Parcare | `RPRT 0` |
| `_` | Obține info | String info |
| `q` | Închide conexiunea | (se închide) |

## Configurare

Toate setările sunt stocate în `settings.json` și pot fi modificate prin interfața web. Fișierul este creat automat la prima rulare.

Parametri cheie (accesibili și prin pagina `/settings`):

```python
# Toleranță poziționare (grade)
TOLERANCE = 1.0          # Oprește când e în acest interval

# Praguri viteză
SLOW_THRESHOLD = 5.0     # Folosește viteză lentă în acest interval de țintă
PWM_FAST = 65535         # Viteză maximă
PWM_SLOW = 32768         # Viteză de precizie
PWM_MIN = 19660          # Minim efectiv (~30%)

# Rată actualizare
POSITION_UPDATE_MS = 50  # Interval buclă de control
```

## Calibrare

Dacă potențiometrele tale au intervale de tensiune diferite:

1. Mută la poziția 0°, notează valoarea tensiunii
2. Mută la poziția maximă, notează valoarea tensiunii
3. Actualizează prin pagina de setări sau `settings.json`:

```python
# Calibrare azimut
AZ_V_MIN = 0.54    # Tensiune la 0°
AZ_V_MAX = 2.32    # Tensiune la 360°

# Calibrare elevație
EL_V_MIN = 0.53    # Tensiune la 0°
EL_V_MAX = 0.98    # Tensiune la 90°
```

## Depanare

### Motoarele nu se mișcă
- Verifică alimentarea H-bridge
- Verifică conexiunile cablurilor
- Încearcă să crești `PWM_MIN` dacă motoarele se blochează

### Citiri poziție instabile
- Crește numărul de eșantioane pentru mediere în `position.py`
- Verifică conexiunile potențiometrelor
- Adaugă condensatoare de 0.1µF pe intrările ADC

### WiFi nu se conectează
- Verifică SSID/parola în config
- Verifică că rețeaua 2.4GHz este disponibilă
- Pico W nu suportă 5GHz

### GPredict nu se conectează
- Confirmă că portul 4533 este corect
- Verifică setările firewall
- Testează mai întâi cu `nc`

## Structura Fișierelor

```
pico-rotor/
├── settings.py    # Manager setări cu persistență JSON
├── motors.py      # Control motor cu PWM
├── position.py    # Citire poziție ADC
├── controller.py  # Logica principală de control
├── rotctld.py     # Server protocol Hamlib
├── webserver.py   # Interfață web (pagini control + setări)
├── main.py        # Punct de intrare aplicație
├── settings.json  # (creat la rulare) Setări salvate
└── README.md      # Acest fișier
```

## Endpoint-uri API

| Endpoint | Metodă | Descriere |
|----------|--------|-----------|
| `/` | GET | Pagină control |
| `/settings` | GET | Pagină setări |
| `/api/status` | GET | Poziție și stare curentă |
| `/api/mode` | POST | Setează modul (manual/auto) |
| `/api/move` | POST | Pornește mișcare manuală |
| `/api/stop` | POST | Oprește orice mișcare |
| `/api/goto` | POST | Mergi la poziție |
| `/api/park` | POST | Mergi la poziția de parcare |
| `/api/settings` | GET | Obține toate setările |
| `/api/settings` | POST | Actualizează setările |
| `/api/settings/reset` | POST | Resetează la valorile implicite |
| `/api/reboot` | POST | Repornește controllerul |

## Licență

Licență MIT - Utilizare liberă pentru aplicații de radioamatori.
