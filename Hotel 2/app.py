# app.py
# Aplicación principal Flask para Hotel_VillaGrace.
# Portátil (sin rutas absolutas) y ejecutable directamente con "Run/F5" en VS Code
# o con:  python app.py

import os
import sys
from pathlib import Path

# -----------------------------------------------------------------------------
# Bootstrap de portabilidad y verificación de dependencias
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

# Asegura que podamos importar módulos locales (config.py, extensions.py, models/)
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Carga variables de entorno desde .env si está disponible
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv(BASE_DIR / ".env")
except Exception:
    # No es obligatorio tener python-dotenv instalado para ejecutar si ya tienes
    # las variables en el entorno del sistema. Ignoramos si falta.
    pass

# Verifica dependencias críticas y da un mensaje claro si faltan
def _import_or_exit():
    try:
        from flask import Flask  # noqa: F401
        import flask_sqlalchemy  # noqa: F401
        import flask_migrate  # noqa: F401
        import pymysql  # noqa: F401
        # Para auth caching_sha2_password, cryptography debe estar presente
        import cryptography  # noqa: F401
    except ModuleNotFoundError as e:
        missing = str(e).split("'")[1]
        msg = (
            f"\n[ERROR] Falta el paquete requerido: {missing}\n"
            "Instálalo en el intérprete que estés usando para ejecutar app.py.\n\n"
            "Ejemplos:\n"
            "  # Si usas el venv del proyecto\n"
            f"  {sys.executable} -m pip install Flask Flask-SQLAlchemy Flask-Migrate PyMySQL python-dotenv cryptography\n\n"
            "  # O con requirements.txt\n"
            f"  {sys.executable} -m pip install -r \"{(BASE_DIR / 'requirements.txt').as_posix()}\"\n"
        )
        print(msg, file=sys.stderr)
        sys.exit(1)

_import_or_exit()

# Ahora sí, imports reales
from flask import Flask, render_template, jsonify, send_from_directory, url_for  # noqa: E402
from sqlalchemy import text  # noqa: E402
from config import Config  # noqa: E402
from extensions import db, migrate  # noqa: E402
# from models import Room  # (opcional) para que Migrate detecte modelos

# -----------------------------------------------------------------------------
# Configuración de la app (portabilidad de templates/static)
# -----------------------------------------------------------------------------
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)

# Cargar configuración (incluye SQLALCHEMY_DATABASE_URI)
app.config.from_object(Config)

# Inicializar extensiones
db.init_app(app)
migrate.init_app(app, db)

# -----------------------------------------------------------------------------
# Endpoint de verificación de base de datos
# -----------------------------------------------------------------------------
@app.get("/db-ping")
def db_ping():
    """
    Verifica conectividad a la base de datos ejecutando SELECT 1.
    Responde 200 si hay conexión, 500 si hay error.
    """
    try:
        result = db.session.execute(text("SELECT 1")).scalar()
        ok = (result == 1)
        return jsonify({"database": "ok" if ok else "unknown"}), 200 if ok else 500
    except Exception as e:
        return jsonify({"database": "error", "detail": str(e)}), 500

# =========================
# Manejo de errores
# =========================
@app.errorhandler(404)
def not_found(e):
    return render_template("/404.html"), 404

# =========================
# Rutas de páginas (las tuyas)
# =========================
@app.route("/about.html")
def about_html():
    return render_template("/about.html")

@app.route("/admin-audit.html")
def admin_audit_html():
    return render_template("/admin-audit.html")

@app.route("/admin-calendario.html")
def admin_calendario_html():
    return render_template("/admin-calendario.html")

@app.route("/admin-channels.html")
def admin_channels_html():
    return render_template("/admin-channels.html")

@app.route("/admin-dashboard.html")
def admin_dashboard_html():
    return render_template("/admin-dashboard.html")

@app.route("/admin-hotel.html")
def admin_hotel_html():
    return render_template("/admin-hotel.html")

@app.route("/admin-rates.html")
def admin_rates_html():
    return render_template("/admin-rates.html")

@app.route("/admin-reserva-detalle.html")
def admin_reserva_detalle_html():
    return render_template("/admin-reserva-detalle.html")

@app.route("/admin-reservas-dashboard.html")
def admin_reservas_dashboard_html():
    return render_template("/admin-reservas-dashboard.html")

@app.route("/admin-reservas-list.html")
def admin_reservas_list_html():
    return render_template("/admin-reservas-list.html")

@app.route("/admin-rooms.html")
def admin_rooms_html():
    return render_template("/admin-rooms.html")

@app.route("/admin-taxes.html")
def admin_taxes_html():
    return render_template("/admin-taxes.html")

@app.route("/admin-users.html")
def admin_users_html():
    return render_template("/admin-users.html")

@app.route("/amenities.html")
def amenities_html():
    return render_template("/amenities.html")

@app.route("/booking-checkout.html")
def booking_checkout_html():
    return render_template("/booking-checkout.html")

@app.route("/booking-confirmation.html")
def booking_confirmation_html():
    return render_template("/booking-confirmation.html")

@app.route("/booking-details.html")
def booking_details_html():
    return render_template("/booking-details.html")

@app.route("/booking-results.html")
def booking_results_html():
    return render_template("/booking-results.html")

@app.route("/booking-search.html")
def booking_search_html():
    return render_template("/booking-search.html")

@app.route("/booking.html")
def booking_html():
    return render_template("/booking.html")

@app.route("/contact.html")
def contact_html():
    return render_template("/contact.html")

@app.route("/events.html")
def events_html():
    return render_template("/events.html")

@app.route("/fin-close.html")
def fin_close_html():
    return render_template("/fin-close.html")

@app.route("/fin-dashboard.html")
def fin_dashboard_html():
    return render_template("/fin-dashboard.html")

@app.route("/fin-invoices.html")
def fin_invoices_html():
    return render_template("/fin-invoices.html")

@app.route("/fin-payments.html")
def fin_payments_html():
    return render_template("/fin-payments.html")

@app.route("/forgot-password.html")
def forgot_password_html():
    return render_template("/forgot-password.html")

@app.route("/gallery.html")
def gallery_html():
    return render_template("/gallery.html")

@app.route("/index.html")
def index_html():
    return render_template("/index.html")

@app.route("/")
def index():
    return render_template("/index.html")

@app.route("/location.html")
def location_html():
    return render_template("/location.html")

@app.route("/login.html")
def login_html():
    return render_template("/login.html")

@app.route("/offers.html")
def offers_html():
    return render_template("/offers.html")

@app.route("/ops-arrivals-departures.html")
def ops_arrivals_departures_html():
    return render_template("/ops-arrivals-departures.html")

@app.route("/ops-dashboard.html")
def ops_dashboard_html():
    return render_template("/ops-dashboard.html")

@app.route("/ops-housekeeping.html")
def ops_housekeeping_html():
    return render_template("/ops-housekeeping.html")

@app.route("/ops-incidents.html")
def ops_incidents_html():
    return render_template("/ops-incidents.html")

@app.route("/ops-inventory.html")
def ops_inventory_html():
    return render_template("/ops-inventory.html")

@app.route("/ops-maintenance.html")
def ops_maintenance_html():
    return render_template("/ops-maintenance.html")

@app.route("/ops-reports.html")
def ops_reports_html():
    return render_template("/ops-reports.html")

@app.route("/ops-rooms-status.html")
def ops_rooms_status_html():
    return render_template("/ops-rooms-status.html")

@app.route("/ops-shift-log.html")
def ops_shift_log_html():
    return render_template("/ops-shift-log.html")

@app.route("/portal-dashboard.html")
def portal_dashboard_html():
    return render_template("/portal-dashboard.html")

@app.route("/portal-facturas.html")
def portal_facturas_html():
    return render_template("/portal-facturas.html")

@app.route("/portal-pagos.html")
def portal_pagos_html():
    return render_template("/portal-pagos.html")

@app.route("/portal-perfil.html")
def portal_perfil_html():
    return render_template("/portal-perfil.html")

@app.route("/portal-preferencias.html")
def portal_preferencias_html():
    return render_template("/portal-preferencias.html")

@app.route("/portal-reserva-detalle.html")
def portal_reserva_detalle_html():
    return render_template("/portal-reserva-detalle.html")

@app.route("/portal-reservas.html")
def portal_reservas_html():
    return render_template("/portal-reservas.html")

@app.route("/portal-soporte.html")
def portal_soporte_html():
    return render_template("/portal-soporte.html")

@app.route("/privacy.html")
def privacy_html():
    return render_template("/privacy.html")

@app.route("/register.html")
def register_html():
    return render_template("/register.html")

@app.route("/restaurant.html")
def restaurant_html():
    return render_template("/restaurant.html")

@app.route("/room-details.html")
def room_details_html():
    return render_template("/room-details.html")

@app.route("/rooms.html")
def rooms_html():
    return render_template("/rooms.html")

@app.route("/starter-page.html")
def starter_page_html():
    return render_template("/starter-page.html")

@app.route("/terms.html")
def terms_html():
    return render_template("/terms.html")






# -----------------------------------------------------------------------------
# Ruta física de assets (si la utilizas en algún endpoint)
# -----------------------------------------------------------------------------
ASSETS_ROOT = os.path.join(
    app.static_folder,
    'Hotel', 'Hotel Villa Grace', 'LuxuryHotel-pro', 'assets'
)
# Si necesitas exponer assets por una ruta, descomenta este ejemplo:
# @app.route("/assets/<path:filename>")
# def assets(filename):
#     return send_from_directory(ASSETS_ROOT, filename)

# -----------------------------------------------------------------------------
# Entry point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Debug server para desarrollo local
    app.run(host="0.0.0.0", port=5000, debug=True)
