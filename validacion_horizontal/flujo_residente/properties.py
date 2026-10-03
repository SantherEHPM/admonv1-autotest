"""
Suite: Flujo Residente (Enjisst §5.7).
Ámbito de propiedades compartidas por las DolphinCollections:
Ingreso y PostulacionAConvocatoria.

Granularidad: cada ingreso de información o click a un botón es un paso.
backend=True: el paso hace peticiones al backend (su backendMs alimenta
el KPI de velocidad de respuesta).
"""

SELECTORS = {
    "login_form": "login-form",
    "login_email": "login-email-input",
    "login_password": "login-password-input",
    "login_submit": "login-submit-button",
    "login_error": "login-error",
    "navbar": "navbar",
    "convocation_card_prefix": "convocation-card-",
    "convocation_view_details_prefix": "convocation-view-details-button-",
    "convocation_register_button": "convocation-register-button",
    "eligibility_message_class": "error-message",
    "create_continue": "create-application-continue-button",
    "create_submit": "create-application-submit-button",
    "doc_block_prefix": "document-type-block-",
    "doc_input_prefix": "document-upload-input-",
    "doc_remove_file_prefix": "document-upload-remove-file-",
    "summary_finish": "application-summary-finish-button",
    "application_card_prefix": "application-card-",
    "applications_empty_button": "applications-empty-view-convocations-button",
    "application_cancel_button": "application-cancel-button",
    "application_cancel_modal": "application-cancel-modal",
    "application_cancel_confirm": "application-cancel-confirm-button",
}

DEFAULT_BASE_URL = "https://aes-puj.duckdns.org"
TEST_USER = {"email": "residente@test.com", "password": "123456"}
WRONG_USER = {"email": "noexiste@test.com", "password": "wrongpass"}

REQUIRED_DOC_CODES = ["LICENCIA_TRANSITO", "SOAT_VIGENTE", "LICENCIA_CONDUCCION"]
MAX_DOC_BYTES = 2 * 1024 * 1024

GAS_API_URL = "https://script.google.com/macros/s/AKfycbzaAfaLi2QNKVFoU8XkcZh_gZ0Tr8MVFDZUNcqYvUxBSqs-tM_vUfAP6yiCL_gj76qD/exec"
DASHBOARD_URL = "https://script.google.com/macros/s/AKfycbyu2xfBl9lJ1oP-oP3jtoojIeYbfpKYcjWaEVaQ_wul5D7u4yEwH2ivm8JzHXweb2ao/exec"

# ---------------------------------------------------------------------------
# Catálogo de pasos (definidos una sola vez en shared/steps/common.py)
# ---------------------------------------------------------------------------
STEPS = {
    "reiniciar_backend": {"desc": "Reiniciar backend local por proceso (BD H2 limpia)", "backend": False, "endpoint": None},
    "reiniciar_frontend": {"desc": "Reiniciar frontend local por proceso (vite :5173)", "backend": False, "endpoint": None},
    "abrir_login": {"desc": "Abrir /login y verificar formulario visible", "backend": False},
    "escribir_email": {"desc": "Escribir el email carácter por carácter", "backend": False},
    "escribir_password": {"desc": "Escribir la contraseña carácter por carácter", "backend": False},
    "pulsar_ingresar": {"desc": "Click en Ingresar", "backend": True, "endpoint": "POST /api/auth/login"},
    "verificar_ingreso": {"desc": "Verificar navbar visible y llegada a convocatorias", "backend": False},
    "verificar_rechazo_login": {"desc": "Verificar error y permanencia en /login", "backend": False},
    "abrir_convocatorias": {"desc": "Abrir /convocations y listar tarjetas", "backend": True, "endpoint": "GET /api/calls"},
    "pulsar_ver_detalles": {"desc": "Click en Ver Detalles de la tarjeta", "backend": False},
    "verificar_detalle": {"desc": "Verificar detalle cargado", "backend": True, "endpoint": "GET /api/calls/:id"},
    "pulsar_registrar": {"desc": "Click en Registrar Postulación", "backend": True, "endpoint": "GET /api/applications/check?callId="},
    "verificar_mensaje_bloqueo": {"desc": "Verificar mensaje de postulación ya existente", "backend": False},
    "pulsar_continuar": {"desc": "Click en Continuar al paso de documentos", "backend": False},
    "cargar_licencia_transito": {"desc": "Subir PDF de licencia de tránsito", "backend": True, "endpoint": "POST /api/documents/presigned-url + PUT + POST /api/documents/:id/complete"},
    "cargar_soat": {"desc": "Subir PDF de SOAT vigente", "backend": True, "endpoint": "POST /api/documents/presigned-url + PUT + POST /api/documents/:id/complete"},
    "cargar_licencia_conduccion": {"desc": "Subir PDF de licencia de conducción", "backend": True, "endpoint": "POST /api/documents/presigned-url + PUT + POST /api/documents/:id/complete"},
    "pulsar_confirmar": {"desc": "Click en Confirmar y Enviar", "backend": True, "endpoint": "POST /api/applications"},
    "verificar_resumen": {"desc": "Verificar resumen ¡Postulación Exitosa!", "backend": False},
    "verificar_registro_api": {"desc": "Verificar por API directa que quedó registrada", "backend": True, "endpoint": "POST /api/auth/login + GET /api/applications"},
    "verificar_lista_postulaciones": {"desc": "Verificar en Mis Postulaciones", "backend": True, "endpoint": "GET /api/applications"},
    "ver_tooltip_registrar": {"desc": "Abrir tooltip de Registrar Postulación", "backend": False},
    "ver_tooltip_cupos": {"desc": "Abrir tooltip de cupos disponibles", "backend": False},
    "ver_tooltip_estado": {"desc": "Abrir tooltip de estado de convocatoria", "backend": False},
    "ver_tooltip_pazysalvo": {"desc": "Abrir tooltip de paz y salvo", "backend": False},
    "ver_tooltip_continuar": {"desc": "Abrir tooltip de Continuar", "backend": False},
    "ver_tooltip_documentos": {"desc": "Abrir tooltips de cada tipo de documento", "backend": False},
    "ver_tooltip_confirmar": {"desc": "Abrir tooltip de Confirmar y Enviar", "backend": False},
    "cargar_archivo_formato_erroneo": {"desc": "Subir .txt (rechazo local, sin petición)", "backend": False},
    "verificar_error_formato": {"desc": "Verificar error 'Solo se permiten archivos PDF'", "backend": False},
    "cargar_archivo_pesado": {"desc": "Subir PDF >2MB (rechazo local, sin petición)", "backend": False},
    "verificar_error_peso": {"desc": "Verificar error de tamaño máximo 2MB", "backend": False},
    "verificar_bloqueo_incompleto": {"desc": "Verificar Confirmar deshabilitado con docs incompletos", "backend": False},
    "verificar_bloqueo_sin_docs": {"desc": "Verificar Confirmar deshabilitado sin documentos", "backend": False},
    "abrir_detalle_postulacion": {"desc": "Abrir el detalle de la postulación", "backend": True, "endpoint": "GET /api/applications/:id"},
    "pulsar_cancelar_postulacion": {"desc": "Click en Cancelar postulación y verificar modal", "backend": False},
    "confirmar_cancelacion": {"desc": "Confirmar cancelación y verificar estado Cancelada", "backend": True, "endpoint": "PATCH /api/applications/:id/cancel"},
    "verificar_cancelacion_api": {"desc": "Verificar por API que quedó CANCELLED", "backend": True, "endpoint": "GET /api/applications/:id"},
    "verificar_estado_cancelada_lista": {"desc": "Verificar insignia Cancelada en la lista", "backend": True, "endpoint": "GET /api/applications"},
    "abrir_mis_postulaciones": {"desc": "Abrir Mis Postulaciones (GET /api/applications)", "backend": True, "endpoint": "GET /api/applications"},
    "obtener_postulaciones_api": {"desc": "Listar postulaciones por API directa", "backend": True, "endpoint": "POST /api/auth/login + GET /api/applications"},
    "verificar_titularidad_lista": {"desc": "Verificar que lo listado corresponde al usuario (UI vs API)", "backend": False},
}

SCENARIOS = {
    "EUV_01": {
        "name": "Ingreso con credenciales correctas", "collection": "Ingreso",
        "objective": "Comprobar que un residente con credenciales válidas ingresa y llega a convocatorias.",
        "steps": ["reiniciar_backend", "reiniciar_frontend", "abrir_login", "escribir_email", "escribir_password", "pulsar_ingresar", "verificar_ingreso"],
    },
    "EUV_02": {
        "name": "Intento de ingreso con credenciales incorrectas", "collection": "Ingreso",
        "objective": "Comprobar que credenciales inválidas son rechazadas sin acceso.",
        "steps": ["reiniciar_backend", "reiniciar_frontend", "abrir_login", "escribir_email", "escribir_password", "pulsar_ingresar", "verificar_rechazo_login"],
    },
    "EUV_03": {
        "name": "Postulación normal con verificación", "collection": "PostulacionAConvocatoria",
        "objective": "Comprobar el happy path completo y que el registro existe vía API y en lista.",
        "steps": ["reiniciar_backend", "reiniciar_frontend", "abrir_login", "escribir_email", "escribir_password", "pulsar_ingresar", "verificar_ingreso", "abrir_convocatorias", "pulsar_ver_detalles", "verificar_detalle", "pulsar_registrar", "pulsar_continuar", "cargar_licencia_transito", "cargar_soat", "cargar_licencia_conduccion", "pulsar_confirmar", "verificar_resumen", "verificar_registro_api", "verificar_lista_postulaciones"],
    },
    "EUV_04": {
        "name": "Intento de postulación con postulación activa", "collection": "PostulacionAConvocatoria",
        "objective": "Comprobar que no se permite una segunda postulación del apartamento en la misma convocatoria.",
        "steps": ["reiniciar_backend", "reiniciar_frontend", "abrir_login", "escribir_email", "escribir_password", "pulsar_ingresar", "verificar_ingreso", "abrir_convocatorias", "pulsar_ver_detalles", "verificar_detalle", "pulsar_registrar", "verificar_mensaje_bloqueo", "verificar_registro_api", "verificar_lista_postulaciones"],
    },
    "EUV_05": {
        "name": "Intento con archivo de formato erróneo", "collection": "PostulacionAConvocatoria",
        "objective": "Comprobar que archivos no-PDF son rechazados con mensaje.",
        "steps": ["reiniciar_backend", "reiniciar_frontend", "abrir_login", "escribir_email", "escribir_password", "pulsar_ingresar", "verificar_ingreso", "abrir_convocatorias", "pulsar_ver_detalles", "verificar_detalle", "pulsar_registrar", "pulsar_continuar", "cargar_archivo_formato_erroneo", "verificar_error_formato"],
    },
    "EUV_06": {
        "name": "Intento con archivo muy pesado", "collection": "PostulacionAConvocatoria",
        "objective": "Comprobar que archivos de más de 2MB son rechazados con mensaje.",
        "steps": ["reiniciar_backend", "reiniciar_frontend", "abrir_login", "escribir_email", "escribir_password", "pulsar_ingresar", "verificar_ingreso", "abrir_convocatorias", "pulsar_ver_detalles", "verificar_detalle", "pulsar_registrar", "pulsar_continuar", "cargar_archivo_pesado", "verificar_error_peso"],
    },
    "EUV_07": {
        "name": "Intento con archivos incompletos", "collection": "PostulacionAConvocatoria",
        "objective": "Comprobar que con documentos obligatorios faltantes no se puede confirmar.",
        "steps": ["reiniciar_backend", "reiniciar_frontend", "abrir_login", "escribir_email", "escribir_password", "pulsar_ingresar", "verificar_ingreso", "abrir_convocatorias", "pulsar_ver_detalles", "verificar_detalle", "pulsar_registrar", "pulsar_continuar", "cargar_licencia_transito", "verificar_bloqueo_incompleto"],
    },
    "EUV_08": {
        "name": "Intento antes de carga de archivos", "collection": "PostulacionAConvocatoria",
        "objective": "Comprobar que sin cargar ningún documento el botón Confirmar está deshabilitado.",
        "steps": ["reiniciar_backend", "reiniciar_frontend", "abrir_login", "escribir_email", "escribir_password", "pulsar_ingresar", "verificar_ingreso", "abrir_convocatorias", "pulsar_ver_detalles", "verificar_detalle", "pulsar_registrar", "pulsar_continuar", "verificar_bloqueo_sin_docs"],
    },
    "EUV_10": {
        "name": "Listado corresponde al usuario logueado", "collection": "PostulacionAConvocatoria",
        "objective": "Comprobar que Mis Postulaciones muestra exactamente las postulaciones del usuario autenticado.",
        "steps": ["reiniciar_backend", "reiniciar_frontend", "abrir_login", "escribir_email", "escribir_password", "pulsar_ingresar", "verificar_ingreso", "abrir_mis_postulaciones", "obtener_postulaciones_api", "verificar_titularidad_lista"],
    },
    "EUV_11": {
        "name": "Cancelar una postulación", "collection": "PostulacionAConvocatoria",
        "objective": "Comprobar que una postulación REGISTERED se cancela con confirmación y queda Cancelada en UI, API y lista.",
        "steps": ["reiniciar_backend", "reiniciar_frontend", "abrir_login", "escribir_email", "escribir_password", "pulsar_ingresar", "verificar_ingreso", "abrir_convocatorias", "pulsar_ver_detalles", "verificar_detalle", "pulsar_registrar", "pulsar_continuar", "cargar_licencia_transito", "cargar_soat", "cargar_licencia_conduccion", "pulsar_confirmar", "verificar_resumen", "abrir_mis_postulaciones", "abrir_detalle_postulacion", "pulsar_cancelar_postulacion", "confirmar_cancelacion", "verificar_cancelacion_api", "verificar_estado_cancelada_lista"],
    },
    "EUV_09": {
        "name": "Postulación usando todos los tooltips", "collection": "PostulacionAConvocatoria",
        "objective": "Comprobar que cada ayuda contextual se abre con su texto y completar la postulación usándolas.",
        "steps": ["reiniciar_backend", "reiniciar_frontend", "abrir_login", "escribir_email", "escribir_password", "pulsar_ingresar", "verificar_ingreso", "abrir_convocatorias", "pulsar_ver_detalles", "verificar_detalle", "ver_tooltip_registrar", "ver_tooltip_cupos", "ver_tooltip_estado", "pulsar_registrar", "ver_tooltip_pazysalvo", "ver_tooltip_continuar", "pulsar_continuar", "ver_tooltip_documentos", "ver_tooltip_confirmar", "cargar_licencia_transito", "cargar_soat", "cargar_licencia_conduccion", "pulsar_confirmar", "verificar_resumen", "verificar_registro_api", "verificar_lista_postulaciones"],
    },
}

EUV_PRODUCT_ELEMENTS = {
    "EUV_01": [
        {"vista": "Casos de Uso", "arbol": "Autenticación", "elemento": "CU-01 Iniciar sesión", "tipo": "CasoUso"},
        {"vista": "No Funcional", "arbol": "Seguridad", "elemento": "RNF-SE-AU-01 Autenticación JWT", "tipo": "RNF"},
    ],
    "EUV_02": [
        {"vista": "Casos de Uso", "arbol": "Autenticación", "elemento": "CU-01 Iniciar sesión - rechazo", "tipo": "CasoUso"},
        {"vista": "No Funcional", "arbol": "Seguridad", "elemento": "RNF-SE-AU-01 Autenticación JWT", "tipo": "RNF"},
    ],
    "EUV_03": [
        {"vista": "Casos de Uso", "arbol": "Gestión Postulaciones", "elemento": "CU-03 Registrar postulación", "tipo": "CasoUso"},
        {"vista": "Semántica", "arbol": "Postulación", "elemento": "Postulación", "tipo": "Entidad"},
        {"vista": "Semántica", "arbol": "Postulación", "elemento": "Documento", "tipo": "Entidad"},
        {"vista": "Semántica", "arbol": "Convocatoria", "elemento": "Convocatoria", "tipo": "Entidad"},
    ],
    "EUV_04": [
        {"vista": "Casos de Uso", "arbol": "Gestión Postulaciones", "elemento": "CU-03 Registrar postulación - duplicado", "tipo": "CasoUso"},
        {"vista": "Regla", "arbol": "Postulación", "elemento": "RN-01 Una postulación por apartamento y convocatoria", "tipo": "Regla"},
    ],
    "EUV_05": [
        {"vista": "Casos de Uso", "arbol": "Gestión Postulaciones", "elemento": "CU-03 Registrar postulación - formato", "tipo": "CasoUso"},
        {"vista": "Regla", "arbol": "Documento", "elemento": "RN-02 Solo archivos PDF", "tipo": "Regla"},
    ],
    "EUV_06": [
        {"vista": "Casos de Uso", "arbol": "Gestión Postulaciones", "elemento": "CU-03 Registrar postulación - peso", "tipo": "CasoUso"},
        {"vista": "Regla", "arbol": "Documento", "elemento": "RN-03 Tamaño máximo 2MB", "tipo": "Regla"},
    ],
    "EUV_07": [
        {"vista": "Casos de Uso", "arbol": "Gestión Postulaciones", "elemento": "CU-03 Registrar postulación - incompletos", "tipo": "CasoUso"},
        {"vista": "Regla", "arbol": "Documento", "elemento": "RN-04 Documentos obligatorios completos", "tipo": "Regla"},
    ],
    "EUV_08": [
        {"vista": "Casos de Uso", "arbol": "Gestión Postulaciones", "elemento": "CU-03 Registrar postulación - sin docs", "tipo": "CasoUso"},
        {"vista": "Regla", "arbol": "Documento", "elemento": "RN-04 Documentos obligatorios completos", "tipo": "Regla"},
    ],
    "EUV_10": [
        {"vista": "Casos de Uso", "arbol": "Gestión Postulaciones", "elemento": "CU-04 Consultar postulaciones", "tipo": "CasoUso"},
        {"vista": "Semántica", "arbol": "Postulación", "elemento": "Postulación", "tipo": "Entidad"},
        {"vista": "No Funcional", "arbol": "Seguridad", "elemento": "RNF-SE-AU-01 Solo datos del usuario autenticado", "tipo": "RNF"},
    ],
    "EUV_11": [
        {"vista": "Casos de Uso", "arbol": "Gestión Postulaciones", "elemento": "CU-05 Cancelar postulación", "tipo": "CasoUso"},
        {"vista": "Regla", "arbol": "Postulación", "elemento": "RN-05 Solo REGISTERED del creador en fechas de convocatoria", "tipo": "Regla"},
        {"vista": "Semántica", "arbol": "Postulación", "elemento": "Postulación", "tipo": "Entidad"},
    ],
    "EUV_09": [
        {"vista": "Casos de Uso", "arbol": "Gestión Postulaciones", "elemento": "CU-03 Registrar postulación - tooltips", "tipo": "CasoUso"},
        {"vista": "No Funcional", "arbol": "Usabilidad", "elemento": "RNF-US-CA-01 Ayuda contextual", "tipo": "RNF"},
        {"vista": "Semántica", "arbol": "Postulación", "elemento": "Postulación", "tipo": "Entidad"},
    ],
}

EUV_META = {
    euv: {"name": SCENARIOS[euv]["name"], "suite": "Flujo Residente", "collection": SCENARIOS[euv]["collection"]}
    for euv in SCENARIOS
}
