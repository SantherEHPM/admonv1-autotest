# admonv1-autotest — Pruebas E2E (Modelo de Validación, Enjisst Cap. 5)

Pruebas automatizadas con **Selenium + pytest** sobre el frontend
(`https://aes-puj.duckdns.org` en prod, `http://localhost:5173` en local).
Cada ejecución registra su resultado en la API de Google Apps Script
(`test_logs.json`) y se visualiza en el dashboard.

## 1. Cómo se estructuraron las pruebas

Estructura física `Paquete → Suite → DolphinCollection → EUV`
(`validacion_horizontal/flujo_residente/dolphin_collections/`):

```
admonv1-autotest/
├── conftest.py                 # flags, fixtures (driver, env, login) y reporte a GAS
├── requirements.txt / pytest.ini / .env.example
├── shared/                     # recursos transversales (no son EUVs)
│   ├── pages/BasePage.py       # go/find/click/type con pausa y resaltado humanamente visible
│   ├── fixtures/auth.py        # login reutilizable ("Igual que")
│   ├── steps/common.py         # PASOS comunes: definidos UNA sola vez, ver §2
│   ├── steps/context.py        # track(): tiempo, fallo y backendMs por paso
│   └── utils/
│       ├── gas_client.py       # build_payload + register_run (POST ?action=register)
│       ├── api_check.py        # verificación directa al backend (solo local)
│       ├── backend_ctl.py      # reinicio del backend local por proceso
│       └── frontend_ctl.py     # reinicio del frontend local por proceso
└── validacion_horizontal/      # PAQUETE (carpeta)
    └── flujo_residente/        # SUITE: propiedades compartidas (properties.py)
        ├── properties.py       # SELECTORS + STEPS + SCENARIOS + trazabilidad EUV
        ├── pages/              # Page Objects (Login, Convocations, Detail, Create, Applications)
        └── dolphin_collections/
            ├── dc_ingreso/         # EUV_01 ingreso correcto, EUV_02 ingreso incorrecto
            └── dc_postulacion/     # EUV_03 normal, EUV_04 duplicado, EUV_05 formato,
                                   # EUV_06 peso, EUV_07 incompletos, EUV_08 sin docs,
                                   # EUV_09 tooltips
```

### Reglas aplicadas

- **Pasos comunes una sola vez** (`shared/steps/common.py`): cada ingreso de
  información o click es un paso propio con `track()` (34 pasos). Los tests
  solo los invocan; nada se duplica.
- **Reinicio por escenario**: cada test reinicia backend (BD H2 limpia) y
  frontend antes de ejecutarse (pasos `reiniciar_backend`/`reiniciar_frontend`,
  solo en local). Los EUVs de postulación son autocontenidos.
- **Primera convocatoria**: los EUVs de postulación trabajan siempre sobre la
  **primera convocatoria consultada** (`primera_convocatoria`), sin buscar ni
  iterar.
- **Verificación API solo en local**: con `--env prod` (duckdns) se omite
  (`apiCheck.performed=false`); en local verifica login, listado y elegibilidad.

## 2. Puesta en marcha en otro equipo (Linux)

Solo se necesita la carpeta `admonv1-autotest` + instalación básica por pip.
El proyecto **no tiene secretos**: `.env` está ignorado y el registro en
Google usa la API pública ya desplegada.

```bash
# 0. Ubicación: deja esta carpeta JUNTO a los clones de front y back
#    HorizontalApp/
#    ├── admonv1-autotest/   <- este proyecto
#    ├── admonv1-backend/
#    └── admonv1-frontend/
#    (Si están en otro lugar, define AUTOTEST_WORKSPACE o
#     AUTOTEST_BACKEND / AUTOTEST_FRONTEND en el .env)

# 1. Solo pip (proyecto de pruebas)
pip install -r requirements.txt
cp .env.example .env   # ya viene listo para local

# 2. Prerrequisitos del sistema (una vez)
#    - Java 21 (el backend se compila/arranca solo con ./mvnw)
#    - Node 18+ y, dentro de admonv1-frontend:  npm install
#    - Google Chrome (webdriver-manager descarga el driver solo)
#    - Puertos libres: 8080 (back) y 5173 (front)

# 3. AWS (una vez, fuera del repo): las subidas de PDF necesitan credenciales
aws configure            # Access Key + Secret + region us-east-1
aws sts get-caller-identity   # debe responder el usuario

# 4. Correr (los servidores se levantan/reinician solos en local)
python3 -m pytest -v --headless --env local --base-url http://localhost:5173
```

Notas:

- Sin `~/.aws/credentials` los escenarios con subida de documentos
  (EUV_03/04/07/09) fallan; el resto pasa igual.
- Sin git en la carpeta, la columna "rama" del dashboard sale vacía (no rompe nada).
- Si GAS no responde, el resultado queda en `reports/pending.json` y la
  prueba igual se califica.

## 3. Comandos

Preparación (una vez):

```bash
pip install -r requirements.txt
cp .env.example .env   # ajustar BASE_URL / GAS_URL si hace falta
```

Variables principales (`.env` o flags):

| Variable / flag      | Efecto |
|----------------------|--------|
| `BASE_URL` / `--base-url` | Frontend bajo prueba (`http://localhost:5173` local) |
| `TEST_ENV` / `--env local\|prod` | `local` verifica por API; `prod` no |
| `HEADLESS` / `--headless` | `true` = sin ventana (CI); `false` = navegador visible |
| `--headed` | Fuerza ventana visible aunque `HEADLESS=true` |
| `SLOW_MO_MS` / `--slow-mo` | Pausa ms entre interacciones (visible) |
| `RESET_BACKEND/RESET_FRONTEND` | `test` = reinicia antes de cada prueba (defecto) |

Ejecución:

```bash
# Toda la suite (headless, local)
python3 -m pytest -v --headless --env local --base-url http://localhost:5173

# Por DolphinCollection completa
python3 -m pytest -v --headless --env local --base-url http://localhost:5173 -m dc_ingreso
python3 -m pytest -v --headless --env local --base-url http://localhost:5173 -m dc_postulacion

# Un escenario individual
python3 -m pytest -v --headless --env local --base-url http://localhost:5173 -m euv03

# En producción (sin verificación API, sin reinicios)
python3 -m pytest -v --headless --env prod

# Visible en navegador (headed, con pausas)
HEADLESS=false python3 -m pytest -v -s --env local -m euv01
```

## 4. Resultados

Cada prueba registra en GAS: `euvId`, `status`, `failedStep`,
`steps[{name,ms,ok,backend,backendMs,endpoint}]`, `env`, `branch` (local),
`apiCheck` y trazabilidad al Modelo de Producto. Dashboard con 3 vistas
(Resultados / Pasos / Escenarios).
