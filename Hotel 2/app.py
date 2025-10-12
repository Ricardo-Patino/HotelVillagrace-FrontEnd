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
    pass

# Verifica dependencias críticas y da un mensaje claro si faltan
def _import_or_exit():
    try:
        from flask import Flask  # noqa: F401
        import flask_sqlalchemy  # noqa: F401
        import flask_migrate  # noqa: F401
        import pymysql  # noqa: F401
        import cryptography  # noqa: F401
        import bcrypt  # soporte para hashes $2b$
    except ModuleNotFoundError as e:
        missing = str(e).split("'")[1]
        msg = (
            f"\n[ERROR] Falta el paquete requerido: {missing}\n"
            "Instálalo en el intérprete que estés usando para ejecutar app.py.\n\n"
            "Ejemplos:\n"
            f"  {sys.executable} -m pip install Flask Flask-SQLAlchemy Flask-Migrate PyMySQL python-dotenv cryptography bcrypt\n\n"
            f"  {sys.executable} -m pip install -r \"{(BASE_DIR / 'requirements.txt').as_posix()}\"\n"
        )
        print(msg, file=sys.stderr)
        sys.exit(1)

_import_or_exit()

# Ahora sí, imports reales
from flask import (
    Flask, render_template, jsonify, send_from_directory, url_for,
    request, redirect, flash, render_template_string, session
)
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt
from config import Config
from extensions import db, migrate
# from models import Room  # (opcional)

# -----------------------------------------------------------------------------
# Configuración de la app (portabilidad de templates/static)
# -----------------------------------------------------------------------------
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)

# Cargar configuración (incluye SQLALCHEMY_DATABASE_URI y SECRET_KEY si lo tienes)
app.config.from_object(Config)

# Inicializar extensiones
db.init_app(app)
migrate.init_app(app, db)

# -----------------------------------------------------------------------------
# Helpers mínimos para registro/login
# -----------------------------------------------------------------------------
def _first_of(form, keys):
    """Devuelve el primer valor no vacío encontrado en el formulario para cualquiera de las claves indicadas."""
    for k in keys:
        v = form.get(k)
        if v is not None and str(v).strip() != "":
            return str(v).strip()
    return None

def _normalize_phone(s):
    if not s:
        return "00000000"
    s = str(s).strip()
    # conserva + al inicio, elimina espacios
    if s.startswith("+"):
        return "+" + "".join(ch for ch in s[1:] if ch.isdigit())
    return "".join(ch for ch in s if ch.isdigit())

def _find_users_table():
    """Detecta automáticamente una tabla de usuarios (case-insensitive)."""
    candidate_tables = [
        os.getenv("USERS_TABLE", "").strip() or None,
        "users", "user", "usuarios", "usuario", "Users", "Usuarios", "Usuario"
    ]
    candidate_tables = [t for t in candidate_tables if t]

    schema = db.engine.url.database  # nombre de BD actual (MySQL)
    for tbl in candidate_tables:
        q = text("""
            SELECT TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = :sch AND LOWER(TABLE_NAME) = LOWER(:tbl)
            LIMIT 1
        """)
        row = db.session.execute(q, {"sch": schema, "tbl": tbl}).first()
        if row:
            return row[0]  # devuelve el nombre real con su casing
    return None

def _available_columns(table):
    """
    Devuelve un dict {col_lower: col_real} para mapear case-insensitive.
    """
    schema = db.engine.url.database
    q = text("""
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = :sch AND TABLE_NAME = :tbl
    """)
    rows = db.session.execute(q, {"sch": schema, "tbl": table}).all()
    return {r[0].lower(): r[0] for r in rows}  # lower -> real

def _put_if_exists(cols_map, payload, candidates, value):
    """
    Si alguna columna (por nombres candidatos, en minúscula) existe en cols_map,
    agrega al payload usando el nombre real de la columna.
    """
    if value is None:
        return
    for cand in candidates:
        col_real = cols_map.get(cand.lower())
        if col_real:
            payload[col_real] = value
            return

def _verify_password(stored_hash: str, candidate: str) -> bool:
    """
    Soporta:
      - PBKDF2/Scrypt de Werkzeug (prefijo 'pbkdf2:' o 'scrypt:')
      - bcrypt ($2a$ / $2b$ / $2y$)
    """
    if not stored_hash or not candidate:
        return False

    s = stored_hash.strip()
    # bcrypt
    if s.startswith("$2a$") or s.startswith("$2b$") or s.startswith("$2y$"):
        try:
            return bcrypt.checkpw(candidate.encode("utf-8"), s.encode("utf-8"))
        except Exception:
            return False

    # Por defecto intenta verificación nativa de Werkzeug (pbkdf2:, scrypt:, etc.)
    try:
        return check_password_hash(s, candidate)
    except Exception:
        return False

def _default_role_id():
    """
    Devuelve un Codigo_Rol por defecto:
    - 'Cliente' si existe
    - luego 'Usuario'
    - si no, el mínimo Codigo_Rol disponible
    """
    try:
        row = db.session.execute(
            text("SELECT Codigo_Rol FROM Rol WHERE LOWER(Nombre)=LOWER('Cliente') LIMIT 1")
        ).first()
        if row: return row[0]
        row = db.session.execute(
            text("SELECT Codigo_Rol FROM Rol WHERE LOWER(Nombre)=LOWER('Usuario') LIMIT 1")
        ).first()
        if row: return row[0]
        row = db.session.execute(
            text("SELECT MIN(Codigo_Rol) FROM Rol")
        ).first()
        if row and row[0] is not None: return row[0]
    except Exception:
        pass
    return None  # si no hay tabla Rol, no forzamos nada

# -----------------------------------------------------------------------------
# Endpoint de verificación de base de datos
# -----------------------------------------------------------------------------
@app.get("/db-ping")
def db_ping():
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

@app.route("/login.html", methods=["GET"])  # GET normal
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

# ===== Registro: acepta GET/POST, guarda en BD y redirige a login con mensaje =====
@app.route("/register.html", methods=["GET", "POST"])
@app.route("/register", methods=["GET", "POST"])
def register_html():
    if request.method == "POST":
        # Campos del formulario (en distintos nombres posibles)
        first_name = _first_of(request.form, ["firstName", "first_name", "nombre", "name"])
        last_name  = _first_of(request.form, ["lastName", "last_name", "apellido"])
        email      = _first_of(request.form, ["email", "correo"])
        username   = _first_of(request.form, ["username", "userName", "user_name", "usuario"])  # opcional si tu tabla no lo usa
        phone      = _normalize_phone(_first_of(request.form, ["telefono", "phone", "tel"]))
        password   = _first_of(request.form, ["password", "contrasena", "clave"])

        # NUEVO: cédula con más alias
        cedula     = _first_of(request.form, [
                        "cedula", "cedula_pasaporte", "Cedula_Pasaporte",
                        "dni", "documento", "document", "identificacion", "identification"
                      ])

        # NUEVO: rol con más alias
        rol_val    = _first_of(request.form, ["rol", "rol_id", "role", "role_id", "Codigo_Rol"])

        if not password:
            flash("La contraseña es obligatoria", "error")
            return render_template("/register.html"), 400

        # Construir 'Nombre' si la tabla lo requiere (Nombre es NOT NULL en tu SQL)
        if first_name and last_name:
            full_name = f"{first_name} {last_name}"
        else:
            full_name = first_name or last_name or username or email or "Usuario"

        pwd_hash = generate_password_hash(password)

        # Detectar tabla y columnas (case-insensitive)
        table = _find_users_table()
        if not table:
            flash("No se encontró una tabla de usuarios en la base de datos.", "error")
            return render_template("/register.html"), 500

        cols_map = _available_columns(table)  # {lower: RealName}

        payload = {}

        # Nombre (tu tabla lo usa con N mayúscula)
        _put_if_exists(cols_map, payload, ["Nombre"], full_name)

        # Correo (NOT NULL/UNIQUE)
        _put_if_exists(cols_map, payload, ["Correo", "email", "correo"], email or "")

        # Telefono (NOT NULL)
        _put_if_exists(cols_map, payload, ["Telefono", "phone", "tel"], phone or "00000000")

        # Contrasena (hash)
        _put_if_exists(cols_map, payload, ["Contrasena", "password", "password_hash", "pwd", "contrasena"], pwd_hash)

        # NUEVO: Cédula / Documento
        _put_if_exists(cols_map, payload, ["Cedula_Pasaporte", "cedula", "cedula_pasaporte", "dni", "documento", "document", "identificacion"], cedula)

        # NUEVO: Rol por defecto si no viene del form
        if not rol_val:
            rol_val = _default_role_id()
        _put_if_exists(cols_map, payload, ["Rol_Id", "rol_id", "role_id", "Codigo_Rol"], rol_val)

        # Estado (por defecto Activo)
        _put_if_exists(cols_map, payload, ["Estado", "estado"], _first_of(request.form, ["estado"]) or "Activo")

        # Código cliente (si aplica)
        _put_if_exists(cols_map, payload, ["Codigo_Cliente", "codigo_cliente"], _first_of(request.form, ["codigo_cliente"]))

        if not payload:
            flash("No hay columnas compatibles para insertar el usuario.", "error")
            return render_template("/register.html"), 500

        # Armar INSERT dinámico seguro
        col_names = ", ".join(payload.keys())
        placeholders = ", ".join([f":{i}" for i in payload.keys()])
        sql = text(f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})")

        try:
            db.session.execute(sql, payload)
            db.session.commit()

            # Página mínima con mensaje visible + redirección automática a /login.html
            return render_template_string("""
                <!doctype html>
                <html lang="es"><head>
                  <meta charset="utf-8">
                  <meta http-equiv="refresh" content="2;url={{ url_for('login_html') }}">
                  <title>Registro exitoso</title>
                  <style>
                    body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial;display:flex;min-height:100vh;align-items:center;justify-content:center;background:#f7f7f7}
                    .card{background:#fff;padding:24px 28px;border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,.08);text-align:center}
                    h1{font-size:20px;margin:0 0 8px}
                    p{margin:0;color:#444}
                    small{display:block;margin-top:10px;color:#666}
                  </style>
                </head><body>
                  <div class="card">
                    <h1>✅ Usuario creado con éxito</h1>
                    <p>Te estamos llevando al inicio de sesión…</p>
                    <small>Si no sucede automáticamente, <a href="{{ url_for('login_html') }}">haz clic aquí</a>.</small>
                  </div>
                </body></html>
            """)
        except Exception as e:
            db.session.rollback()
            flash(f"Error al registrar el usuario: {e}", "error")
            return render_template("/register.html"), 500

    # GET: mostrar formulario
    return render_template("/register.html")

# ===== Login: procesa POST desde el formulario (sin tocar templates) =====
# Cubrimos tres posibles actions del form:
@app.route("/login.html", methods=["POST"])       # si el form postea a /login.html
@app.route("/dashboard.html", methods=["POST"])   # si postea a dashboard.html
@app.route("/login", methods=["POST"])            # alterno por si cambias el form
def login_post():
    # Acepta distintos nombres de campo
    email = _first_of(request.form, ["email", "correo", "user", "username", "userName"])
    password = _first_of(request.form, ["password", "contrasena", "clave"])

    if not email or not password:
        flash("Ingresa correo/usuario y contraseña.", "warning")
        return redirect(url_for("login_html"))

    # Detecta tabla Usuario y columnas reales
    table = _find_users_table()
    if not table:
        flash("No se encontró una tabla de usuarios en la base de datos.", "error")
        return redirect(url_for("login_html"))

    # Trae al usuario por Correo (fallback por Nombre)
    sql = text(f"""
        SELECT u.*, r.Nombre AS Rol_Nombre
        FROM {table} u
        LEFT JOIN Rol r ON r.Codigo_Rol = u.Rol_Id
        WHERE u.Correo = :val
        LIMIT 1
    """)
    row = db.session.execute(sql, {"val": email}).mappings().first()

    if not row:
        sql2 = text(f"""
            SELECT u.*, r.Nombre AS Rol_Nombre
            FROM {table} u
            LEFT JOIN Rol r ON r.Codigo_Rol = u.Rol_Id
            WHERE u.Nombre = :val
            LIMIT 1
        """)
        row = db.session.execute(sql2, {"val": email}).mappings().first()

    if not row:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for("login_html"))

    # Estado debe estar Activo
    if str(row.get("Estado", "")).lower() != "activo":
        flash("Tu usuario está inactivo. Contacta al administrador.", "danger")
        return redirect(url_for("login_html"))

    # Verificar contraseña (PBKDF2/Scrypt o bcrypt)
    if not _verify_password(row.get("Contrasena", ""), password):
        flash("Credenciales inválidas.", "danger")
        return redirect(url_for("login_html"))

    # Autenticación OK → guardamos sesión mínima
    session["user_id"] = row.get("Codigo_Usuario")
    session["user_email"] = row.get("Correo")
    session["user_name"] = row.get("Nombre")
    session["user_role"] = row.get("Rol_Nombre")  # p.ej. 'Administrador', 'Cliente', etc.

    # Redirección según rol
    role = (row.get("Rol_Nombre") or "").lower()
    if role == "administrador":
        return redirect(url_for("admin_dashboard_html"))
    else:
        return redirect(url_for("portal_dashboard_html"))

# ===== Logout =====
@app.get("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("login_html"))

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

# -----------------------------------------------------------------------------
# Entry point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app.secret_key = app.config.get("SECRET_KEY", "cambia-esta-clave-ultra-secreta")
    app.run(host="0.0.0.0", port=5000, debug=True)
