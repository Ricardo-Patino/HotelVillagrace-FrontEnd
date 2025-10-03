from flask import Flask, render_template, url_for
from pathlib import Path

app = Flask(__name__)

@app.errorhandler(404)
def not_found(e):
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/404.html"), 404

@app.route("/about.html")
def about_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/about.html")

@app.route("/admin-audit.html")
def admin_audit_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/admin-audit.html")

@app.route("/admin-calendario.html")
def admin_calendario_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/admin-calendario.html")

@app.route("/admin-channels.html")
def admin_channels_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/admin-channels.html")

@app.route("/admin-dashboard.html")
def admin_dashboard_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/admin-dashboard.html")

@app.route("/admin-hotel.html")
def admin_hotel_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/admin-hotel.html")

@app.route("/admin-rates.html")
def admin_rates_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/admin-rates.html")

@app.route("/admin-reserva-detalle.html")
def admin_reserva_detalle_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/admin-reserva-detalle.html")

@app.route("/admin-reservas-dashboard.html")
def admin_reservas_dashboard_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/admin-reservas-dashboard.html")

@app.route("/admin-reservas-list.html")
def admin_reservas_list_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/admin-reservas-list.html")

@app.route("/admin-rooms.html")
def admin_rooms_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/admin-rooms.html")

@app.route("/admin-taxes.html")
def admin_taxes_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/admin-taxes.html")

@app.route("/admin-users.html")
def admin_users_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/admin-users.html")

@app.route("/amenities.html")
def amenities_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/amenities.html")

@app.route("/booking-checkout.html")
def booking_checkout_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/booking-checkout.html")

@app.route("/booking-confirmation.html")
def booking_confirmation_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/booking-confirmation.html")

@app.route("/booking-details.html")
def booking_details_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/booking-details.html")

@app.route("/booking-results.html")
def booking_results_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/booking-results.html")

@app.route("/booking-search.html")
def booking_search_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/booking-search.html")

@app.route("/booking.html")
def booking_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/booking.html")

@app.route("/contact.html")
def contact_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/contact.html")

@app.route("/events.html")
def events_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/events.html")

@app.route("/fin-close.html")
def fin_close_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/fin-close.html")

@app.route("/fin-dashboard.html")
def fin_dashboard_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/fin-dashboard.html")

@app.route("/fin-invoices.html")
def fin_invoices_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/fin-invoices.html")

@app.route("/fin-payments.html")
def fin_payments_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/fin-payments.html")

@app.route("/forgot-password.html")
def forgot_password_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/forgot-password.html")

@app.route("/gallery.html")
def gallery_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/gallery.html")

@app.route("/index.html")
def index_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/index.html")

@app.route("/")
def index():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/index.html")

@app.route("/location.html")
def location_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/location.html")

@app.route("/login.html")
def login_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/login.html")

@app.route("/offers.html")
def offers_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/offers.html")

@app.route("/ops-arrivals-departures.html")
def ops_arrivals_departures_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/ops-arrivals-departures.html")

@app.route("/ops-dashboard.html")
def ops_dashboard_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/ops-dashboard.html")

@app.route("/ops-housekeeping.html")
def ops_housekeeping_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/ops-housekeeping.html")

@app.route("/ops-incidents.html")
def ops_incidents_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/ops-incidents.html")

@app.route("/ops-inventory.html")
def ops_inventory_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/ops-inventory.html")

@app.route("/ops-maintenance.html")
def ops_maintenance_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/ops-maintenance.html")

@app.route("/ops-reports.html")
def ops_reports_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/ops-reports.html")

@app.route("/ops-rooms-status.html")
def ops_rooms_status_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/ops-rooms-status.html")

@app.route("/ops-shift-log.html")
def ops_shift_log_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/ops-shift-log.html")

@app.route("/portal-dashboard.html")
def portal_dashboard_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/portal-dashboard.html")

@app.route("/portal-facturas.html")
def portal_facturas_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/portal-facturas.html")

@app.route("/portal-pagos.html")
def portal_pagos_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/portal-pagos.html")

@app.route("/portal-perfil.html")
def portal_perfil_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/portal-perfil.html")

@app.route("/portal-preferencias.html")
def portal_preferencias_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/portal-preferencias.html")

@app.route("/portal-reserva-detalle.html")
def portal_reserva_detalle_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/portal-reserva-detalle.html")

@app.route("/portal-reservas.html")
def portal_reservas_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/portal-reservas.html")

@app.route("/portal-soporte.html")
def portal_soporte_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/portal-soporte.html")

@app.route("/privacy.html")
def privacy_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/privacy.html")

@app.route("/register.html")
def register_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/register.html")

@app.route("/restaurant.html")
def restaurant_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/restaurant.html")

@app.route("/room-details.html")
def room_details_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/room-details.html")

@app.route("/rooms.html")
def rooms_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/rooms.html")

@app.route("/starter-page.html")
def starter_page_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/starter-page.html")

@app.route("/terms.html")
def terms_html():
    return render_template("Hotel/Hotel Villa Grace/LuxuryHotel-pro/terms.html")


if __name__ == "__main__":
     # Debug server for local development
    app.run(host="0.0.0.0", port=5000, debug=True)

import os
from flask import send_from_directory

# Ruta física donde están tus assets dentro de static/
ASSETS_ROOT = os.path.join(
    app.static_folder,
    'Hotel', 'Hotel Villa Grace', 'LuxuryHotel-pro', 'assets'
)




