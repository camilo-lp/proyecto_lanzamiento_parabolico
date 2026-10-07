import asyncio
import math
import pygame

from config_mejorado import *
from motor import trayectoria, analitico


class Deslizador:
    """Control deslizante para modificar un parmetro de la simulacin."""

    def __init__(self, x, y, ancho, minimo, maximo, valor, etiqueta, unidad):
        self.rect = pygame.Rect(x, y, ancho, 8)
        self.minimo = minimo
        self.maximo = maximo
        self.valor = valor
        self.etiqueta = etiqueta
        self.unidad = unidad
        self.arrastrando = False

    def _mover(self, mx):
        t = (mx - self.rect.x) / self.rect.width
        t = max(0.0, min(1.0, t))
        self.valor = self.minimo + t * (self.maximo - self.minimo)

    def evento(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.rect.inflate(20, 30).collidepoint(e.pos):
                self.arrastrando = True
                self._mover(e.pos[0])
        elif e.type == pygame.MOUSEMOTION and self.arrastrando:
            self._mover(e.pos[0])
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            self.arrastrando = False

    def dibujar(self, pantalla, fuente, fuente_valor):
        # Etiqueta
        texto = fuente.render(self.etiqueta.upper(), True, COLOR_TEXTO_SEC)
        pantalla.blit(texto, (self.rect.x, self.rect.y - 43))

        # Valor grande
        valor_txt = fuente_valor.render(
            f"{self.valor:.0f} {self.unidad}", True, COLOR_TEXTO
        )
        pantalla.blit(valor_txt, (self.rect.x, self.rect.y - 20))

        # Barra
        pygame.draw.rect(
            pantalla, COLOR_BORDE, self.rect, border_radius=4
        )

        t = (self.valor - self.minimo) / (self.maximo - self.minimo)
        parte = pygame.Rect(
            self.rect.x, self.rect.y, max(2, int(self.rect.width * t)), 8
        )
        pygame.draw.rect(pantalla, COLOR_ACENTO, parte, border_radius=4)

        # Punto de control
        cx = int(self.rect.x + t * self.rect.width)
        pygame.draw.circle(pantalla, COLOR_ACENTO, (cx, self.rect.centery), 11)
        pygame.draw.circle(pantalla, COLOR_PANEL, (cx, self.rect.centery), 5)


def texto_centrado(pantalla, texto, fuente, color, centro):
    superficie = fuente.render(texto, True, color)
    pantalla.blit(superficie, superficie.get_rect(center=centro))


def dibujar_tarjeta(pantalla, rect, titulo, valor, subtitulo, fuente_titulo,
                    fuente_valor, fuente_subtitulo):
    pygame.draw.rect(pantalla, COLOR_TARJETA, rect, border_radius=12)
    pygame.draw.rect(pantalla, COLOR_BORDE, rect, 1, border_radius=12)

    pantalla.blit(
        fuente_titulo.render(titulo.upper(), True, COLOR_TEXTO_SEC),
        (rect.x + 16, rect.y + 10)
    )
    pantalla.blit(
        fuente_valor.render(valor, True, COLOR_TEXTO),
        (rect.x + 16, rect.y + 30)
    )
    pantalla.blit(
        fuente_subtitulo.render(subtitulo, True, COLOR_TEXTO_SEC),
        (rect.x + 16, rect.bottom - 25)
    )


def calcular_escala(alcance, h_max, ancho_grafica, alto_grafica):
    """Calcula escalas independientes para X y Y."""
    esc_x = (ancho_grafica - 30) / max(alcance, 1e-6)
    esc_y = (alto_grafica - 25) / max(h_max, 1e-6)
    return esc_x, esc_y


def conversion(x, y, escala_x, escala_y, origen_x, origen_y):
    return (
        int(origen_x + x * escala_x),
        int(origen_y - y * escala_y)
    )


def paso_eje(valor_max):
    """Elige una separacion comoda para las marcas del eje."""
    if valor_max <= 10:
        return 1
    if valor_max <= 25:
        return 5
    if valor_max <= 60:
        return 10
    if valor_max <= 150:
        return 20
    if valor_max <= 300:
        return 50
    return 100


def dibujar_grafica(pantalla, sim, fuentes):
    fuente_eje, fuente_titulo, fuente_pequena = fuentes

    margen_x = MARGEN
    izquierda = margen_x + 42
    derecha = ANCHO - MARGEN - 15
    arriba = GRAFICA_TOP + 25
    abajo = SUELO_Y
    ancho = derecha - izquierda
    alto = abajo - arriba

    esc_x, esc_y = calcular_escala(
        sim["alcance"], sim["h_max"], ancho, alto
    )

    # rea de la grfica
    area = pygame.Rect(izquierda, arriba, ancho, alto)
    pygame.draw.rect(pantalla, COLOR_PANEL, area, border_radius=12)
    pygame.draw.rect(pantalla, COLOR_BORDE, area, 1, border_radius=12)

    # Lmites fsicos visibles.
    max_x = max(sim["alcance"], 1)
    max_y = max(sim["h_max"], 1)

    # Marcas X
    paso_x = paso_eje(max_x)
    x = 0
    while x <= max_x + paso_x * 0.01:
        px = izquierda + (x / max_x) * ancho
        pygame.draw.line(
            pantalla, COLOR_REJILLA,
            (int(px), arriba), (int(px), abajo), 1
        )
        etiqueta = fuente_eje.render(f"{x:g}", True, COLOR_TEXTO_SEC)
        pantalla.blit(
            etiqueta,
            etiqueta.get_rect(center=(int(px), abajo + 16))
        )
        x += paso_x

    # Marcas Y
    paso_y = paso_eje(max_y)
    y = 0
    while y <= max_y + paso_y * 0.01:
        py = abajo - (y / max_y) * alto
        pygame.draw.line(
            pantalla, COLOR_REJILLA,
            (izquierda, int(py)), (derecha, int(py)), 1
        )
        if y > 0:
            etiqueta = fuente_eje.render(f"{y:g}", True, COLOR_TEXTO_SEC)
            pantalla.blit(
                etiqueta,
                etiqueta.get_rect(
                    midright=(izquierda - 8, int(py))
                )
            )
        y += paso_y

    # Ejes
    pygame.draw.line(
        pantalla, COLOR_EJE,
        (izquierda, abajo), (derecha, abajo), 2
    )
    pygame.draw.line(
        pantalla, COLOR_EJE,
        (izquierda, abajo), (izquierda, arriba), 2
    )

    # Ttulos de ejes
    texto_centrado(
        pantalla, "distancia horizontal (m)", fuente_pequena,
        COLOR_TEXTO_SEC, ((izquierda + derecha) // 2, abajo + 38)
    )
    texto_centrado(
        pantalla, "altura (m)", fuente_pequena,
        COLOR_TEXTO_SEC, (izquierda - 48, arriba - 10)
    )

    # Trayectoria completa de referencia, muy suave.
    puntos_completos = []
    for p in sim["puntos"]:
        px = izquierda + (p[0] / max_x) * ancho
        py = abajo - (p[1] / max_y) * alto
        puntos_completos.append((int(px), int(py)))

    if len(puntos_completos) > 1:
        pygame.draw.lines(
            pantalla, COLOR_TRAYECTORIA_SUAVE,
            False, puntos_completos, 1
        )

    # Trayectoria recorrida por el proyectil.
    i = sim["indice"]
    puntos_recorridos = puntos_completos[: i + 1]

    if len(puntos_recorridos) > 1:
        pygame.draw.lines(
            pantalla, COLOR_TRAYECTORIA,
            False, puntos_recorridos, 4
        )

    # Punto de salida e impacto.
    if puntos_completos:
        pygame.draw.circle(
            pantalla, COLOR_ACENTO, puntos_completos[0], 5
        )
        pygame.draw.circle(
            pantalla, COLOR_PROYECTIL,
            puntos_completos[-1], 6
        )

    # Proyectil actual.
    if puntos_recorridos:
        proyectil = puntos_recorridos[-1]
        pygame.draw.circle(
            pantalla, (255, 255, 255), proyectil, 11
        )
        pygame.draw.circle(
            pantalla, COLOR_PROYECTIL, proyectil, 8
        )

    # Ttulo de la grfica.
    pantalla.blit(
        fuente_titulo.render("TRAYECTORIA DEL PROYECTIL", True, COLOR_TEXTO),
        (izquierda + 16, arriba + 10)
    )

    # Leyenda.
    leyenda_y = arriba + 12
    lx = derecha - 220
    pygame.draw.line(
        pantalla, COLOR_TRAYECTORIA, (lx, leyenda_y + 9),
        (lx + 25, leyenda_y + 9), 3
    )
    pantalla.blit(
        fuente_pequena.render("trayectoria", True, COLOR_TEXTO_SEC),
        (lx + 32, leyenda_y)
    )


async def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Simulador de lanzamiento parabolico")
    reloj = pygame.time.Clock()

    # Fuentes
    fuente = pygame.font.Font(None, 22)
    fuente_pequena = pygame.font.Font(None, 19)
    fuente_valor = pygame.font.Font(None, 27)
    fuente_titulo = pygame.font.Font(None, 27)
    fuente_grande = pygame.font.Font(None, 36)
    fuente_boton = pygame.font.Font(None, 30)

    # Controles
    s_vel = Deslizador(
        55, 116, 315, 1, 100,
        V0_DEFECTO, "Velocidad inicial", "m/s"
    )
    s_ang = Deslizador(
        425, 116, 315, 1, 89,
        ANGULO_DEFECTO, "ngulo de lanzamiento", ""
    )
    boton = pygame.Rect(835, 91, 205, 58)

    sim = {}

    def lanzar():
        v0 = s_vel.valor
        ang = s_ang.valor

        puntos, t_v, alc, h = trayectoria(v0, ang)

        sim["puntos"] = puntos
        sim["indice"] = 0
        sim["t_vuelo"] = t_v
        sim["alcance"] = alc
        sim["h_max"] = h
        sim["exacto"] = analitico(v0, ang)
        sim["v0"] = v0
        sim["angulo"] = ang

    lanzar()

    ejecutando = True
    while ejecutando:
        mouse = pygame.mouse.get_pos()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                ejecutando = False

            s_vel.evento(e)
            s_ang.evento(e)

            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if boton.collidepoint(e.pos):
                    lanzar()

            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_SPACE, pygame.K_RETURN):
                    lanzar()
                elif e.key == pygame.K_r:
                    s_vel.valor = V0_DEFECTO
                    s_ang.valor = ANGULO_DEFECTO
                    lanzar()

        # Animacin.
        if sim["indice"] < len(sim["puntos"]) - 1:
            sim["indice"] += 1

        # Fondo.
        pantalla.fill(COLOR_FONDO)

        # Encabezado.
        pygame.draw.rect(
            pantalla, COLOR_PANEL,
            (0, 0, ANCHO, PANEL_ALTO)
        )

        # Separador.
        pygame.draw.line(
            pantalla, COLOR_BORDE,
            (0, PANEL_ALTO), (ANCHO, PANEL_ALTO), 1
        )

        # Ttulo.
        pantalla.blit(
            fuente_grande.render(
                "Simulador de lanzamiento parabolico",
                True, COLOR_TEXTO
            ),
            (MARGEN, 18)
        )

        pantalla.blit(
            fuente_pequena.render(
                "ajusta los parmetros y presiona Lanza para iniciar la simulacin",
                True, COLOR_TEXTO_SEC
            ),
            (MARGEN, 52)
        )

        # Controles.
        s_vel.dibujar(pantalla, fuente, fuente_valor)
        s_ang.dibujar(pantalla, fuente, fuente_valor)

        # Botn con hover.
        color_boton = (
            COLOR_BOTON_HOVER
            if boton.collidepoint(mouse)
            else COLOR_BOTON
        )

        pygame.draw.rect(
            pantalla, color_boton, boton, border_radius=12
        )
        pygame.draw.rect(
            pantalla, (100, 220, 150), boton, 1, border_radius=12
        )
        texto_centrado(
            pantalla, "LANZAR", fuente_boton,
            COLOR_TEXTO, boton.center
        )

        # Grfica.
        dibujar_grafica(
            pantalla, sim,
            (fuente_pequena, fuente_titulo, fuente_pequena)
        )

        # Resultados inferiores.
        t_e, a_e, h_e = sim["exacto"]
        err = (
            abs(sim["alcance"] - a_e) / a_e * 100
            if a_e else 0
        )

        tarjeta_y = 595
        tarjeta_h = 80
        separacion = 12
        tarjeta_w = (ANCHO - 2 * MARGEN - 3 * separacion) // 4

        resultados = [
            (
                "TIEMPO DE VUELO",
                f"{sim['t_vuelo']:.2f} s",
                f"exacto: {t_e:.2f} s"
            ),
            (
                "ALCANCE",
                f"{sim['alcance']:.2f} m",
                f"exacto: {a_e:.2f} m"
            ),
            (
                "ALTURA MXIMA",
                f"{sim['h_max']:.2f} m",
                f"exacto: {h_e:.2f} m"
            ),
            (
                "ERROR NUMRICO",
                f"{err:.3f} %",
                "comparacion con solucin analtica"
            ),
        ]

        for n, datos in enumerate(resultados):
            rect = pygame.Rect(
                MARGEN + n * (tarjeta_w + separacion),
                tarjeta_y,
                tarjeta_w,
                tarjeta_h
            )
            dibujar_tarjeta(
                pantalla, rect, *datos,
                fuente_pequena, fuente_valor, fuente_pequena
            )

        # Indicador de ayuda.
        ayuda = "ESPACIO / ENTER: lanzar    R: restaurar valores"
        texto_centrado(
            pantalla, ayuda, fuente_pequena,
            COLOR_TEXTO_SEC, (ANCHO // 2, ALTO - 10)
        )

        pygame.display.flip()
        reloj.tick(FPS)
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
