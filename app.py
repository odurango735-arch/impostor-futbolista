from flask import Flask, render_template, request, redirect, url_for, flash
import random
import uuid

app = Flask(__name__)
app.secret_key = "cambiame_por_una_clave_segura"  # Cambia esto si lo publicas

# Datos en memoria (suficiente para uso local / pruebas)
# Estructuras:
# players_tokens: token -> {"nombre": "Jugador 1", "rol": "impostor" or "Messi", "visto": False}
players_tokens = {}
# lista ordenada de jugadores para mostrar en la página de administración
jugadores_ordenados = []

@app.route("/", methods=["GET", "POST"])
def index():
    """
    Página principal: elegir número de jugadores e impostores.
    """
    if request.method == "POST":
        try:
            num_jugadores = int(request.form.get("jugadores", 0))
            num_impostores = int(request.form.get("impostores", 0))
        except ValueError:
            flash("Introduce números válidos.")
            return redirect(url_for("index"))

        if num_jugadores < 4:
            flash("Debe haber al menos 4 jugadores.")
            return redirect(url_for("index"))
        if num_impostores < 1 or num_impostores >= num_jugadores:
            flash("Número inválido de impostores.")
            return redirect(url_for("index"))

        # Generar nombres (puedes modificarlos para pedir nombres manuales)
        jugadores = [f"Jugador {i+1}" for i in range(num_jugadores)]

        # Elegir impostores
        impostores = set(random.sample(jugadores, num_impostores))

        # Elegir futbolista para tripulantes (misma para todos)
        futbolistas = ["Messi", "Cristiano Ronaldo", "Mbappé", "Neymar", "Bellingham", "Haaland"]
        futbolista_elegido = random.choice(futbolistas)

        # Limpiar estructuras previas
        players_tokens.clear()
        jugadores_ordenados.clear()

        # Crear token por jugador y almacenar rol
        for j in jugadores:
            token = uuid.uuid4().hex  # token secreto único
            rol = "impostor" if j in impostores else futbolista_elegido
            players_tokens[token] = {"nombre": j, "rol": rol, "visto": False}
            jugadores_ordenados.append({"nombre": j, "token": token})

        # Generar lista de enlaces (completa) para mostrar en la página de "roles"
        return redirect(url_for("roles"))

    return render_template("index.html")


@app.route("/roles")
def roles():
    """
    Muestra la lista de jugadores con botones para copiar/abrir su enlace secreto.
    NO revela los roles aquí (solo nombres y estado 'visto' para administración).
    """
    base = request.host_url.rstrip("/")
    # crear una vista ordenada con estado visto/no visto
    vista = []
    for p in jugadores_ordenados:
        token = p["token"]
        info = players_tokens.get(token, {})
        link = f"{base}{url_for('ver_role', token=token)}"  # url completa
        vista.append({
            "nombre": p["nombre"],
            "link": link,
            "visto": info.get("visto", False)
        })
    return render_template("roles.html", jugadores=vista)


@app.route("/role/<token>", methods=["GET", "POST"])
def ver_role(token):
    """
    Página que ve cada jugador: muestra SU rol según el token.
    Marca 'visto' cuando el jugador entra.
    """
    info = players_tokens.get(token)
    if info is None:
        return "Enlace inválido o expirado.", 404

    # Si visitas con POST podría usarse para "confirmar" que ya vio el rol
    if request.method == "POST":
        # Marca como visto y redirige a una página de confirmación (o volver al inicio)
        info["visto"] = True
        flash("Rol marcado como visto.")
        return redirect(url_for("ver_role", token=token))

    # Cuando se carga la página por GET, marcamos como visto (opcional)
    # Si no quieres marcar automáticamente, comenta la siguiente línea.
    info["visto"] = True

    # Mostrar mensaje dependiendo del rol
    if info["rol"] == "impostor":
        mensaje = "🟥 ERES EL IMPOSTOR."
    else:
        mensaje = f"🟩 Eres {info['rol']}, un jugador de fútbol profesional. Entrena, juega limpio y descubre al impostor."

    return render_template("role.html", nombre=info["nombre"], mensaje=mensaje, visto=info["visto"])


if __name__ == "__main__":
    # Modo debug para desarrollo local; quítalo o pon False si lo subes a producción.
    app.run(debug=True)
