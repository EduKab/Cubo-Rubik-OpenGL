# Se importan las librerias a utilizar.

import pygame;
from pygame.locals import *;

from OpenGL.GL import *;
from OpenGL.GLU import *;

vertices = (( 1, -1, -1), ( 1,  1, -1), (-1,  1, -1), (-1, -1, -1),
            ( 1, -1,  1), ( 1,  1,  1), (-1, -1,  1), (-1,  1,  1))
bordes = ((0,1),(0,3),(0,4),(2,1),(2,3),(2,7),(6,3),(6,4),(6,7),(5,1),(5,4),(5,7))
superficies = ((0, 1, 2, 3), (3, 2, 7, 6), (6, 7, 5, 4), (4, 5, 1, 0), (1, 5, 7, 2), (4, 0, 3, 6))
colores = ((1, 0, 0), (0, 1, 0), (1, 0.5, 0), (1, 1, 0), (1, 1, 1), (0, 0, 1))

#Metodo main para inicializar componentes.
def main():

    pygame.init();
    display = (1024,600);
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL);
    glEnable(GL_DEPTH_TEST);

    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)

    rubik = Rubik(3, 1.5)
    rubik.mainloop()

#Esta clase es para el cubo completo de Rubik.
class Rubik():
    def __init__(self, p_numeCuadros, p_escala):
        self.numeCuadros = p_numeCuadros
        contador = range(self.numeCuadros)
        #Se crean los cubos del cubo de rubik esto para X, Y y Z.
        self.cubos = [Cubo((x, y, z), self.numeCuadros, p_escala) for x in contador for y in contador for z in contador]

    def mainloop(self):

        #Declaracion de botones
        rotaVistaFlechas  = {K_UP: (-2, 0), K_DOWN: (2, 0), K_LEFT: (0, -2), K_RIGHT: (0, 2)}
        rotaCuboTeclas = {K_1: (0, 0, 1), K_2: (0, 1, 1), K_3: (0, 2, 1), K_4: (1, 0, 1), K_5: (1, 1, 1),
                          K_6: (1, 2, 1), K_7: (2, 0, 1), K_8: (2, 1, 1), K_9: (2, 2, 1),
                          K_F1: (0, 0, -1), K_F2: (0, 1, -1), K_F3: (0, 2, -1), K_F4: (1, 0, -1), K_F5: (1, 1, -1),
                          K_F6: (1, 2, -1), K_F7: (2, 0, -1), K_F8: (2, 1, -1), K_F9: (2, 2, -1)}

        anguX, anguY, rotaCubo = 0, 0, (0, 0)
        animacion, animAngulo, animVelocidad = False, 0, 5
        accion = (0, 0, 0)

        while True:
            for event in pygame.event.get():
                #Si se cierra la ventana, se quita el pygame.
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                #Si se presiona una tecla, se busca que sea una flecha, si es una flecha se asigna a la rotacion
                # , si no es una flecha entonces es una tecla para el cubo, se pone en true la animacion y la accion
                # y se asigna el movimiento.
                if event.type == KEYDOWN:
                    if event.key in rotaVistaFlechas:
                        rotaCubo = rotaVistaFlechas[event.key]
                    if not animacion and event.key in rotaCuboTeclas:
                        animacion, accion = True, rotaCuboTeclas[event.key]
                #Cuando se deja de presionar una tecla, la rotacion del cubo de queda en 0.
                if event.type == KEYUP:
                    if event.key in rotaVistaFlechas:
                        rotaCubo = (0, 0)
            anguX += rotaCubo[0] * 2
            anguY += rotaCubo[1] * 2
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            glTranslatef(0, 0, -40)
            glRotatef(anguY, 0, 1, 0)
            glRotatef(anguX, 1, 0, 0)

            #Si la animacion esta en true, entonces se compara que el angulo de la animacion sea mayor o igual a 90,
            # si lo es, entonces cada cubo se actualiza con los nuevos valores correspondientes, luego se vuelve a poner
            # la animacion y el angulo de la animacion en False y 0.
            if animacion:
                if animAngulo >= 90:
                    for cubo in self.cubos:
                        cubo.m_actualizar(*accion)
                    animacion, animAngulo = False, 0

            for cubo in self.cubos:
                cubo.m_draw(colores, superficies, vertices, animacion, animAngulo, *accion)
            if animacion:
                animAngulo += animVelocidad

            pygame.display.flip()
            pygame.time.wait(10)

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

#Esta clase son para la generacion de los cuadros del cubo de Rubik.
class Cubo():
    def __init__(self, p_id, p_numeCuadros, p_escala):
        self.numeCuadros = p_numeCuadros
        self.escala = p_escala
        self.init_i = [*p_id]
        self.current_i = [*p_id]
        self.rotacion = [[1 if i==j else 0 for i in range(3)] for j in range(3)]

    def m_actualizar(self, p_x, p_y, p_direccion):

        #Si los valores de self no fueron afectados se sale del metodo.
        if not self.isAffected(p_x, p_y, p_direccion):
            return

        i, j = (p_x+1) % 3, (p_x+2) % 3
        for k in range(3):
            self.rotacion[k][i], self.rotacion[k][j] = -self.rotacion[k][j]*p_direccion, self.rotacion[k][i]*p_direccion

        self.current_i[i], self.current_i[j] = (
            self.current_i[j] if p_direccion < 0 else self.N - 1 - self.current_i[j],
            self.current_i[i] if p_direccion > 0 else self.N - 1 - self.current_i[i] )

    def m_draw(self, p_colores, p_superficies, p_vertices, p_animacion, p_animAngulo, p_X, p_Y, p_direccion):

        glPushMatrix()
        if p_animacion and self.isAffected(p_X, p_Y, p_direccion):
            glRotatef(p_animAngulo*p_direccion, *[1 if i == p_X else 0 for i in range(3)])
        glMultMatrixf(self.transformMat())

        glBegin(GL_QUADS)
        for i in range(len(p_superficies)):
            glColor3fv(p_colores[i])
            for j in p_superficies[i]:
                glVertex3fv(p_vertices[j])
        glEnd()

        glPopMatrix()

    def transformMat(self):
         escalaA = [[s * self.escala for s in a] for a in self.rotacion]
         escalaT = [(p - (self.numeCuadros - 1) / 2) * 2.1 * self.escala for p in self.current_i]
         return [*escalaA[0], 0, *escalaA[1], 0, *escalaA[2], 0, *escalaT, 1]

#Se ejecuta el metodo main.
if __name__ == '__main__':
    main();