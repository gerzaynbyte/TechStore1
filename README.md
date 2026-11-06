# Laboratorio Unidad 5 · Integración, Pruebas y Calidad

Proyecto de pruebas automatizadas para reglas de negocio de pedidos, con adaptación al PIA de la empresa PetMarket (comercio electrónico de productos para mascotas).

# Descripción
El proyecto verifica con pruebas automatizadas que las reglas de negocio se cumplen, que la persistencia y los servicios externos se comportan como se espera, y que el pipeline de GitHub Actions rechaza cambios que rompan las pruebas.

Consta de dos capas:

Proyecto base de pedidos (ZIP 05_Proyecto_Base_U5): reglas de pedidos VIP con descuento del 15%, cobro mediante pasarela de pago simulada, persistencia con SQLAlchemy y política de cancelación.
Adaptación al PIA (PetMarket): tres reglas de negocio propias del BRD de la empresa, con 9 casos de prueba (éxito, error y límite por regla):
RN-07 — Límite de 50 unidades por SKU por pedido.
RN-08 — Máximo 3 intentos de pago en 15 minutos; al tercer rechazo el carrito se libera y el cliente debe reiniciar el checkout.
RN-11 — Cancelación gratuita por el cliente solo dentro de 2 horas desde la confirmación del pago y en estatus "Pago confirmado" o "En preparación".
- Requisitos
  Python 3.11 o superior
  Git (para el flujo CI)
  No se requiere Docker ni base de datos instalada: las pruebas de persistencia usan SQLite en memoria.
- Instalación
Windows PowerShell
  py -3.11 -m venv .venv
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt

macOS / Linux
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt

Si falla la activación en PowerShell, use el intérprete directo: .venv\Scripts\python.exe -m pytest -v.

- Comandos de ejecución
# Suite completa de pruebas
pytest -v --cov=src --cov-report=term-missing --cov-report=html --cov-fail-under=80

# Verificación de estilo de código (lint)
ruff check src tests

Resultado esperado: pytest termina en verde con cobertura ≥ 80% sobre src/ y Ruff sin errores. La cobertura del 80% significa que al menos el 80% de las líneas instrumentadas fueron ejecutadas, no que el 80% de los defectos fueron detectados.

🏗️ Arquitectura
El proyecto aplica Domain Model con separación estricta de capas; cada regla de negocio vive en una sola clase, lo que localiza el costo de cualquier cambio futuro:

src/
├── domain.py            # Reglas del proyecto base: Order.confirm(), descuento VIP,
│                        #   validación de total y estado CONFIRMED
├── petmarket_domain.py  # Adaptación PIA: Pedido (RN-07, RN-11) y
│                        #   SesionPago (RN-08), con errores auditable s(RN-xx en mensaje)
├── application.py       # Servicio de cobro OrderService, con inyección de pasarela
├── repository.py        # Persistencia SQLAlchemy (tabla orders, commit/rollback)
└── security.py          # Política de cancelación por rol y antigüedad (24 h)

tests/
├── test_order.py        # Unitarias del dominio base
├── test_petmarket_rn07_rn08_rn11.py  # 9 casos del PIA (CP-01 … CP-09)
├── test_repository.py   # Integración: commit y rollback en SQLite en memoria
├── test_service.py      # Simulación de pasarela con unittest.mock
└── test_security.py     # Matriz de autorización con fechas fijas

Decisiones de diseño relevantes:

Arranque–Acto–Afirmación (AAA) en todas las pruebas; fechas fijas pasadas explícitamente (now) para resultados deterministas.
Mocks para servicios externos: ninguna prueba genera un cargo real; la pasarela es un Mock.
SQLite en memoria para las pruebas de transacciones: no sustituye todas las pruebas de un motor productivo como PostgreSQL.
Los bordes de las reglas temporales y numéricas de PetMarket (2 h exactas en RN-11, tercer rechazo en RN-08, unidad 51 en RN-07) se tratan como excluyentes/incluyentes según lo aprobado en el BRD, y cada supuesto está documentado en la sección 12 del informe.
🔁 Integración continua (CI)
El workflow .github/workflows/ci.yml ejecuta en cada push y pull request: checkout, instalación de Python y dependencias, Ruff, pytest con umbral de cobertura del 80% y compilación de src/ (compileall).

Importante: El pipeline realiza verificación de build (compileall), no despliegue productivo.

⚠️ Notas sobre el alcance
Importante: El proyecto es un ejemplo de pedidos, no la solución de los 17 PIA. La regla de cancelación impide cancelar pedidos enviados incluso para administrador; esto resuelve explícitamente una ambigüedad del slide original.

La adaptación al PIA (PetMarket) cubre las tres reglas seleccionadas del BRD; el resto de las 21 RN del documento de requisitos no está implementado en este laboratorio.

