import math
from config_mejorado import G, DT


def trayectoria(v0, angulo):
    """Integra el movimiento paso a paso con Euler.
    Devuelve (puntos, t_vuelo, alcance, h_max).
    Cada punto es (x, y, vel_x, vel_y, t)."""
    rad = math.radians(angulo)
    vel_x = v0 * math.cos(rad)
    vel_y = v0 * math.sin(rad)

    x = y = t = 0.0
    h_max = 0.0
    puntos = [(x, y, vel_x, vel_y, t)]

    while True:
        x_ant, y_ant, t_ant = x, y, t
        x += vel_x * DT
        y += vel_y * DT
        vel_y -= G * DT
        t += DT

        if y < 0:
            # Se interpola el ultimo tramo para caer justo en y = 0
            f = y_ant / (y_ant - y)
            x = x_ant + (x - x_ant) * f
            t = t_ant + DT * f
            y = 0.0
            puntos.append((x, y, vel_x, vel_y, t))
            break

        h_max = max(h_max, y)
        puntos.append((x, y, vel_x, vel_y, t))

    return puntos, t, x, h_max


def analitico(v0, angulo):
    """Soluciones exactas: (t_vuelo, alcance, h_max)."""
    rad = math.radians(angulo)
    t_vuelo = 2 * v0 * math.sin(rad) / G
    alcance = v0 ** 2 * math.sin(2 * rad) / G
    h_max = (v0 * math.sin(rad)) ** 2 / (2 * G)
    return t_vuelo, alcance, h_max
